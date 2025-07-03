# -*- coding: utf-8 -*-
"""
单词编辑对话框模块
================

提供单词编辑界面，支持：
- 添加新单词
- 编辑现有单词
- 输入英文单词、中文翻译和词性

用于单词数据的创建和修改操作。
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, 
                             QFormLayout, QLabel, QApplication)
from src.core.word_manager import WordManager

class WordEditorDialog(QDialog):
    """
    单词编辑对话框
    
    提供用户界面来添加新单词或编辑现有单词，
    包含英文单词、中文翻译和词性的输入框。
    """
    
    def __init__(self, parent=None, word_data=None):
        """
        初始化单词编辑对话框
        
        Args:
            parent: 父窗口对象
            word_data (dict, optional): 单词数据字典，用于编辑模式
                                      如果为None则为添加模式
        """
        super().__init__(parent)
        
        # 根据是否有数据设置窗口标题
        if word_data:
            self.setWindowTitle("编辑单词")
        else:
            self.setWindowTitle("添加新单词")

        self.word_data = word_data

        # 创建主布局
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 创建输入框
        self.word_input = QLineEdit(self)          # 英文单词输入框
        self.translation_input = QLineEdit(self)   # 中文翻译输入框
        self.pos_input = QLineEdit(self)           # 词性输入框

        # 添加表单行
        form_layout.addRow(QLabel("单词:"), self.word_input)
        form_layout.addRow(QLabel("翻译:"), self.translation_input)
        form_layout.addRow(QLabel("词性:"), self.pos_input)
        
        layout.addLayout(form_layout)

        # 创建对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 如果是编辑模式，使用传入的数据填充输入框
        if self.word_data:
            self._populate_fields()
        
        # 居中显示对话框
        self.center_dialog()

    def center_dialog(self):
        """
        将对话框居中显示在屏幕上
        
        计算屏幕中心位置，将对话框移动到屏幕中央。
        """
        screen = QApplication.primaryScreen().geometry()
        dialog_rect = self.frameGeometry()
        center_point = screen.center()
        dialog_rect.moveCenter(center_point)
        self.move(dialog_rect.topLeft())

    def _populate_fields(self):
        """
        使用现有数据填充输入框
        
        在编辑模式下，将传入的单词数据填充到对应的输入框中。
        """
        self.word_input.setText(self.word_data.get(WordManager.KEY_WORD, ''))
        self.translation_input.setText(self.word_data.get(WordManager.KEY_TRANSLATION, ''))
        self.pos_input.setText(self.word_data.get(WordManager.KEY_POS, ''))
        
    def get_word_data(self):
        """
        获取用户输入的单词数据
        
        收集用户在对话框中输入的所有信息，并返回标准格式的字典。
        会自动去除文本的前后空白字符。
        
        Returns:
            dict: 包含单词信息的字典，键名由 WordManager 中的常量定义
                  包含：英文单词、中文翻译、词性
        """
        return {
            WordManager.KEY_WORD: self.word_input.text().strip(),
            WordManager.KEY_TRANSLATION: self.translation_input.text().strip(),
            WordManager.KEY_POS: self.pos_input.text().strip()
        } 