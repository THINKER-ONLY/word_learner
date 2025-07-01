from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QFormLayout, QLabel
from src.core.word_manager import WordManager

class WordEditorDialog(QDialog):
    def __init__(self, parent=None, word_data=None):
        """
        初始化单词编辑器对话框。
        :param parent: 父窗口。
        :param word_data: (可选) 一个包含现有单词数据的字典，用于编辑模式。
                          例如: {'word': 'apple', 'translation': '苹果', 'partOfSpeech': 'n.'}
        """
        super().__init__(parent)
        
        if word_data:
            self.setWindowTitle("Edit Word")
        else:
            self.setWindowTitle("Add New Word")

        self.word_data = word_data or {} # Store original data if in edit mode

        # --- Layouts and Widgets ---
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.word_input = QLineEdit(self)
        self.translation_input = QLineEdit(self)
        self.pos_input = QLineEdit(self) # Part of Speech

        form_layout.addRow(QLabel("Word:"), self.word_input)
        form_layout.addRow(QLabel("Translation:"), self.translation_input)
        form_layout.addRow(QLabel("Part of Speech:"), self.pos_input)
        
        layout.addLayout(form_layout)

        # --- Dialog Buttons (OK/Cancel) ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # If in edit mode, populate the fields
        if self.word_data:
            self._populate_fields()

    def _populate_fields(self):
        """If editing, fill the input fields with existing data."""
        self.word_input.setText(self.word_data.get(WordManager.KEY_WORD, ''))
        self.translation_input.setText(self.word_data.get(WordManager.KEY_TRANSLATION, ''))
        self.pos_input.setText(self.word_data.get(WordManager.KEY_POS, ''))
        
    def get_word_data(self):
        """
        获取用户在对话框中输入的数据。
        :return: 一个包含单词信息的字典。
        """
        return {
            WordManager.KEY_WORD: self.word_input.text().strip(),
            WordManager.KEY_TRANSLATION: self.translation_input.text().strip(),
            WordManager.KEY_POS: self.pos_input.text().strip()
        } 