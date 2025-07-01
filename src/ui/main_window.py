from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt, QTimer

# Import the backend managers
from src.core.word_manager import WordManager
from src.core.settings_manager import SettingsManager
from src.ui.word_editor_dialog import WordEditorDialog
from src.ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Learner")
        self.setGeometry(100, 100, 400, 200) # x, y, width, height

        # --- Backend Initialization ---
        # NOTE: We are assuming default paths for the data files.
        self.settings_manager = SettingsManager("config.json")
        self.word_manager = WordManager("assets/words.json")
        self.current_word_data = None # To hold the currently displayed word
        # ---

        # --- Menu Bar ---
        self._create_menu_bar()
        # ---

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Word display label
        self.word_label = QLabel("...")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("font-size: 36px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(self.word_label)

        # Translation display label
        self.translation_label = QLabel("...")
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.setStyleSheet("font-size: 24px; color: grey;")
        layout.addWidget(self.translation_label)

        # Spacer to push the button to the bottom
        layout.addStretch()

        # "Next Word" button
        self.next_button = QPushButton("Next Word")
        self.next_button.setStyleSheet("font-size: 16px; padding: 10px;")
        # --- Connect the button's clicked signal to the method ---
        self.next_button.clicked.connect(self.show_next_word_and_reset_timer)
        layout.addWidget(self.next_button)

        # Setup and start the timer for automatic word display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_word)

        # Show the first word and start the timer
        self.show_next_word_and_reset_timer()

    def show_next_word_and_reset_timer(self):
        """Shows a new word and resets the timer to the configured interval."""
        self.show_next_word()
        # Read interval from settings and start the timer
        interval_seconds = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_INTERVAL)
        if interval_seconds > 0:
            self.timer.start(interval_seconds * 1000)  # QTimer wants milliseconds

    def show_next_word(self):
        """Fetch and display the next word from the manager based on settings."""
        # Get settings
        display_mode = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_MODE)
        show_chinese = self.settings_manager.get_settings(self.settings_manager.KEY_SHOW_CHINESE)

        # Get the next word based on the mode
        if display_mode == 'random':
            self.current_word_data = self.word_manager.get_random_word()
        else:  # 'sequential' or any other value will default to sequential
            self.current_word_data = self.word_manager.get_next_word()

        if self.current_word_data:
            self._set_display(self.current_word_data.get(self.word_manager.KEY_WORD, "Error"), self.current_word_data.get(self.word_manager.KEY_TRANSLATION, "Key mismatch"))
        else:
            self._set_display("No words found", "Please add words.")
            self.timer.stop()  # Stop the timer if there are no words

        # Set translation visibility based on settings
        self.translation_label.setVisible(show_chinese)

    def _set_display(self, word, translation):
        """Helper to set the text on the labels."""
        self.word_label.setText(word)
        self.translation_label.setText(translation)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        # File Menu
        file_menu = menu_bar.addMenu("&File")

        # Add/Edit/Delete actions will be here
        add_action = file_menu.addAction("&Add Word...")
        add_action.triggered.connect(self.open_add_word_dialog)

        edit_action = file_menu.addAction("&Edit Word...")
        edit_action.triggered.connect(self.open_edit_word_dialog)

        delete_action = file_menu.addAction("&Delete Word...")
        delete_action.triggered.connect(self.open_delete_word_dialog)
        file_menu.addSeparator()
        
        settings_action = file_menu.addAction("&Settings...")
        settings_action.triggered.connect(self.open_settings_dialog)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about_dialog)

    def open_add_word_dialog(self):
        """Opens the dialog to add a new word."""
        dialog = WordEditorDialog(self)
        if dialog.exec():  # This blocks until the dialog is closed (OK or Cancel)
            new_word_data = dialog.get_word_data()
            if not new_word_data[self.word_manager.KEY_WORD] or not new_word_data[self.word_manager.KEY_TRANSLATION]:
                QMessageBox.warning(self, "Input Error", "Word and Translation fields cannot be empty.")
                return

            success = self.word_manager.add_word(
                word=new_word_data[self.word_manager.KEY_WORD],
                translation=new_word_data[self.word_manager.KEY_TRANSLATION],
                part_of_speech=new_word_data[self.word_manager.KEY_POS]
            )

            if success:
                self.word_manager.save_changes()
                QMessageBox.information(self, "Success", f"Word '{new_word_data[self.word_manager.KEY_WORD]}' added successfully.")
            else:
                QMessageBox.warning(self, "Error", f"Could not add the word '{new_word_data[self.word_manager.KEY_WORD]}'. It might already exist.")

    def open_edit_word_dialog(self):
        """Opens the dialog to edit the currently displayed word."""
        if not self.current_word_data:
            QMessageBox.information(self, "No Word", "There is no word currently displayed to edit.")
            return

        dialog = WordEditorDialog(self, word_data=self.current_word_data)
        if dialog.exec():
            updated_data = dialog.get_word_data()
            if not updated_data[self.word_manager.KEY_WORD] or not updated_data[self.word_manager.KEY_TRANSLATION]:
                QMessageBox.warning(self, "Input Error", "Word and Translation fields cannot be empty.")
                return
            
            original_word = self.current_word_data[self.word_manager.KEY_WORD]
            success = self.word_manager.edit_word(original_word, updated_data)

            if success:
                self.word_manager.save_changes()
                QMessageBox.information(self, "Success", f"Word '{original_word}' updated successfully.")
                # Refresh the display to show potential changes
                self.show_next_word_and_reset_timer()
            else:
                QMessageBox.warning(self, "Error", "Could not update the word. The new name might conflict with an existing word.")

    def open_delete_word_dialog(self):
        """Opens a dialog to find and delete a word."""
        word_to_delete, ok = QInputDialog.getText(self, "Delete Word", "Enter the English word to delete:")

        if ok and word_to_delete:
            word_to_delete = word_to_delete.strip()
            # First, check if the word exists
            if not self.word_manager.find_word(word_to_delete, key=self.word_manager.KEY_WORD):
                QMessageBox.information(self, "Not Found", f"The word '{word_to_delete}' was not found in your library.")
                return

            # Ask for confirmation before deleting
            reply = QMessageBox.question(self, 'Confirm Deletion',
                                           f"Are you sure you want to permanently delete '{word_to_delete}'?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self.word_manager.delete_word(word_to_delete)
                if success:
                    self.word_manager.save_changes()
                    QMessageBox.information(self, "Success", f"Word '{word_to_delete}' has been deleted.")
                    # If the deleted word was the one being displayed, refresh the view
                    if self.current_word_data and self.current_word_data.get(self.word_manager.KEY_WORD) == word_to_delete:
                        self.show_next_word()
                else:
                    # This case is unlikely if find_word passed, but good for robustness
                    QMessageBox.warning(self, "Error", f"An unexpected error occurred while trying to delete '{word_to_delete}'.")

    def open_settings_dialog(self):
        """Opens the settings dialog."""
        dialog = SettingsDialog(self.settings_manager, self)
        if dialog.exec():
            # Settings are saved within the dialog's accept() method.
            # We just need to apply them to the current session.
            QMessageBox.information(self, "Settings Saved", "Your new settings have been saved.")
            # Restart the timer to apply the new interval immediately.
            # Also re-triggers a word display, which will apply mode and visibility settings.
            self.show_next_word_and_reset_timer() 

    def show_about_dialog(self):
        """Shows the About dialog with application and author information."""
        # --- PLEASE FILL IN YOUR DETAILS HERE ---
        name = "李政阳"
        student_id = "9116124039"
        class_info = "数据科学与大数据技术242班"
        github_user = "THINKER-ONLY"
        project_url = "https://github.com/THINKER-ONLY/word_learner" # Example URL
        # ---

        about_text = f"""
        <h2>Word Learner v1.0</h2>
        <p>A simple application to help you memorize English words.</p>
        <p><b>Author Details:</b></p>
        <ul>
            <li><b>Name:</b> {name}</li>
            <li><b>Student ID:</b> {student_id}</li>
            <li><b>Class:</b> {class_info}</li>
        </ul>
        <p><b>Find this project on GitHub:</b></p>
        <p><a href="{project_url}">{project_url}</a></p>
        """
        QMessageBox.about(self, "About Word Learner", about_text) 