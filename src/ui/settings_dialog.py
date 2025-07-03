# -*- coding: utf-8 -*-
"""
设置对话框模块
=============

提供用户设置界面，允许用户配置：
- 单词显示间隔时间
- 单词显示模式（随机/顺序）
- 中文翻译显示控制

设置会实时保存到配置文件中。
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, 
                             QFormLayout, QLabel, QSpinBox, QComboBox, 
                             QCheckBox, QApplication)

class SettingsDialog(QDialog):
    """
    设置对话框
    
    提供用户界面来配置应用程序的各种设置，
    包括显示间隔、模式选择和中文显示控制。
    """
    
    def __init__(self, settings_manager, parent=None):
        """
        初始化设置对话框
        
        Args:
            settings_manager (SettingsManager): 设置管理器实例
            parent: 父窗口对象
        """
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.settings_manager = settings_manager

        # 创建主布局
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 显示间隔设置（秒）
        self.interval_input = QSpinBox(self)
        self.interval_input.setMinimum(1)       # 最小1秒
        self.interval_input.setMaximum(60)      # 最大60秒
        self.interval_input.setSuffix(" 秒")

        # 显示模式设置（随机/顺序）
        self.mode_input = QComboBox(self)
        self.mode_input.addItems(["random", "sequential"])

        # 中文翻译显示控制
        self.show_chinese_input = QCheckBox("默认显示翻译")
        
        # 添加表单行
        form_layout.addRow(QLabel("单词显示间隔:"), self.interval_input)
        form_layout.addRow(QLabel("单词显示模式:"), self.mode_input)
        form_layout.addRow(self.show_chinese_input)
        
        layout.addLayout(form_layout)

        # 创建对话框按钮（确定/取消）
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)  # 确定按钮，调用重写的accept方法
        button_box.rejected.connect(self.reject)  # 取消按钮
        layout.addWidget(button_box)

        # 加载当前设置并居中显示
        self._load_current_settings()
        self.center_dialog()

    def _load_current_settings(self):
        """
        加载当前设置到UI控件
        
        从设置管理器中读取当前的配置值，
        并将其填充到对应的UI控件中。
        """
        # 加载显示间隔设置
        interval = self.settings_manager.get_settings("display_interval")
        self.interval_input.setValue(interval)

        # 加载显示模式设置
        mode = self.settings_manager.get_settings("display_mode")
        self.mode_input.setCurrentText(mode)

        # 加载中文显示设置
        show_chinese = self.settings_manager.get_settings("show_chinese")
        self.show_chinese_input.setChecked(show_chinese)
        
    def _save_settings(self):
        """
        保存UI控件中的设置值
        
        将UI控件中的当前值保存到设置管理器中，
        设置会立即写入配置文件。
        """
        self.settings_manager.set_settings("display_interval", self.interval_input.value())
        self.settings_manager.set_settings("display_mode", self.mode_input.currentText())
        self.settings_manager.set_settings("show_chinese", self.show_chinese_input.isChecked())
    
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

    def accept(self):
        """
        重写接受方法
        
        在用户点击确定按钮时，先保存设置，
        然后调用父类的accept方法关闭对话框。
        """
        self._save_settings()
        super().accept() 