from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Learner")
        self.setGeometry(100, 100, 400, 200) # x, y, width, height

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Word display label
        self.word_label = QLabel("Word")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("font-size: 36px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(self.word_label)

        # Translation display label
        self.translation_label = QLabel("Translation")
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.setStyleSheet("font-size: 24px; color: grey;")
        layout.addWidget(self.translation_label)

        # Spacer to push the button to the bottom
        layout.addStretch()

        # "Next Word" button
        self.next_button = QPushButton("Next Word")
        self.next_button.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(self.next_button)

        # Set placeholder content
        self._set_display("Hello", "你好")

    def _set_display(self, word, translation):
        """Helper to set the text on the labels."""
        self.word_label.setText(word)
        self.translation_label.setText(translation) 