from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt

# Import the backend managers
from src.core.word_manager import WordManager
from src.core.settings_manager import SettingsManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Learner")
        self.setGeometry(100, 100, 400, 200) # x, y, width, height

        # --- Backend Initialization ---
        # NOTE: We are assuming default paths for the data files.
        self.settings_manager = SettingsManager("config.json")
        self.word_manager = WordManager("assets/words.json")
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
        self.next_button.clicked.connect(self.show_next_word)
        layout.addWidget(self.next_button)

        # Show the first word immediately on startup
        self.show_next_word()

    def show_next_word(self):
        """Fetch and display the next word from the manager."""
        # TODO: Implement logic to switch between random and sequential mode based on settings
        word_data = self.word_manager.get_random_word()

        if word_data:
            # If a word is found, display it.
            # IMPORTANT: The keys 'word' and 'translation' here MUST match the keys in words.json
            self._set_display(word_data.get("word", "Error"), word_data.get("translation", "Key mismatch"))
        else:
            # If no word is found (e.g., file is empty or couldn't be read)
            self._set_display("No words found", "Please check your words.json file.")

    def _set_display(self, word, translation):
        """Helper to set the text on the labels."""
        self.word_label.setText(word)
        self.translation_label.setText(translation) 