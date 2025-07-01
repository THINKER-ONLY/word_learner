from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QFormLayout, QLabel
from src.core.word_manager import WordManager

class WordEditorDialog(QDialog):
    def __init__(self, parent=None, word_data=None):
        """
        初始化单词编辑器对话框。
        :param parent: 父窗口。
        :param word_data: (可选) 用于初始化编辑器内容的单词数据字典，用于编辑模式。
        """
        super().__init__(parent)
        
        if word_data:
            self.setWindowTitle("编辑单词")
        else:
            self.setWindowTitle("添加新单词")

        self.word_data = word_data

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.word_input = QLineEdit(self)
        self.translation_input = QLineEdit(self)
        self.pos_input = QLineEdit(self)

        form_layout.addRow(QLabel("单词:"), self.word_input)
        form_layout.addRow(QLabel("翻译:"), self.translation_input)
        form_layout.addRow(QLabel("词性:"), self.pos_input)
        
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 如果是编辑模式，则使用传入的数据填充输入框
        if self.word_data:
            self._populate_fields()

    def _populate_fields(self):
        """使用现有数据填充输入框。"""
        self.word_input.setText(self.word_data.get(WordManager.KEY_WORD, ''))
        self.translation_input.setText(self.word_data.get(WordManager.KEY_TRANSLATION, ''))
        self.pos_input.setText(self.word_data.get(WordManager.KEY_POS, ''))
        
    def get_word_data(self):
        """
        获取用户在对话框中输入的数据。
        :return: 一个包含单词信息的字典，键由 WordManager 中的常量定义。
        """
        return {
            WordManager.KEY_WORD: self.word_input.text().strip(),
            WordManager.KEY_TRANSLATION: self.translation_input.text().strip(),
            WordManager.KEY_POS: self.pos_input.text().strip()
        } 