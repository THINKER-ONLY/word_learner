#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Learner - 桌面单词学习工具
=================================

这是一个基于 PyQt6 的桌面单词学习应用程序。
帮助用户学习英语单词，支持随机/顺序播放、自定义时间间隔等功能。

作者: Word Learner Team
版本: 0.1.0
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    """
    应用程序主函数
    初始化 Qt 应用程序并显示主窗口
    """
    # 创建 Qt 应用程序实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 启动应用程序主循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
