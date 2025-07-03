# -*- coding: utf-8 -*-
"""
主窗口模块
=========

应用程序的主窗口界面，包含：
- 单词显示区域
- 控制按钮
- 菜单栏
- 定时器控制
- 历史记录管理

这是用户与应用程序交互的主要界面。
"""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, 
                             QPushButton, QMessageBox, QInputDialog, QLineEdit, 
                             QHBoxLayout, QCheckBox, QDialog, QTextEdit, 
                             QDialogButtonBox, QApplication)
from PyQt6.QtCore import Qt, QTimer

from src.core.word_manager import WordManager
from src.core.settings_manager import SettingsManager
from src.ui.word_editor_dialog import WordEditorDialog
from src.ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """
    主窗口类
    
    应用程序的主窗口，负责显示单词学习界面，
    包含单词显示、控制按钮、菜单栏等所有UI组件。
    """
    def __init__(self):
        """
        初始化主窗口
        
        设置窗口基本属性、创建所有UI组件、初始化管理器对象、
        设置信号连接和定时器等。
        """
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("背单词小工具")
        self.resize(675, 375)
        self.setMinimumSize(600, 375)
        self.center_window()

        # 初始化管理器对象
        self.settings_manager = SettingsManager("config.json")
        self.word_manager = WordManager("assets/words.json")
        self.current_word_data = None  # 当前显示的单词数据

        # 创建搜索组件（作为实例变量，以便在多个方法中访问）
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("查找单词...")
        self.search_input.setMaximumWidth(375)  # 限制搜索框最大宽度
        self.search_button = QPushButton("🔍")

        # 创建菜单栏
        self._create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        word_display_container = QWidget()
        word_layout = QVBoxLayout(word_display_container)
        word_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.word_label = QLabel("...")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setStyleSheet("font-weight: bold;") 
        word_layout.addWidget(self.word_label)

        self.pos_label = QLabel("...")
        self.pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pos_label.setStyleSheet("color: grey; font-style: italic;")
        word_layout.addWidget(self.pos_label)

        self.translation_label = QLabel("...")
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.setStyleSheet("color: grey;") 
        word_layout.addWidget(self.translation_label)

        main_layout.addWidget(word_display_container, 1)

        # 添加显示中文的快速切换选项和倒计时显示
        control_layout = QHBoxLayout()
        
        self.show_chinese_checkbox = QCheckBox("显示中文")
        self.show_chinese_checkbox.setChecked(self.settings_manager.get_settings(self.settings_manager.KEY_SHOW_CHINESE))
        self.show_chinese_checkbox.toggled.connect(self.toggle_chinese_display)
        control_layout.addWidget(self.show_chinese_checkbox)
        
        control_layout.addStretch()  # 添加弹性空间
        
        # 添加倒计时显示
        self.countdown_label = QLabel("⏱️ --")
        self.countdown_label.setStyleSheet("color: #666666; font-weight: bold; font-size: 18px;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        control_layout.addWidget(self.countdown_label)
        
        main_layout.addLayout(control_layout)

        # 添加按钮布局
        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("上一个")
        self.prev_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.prev_button.clicked.connect(self.show_previous_word)
        self.prev_button.setEnabled(False)  # 初始状态禁用
        button_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("下一个")
        self.next_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.next_button.clicked.connect(self.show_next_word_smart)
        button_layout.addWidget(self.next_button)
        
        main_layout.addLayout(button_layout)

        # 信号连接
        self.search_button.clicked.connect(self._perform_search)
        self.search_input.returnPressed.connect(self._perform_search)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_word)
        
        # 添加倒计时功能
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.remaining_time = 0  # 剩余时间（秒）

        self.show_next_word_and_reset_timer()
        self.update_button_states()  # 初始化按钮状态
        self.resizeEvent(None)

    def center_window(self):
        """
        将窗口居中显示在屏幕上
        
        获取屏幕的几何信息，计算窗口应该放置的位置，
        使窗口在屏幕中央显示。
        """
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())

    def center_dialog(self, dialog):
        """
        将对话框居中显示在屏幕上
        
        Args:
            dialog: 要居中显示的对话框对象
        """
        screen = QApplication.primaryScreen().geometry()
        dialog_rect = dialog.frameGeometry()
        center_point = screen.center()
        dialog_rect.moveCenter(center_point)
        dialog.move(dialog_rect.topLeft()) 

    def resizeEvent(self, event):
        """
        处理窗口大小调整事件
        
        当窗口大小改变时，自动调整字体大小以保持良好的显示效果。
        字体大小根据窗口高度按比例缩放。
        
        Args:
            event: 窗口大小调整事件对象
        """
        # 根据窗口高度计算字体大小
        base_height = self.height()
        word_font_size = max(18, int(base_height / 7))        # 单词字体
        pos_font_size = max(12, int(base_height / 14))        # 词性字体
        translation_font_size = max(14, int(base_height / 10)) # 翻译字体

        # 设置单词字体大小
        font_word = self.word_label.font()
        font_word.setPointSize(word_font_size)
        self.word_label.setFont(font_word)

        # 设置词性字体大小
        font_pos = self.pos_label.font()
        font_pos.setPointSize(pos_font_size)
        self.pos_label.setFont(font_pos)

        # 设置翻译字体大小
        font_translation = self.translation_label.font()
        font_translation.setPointSize(translation_font_size)
        self.translation_label.setFont(font_translation)
        
        # 调用父类的 resizeEvent 方法
        if event:
            super().resizeEvent(event)

    def show_next_word_and_reset_timer(self):
        """
        显示新单词并重置定时器
        
        这是一个组合方法，它会：
        1. 显示下一个单词
        2. 更新按钮状态
        3. 根据设置重置自动切换定时器
        4. 启动倒计时显示
        """
        self.show_next_word()
        self.update_button_states()  # 更新按钮状态

        # 获取显示间隔设置
        interval_seconds = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_INTERVAL)
        
        if interval_seconds > 0:
            # 停止之前的定时器
            self.timer.stop()
            self.countdown_timer.stop()
            
            # 启动倒计时显示（使用倒计时定时器来控制自动切换）
            self.remaining_time = interval_seconds
            self.countdown_timer.start(1000)  # 每秒更新一次
            self.update_countdown()
        else:
            # 如果设置为0（不自动切换），停止所有定时器并隐藏倒计时
            self.timer.stop()
            self.countdown_timer.stop()
            self.countdown_label.setText("⏱️ --")

    def show_next_word(self):
        """
        根据设置获取并显示下一个单词
        
        根据当前的显示模式（随机/顺序）获取单词，
        并根据中文显示设置控制翻译的可见性。
        """
        # 获取显示模式和中文显示设置
        display_mode = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_MODE)
        show_chinese = self.settings_manager.get_settings(self.settings_manager.KEY_SHOW_CHINESE)

        # 根据显示模式获取单词
        if display_mode == 'random':
            self.current_word_data = self.word_manager.get_random_word()
        else:
            self.current_word_data = self.word_manager.get_next_word()

        # 显示单词数据
        if self.current_word_data:
            self._set_display(
                self.current_word_data.get(self.word_manager.KEY_WORD, "错误"),
                self.current_word_data.get(self.word_manager.KEY_TRANSLATION, "键名不匹配"),
                self.current_word_data.get(self.word_manager.KEY_POS, "")
            )
        else:
            # 没有单词时显示提示信息
            self._set_display("没有单词", "请先添加单词。", "")
            self.timer.stop()

        # 根据设置控制中文翻译的显示
        self.translation_label.setVisible(show_chinese)

    def _set_display(self, word, translation, pos):
        """
        设置单词显示内容
        
        这是一个辅助方法，用于设置单词、翻译和词性标签的文本。
        
        Args:
            word (str): 英文单词
            translation (str): 中文翻译
            pos (str): 词性
        """
        self.word_label.setText(word)
        self.pos_label.setText(pos)
        self.translation_label.setText(translation)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # 左侧菜单
        file_menu = menu_bar.addMenu("文件(&F)")
        # ... (添加, 编辑, 删除等菜单项)
        add_action = file_menu.addAction("添加单词(&A)...")
        add_action.triggered.connect(self.open_add_word_dialog)
        edit_action = file_menu.addAction("编辑单词(&E)...")
        edit_action.triggered.connect(self.open_edit_word_dialog)
        delete_action = file_menu.addAction("删除单词(&D)...")
        delete_action.triggered.connect(self.open_delete_word_dialog)
        file_menu.addSeparator()
        settings_action = file_menu.addAction("设置(&S)...")
        settings_action.triggered.connect(self.open_settings_dialog)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("退出(&X)")
        exit_action.triggered.connect(self.close)

        # 学习菜单
        study_menu = menu_bar.addMenu("学习(&L)")
        history_action = study_menu.addAction("查看学习历史(&H)...")
        history_action.triggered.connect(self.show_history_dialog)

        help_menu = menu_bar.addMenu("帮助(&H)")
        about_action = help_menu.addAction("关于(&B)")
        about_action.triggered.connect(self.show_about_dialog)

        # 右上角搜索框
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        menu_bar.setCornerWidget(search_widget, Qt.Corner.TopRightCorner)

    def open_add_word_dialog(self):
        """打开用于添加新单词的对话框。"""
        dialog = WordEditorDialog(self)
        if dialog.exec(): 
            new_word_data = dialog.get_word_data()
            if not new_word_data[self.word_manager.KEY_WORD] or not new_word_data[self.word_manager.KEY_TRANSLATION]:
                QMessageBox.warning(self, "输入错误", "单词和翻译不能为空。")
                return

            success = self.word_manager.add_word(
                word=new_word_data[self.word_manager.KEY_WORD],
                translation=new_word_data[self.word_manager.KEY_TRANSLATION],
                part_of_speech=new_word_data[self.word_manager.KEY_POS]
            )

            if success:
                self.word_manager.save_changes()
                QMessageBox.information(self, "成功", f"单词 '{new_word_data[self.word_manager.KEY_WORD]}' 已成功添加。")
            else:
                QMessageBox.warning(self, "错误", f"无法添加单词 '{new_word_data[self.word_manager.KEY_WORD]}'，该单词可能已存在。")

    def open_edit_word_dialog(self):
        """打开用于编辑当前显示单词的对话框。"""
        if not self.current_word_data:
            QMessageBox.information(self, "无单词", "当前没有显示的单词可供编辑。")
            return

        dialog = WordEditorDialog(self, word_data=self.current_word_data)
        if dialog.exec():
            updated_data = dialog.get_word_data()
            if not updated_data[self.word_manager.KEY_WORD] or not updated_data[self.word_manager.KEY_TRANSLATION]:
                QMessageBox.warning(self, "输入错误", "单词和翻译不能为空。")
                return
            
            original_word = self.current_word_data[self.word_manager.KEY_WORD]
            success = self.word_manager.edit_word(original_word, updated_data)

            if success:
                self.word_manager.save_changes()
                QMessageBox.information(self, "成功", f"单词 '{original_word}' 已成功更新。")

                self.show_next_word_and_reset_timer()
            else:
                QMessageBox.warning(self, "错误", "无法更新单词，新单词可能与现有单词冲突。")

    def open_delete_word_dialog(self):
        """打开一个对话框来查找并删除一个单词。"""
        word_to_delete, ok = QInputDialog.getText(self, "删除单词", "请输入要删除的英文单词:")

        if ok and word_to_delete:
            word_to_delete = word_to_delete.strip()

            if not self.word_manager.find_word(word_to_delete, key=self.word_manager.KEY_WORD):
                QMessageBox.information(self, "未找到", f"词库中未找到单词 '{word_to_delete}'。")
                return

            reply = QMessageBox.question(self, '确认删除',
                                           f"您确定要永久删除单词 '{word_to_delete}' 吗?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self.word_manager.delete_word(word_to_delete)
                if success:
                    self.word_manager.save_changes()
                    QMessageBox.information(self, "成功", f"单词 '{word_to_delete}' 已被删除。")
                    if self.current_word_data and self.current_word_data.get(self.word_manager.KEY_WORD) == word_to_delete:
                        self.show_next_word()
                else:
                    QMessageBox.warning(self, "错误", f"尝试删除 '{word_to_delete}' 时发生未知错误。")

    def open_settings_dialog(self):
        """打开设置对话框。"""
        dialog = SettingsDialog(self.settings_manager, self)
        if dialog.exec():
            QMessageBox.information(self, "设置已保存", "您的新设置已保存。")
            self.show_next_word_and_reset_timer() 

    def _perform_search(self):
        """获取搜索框内容，执行查找并显示结果。"""
        query = self.search_input.text().strip()
        if not query:
            return  # 如果搜索内容为空则不执行任何操作

        found_word = self.word_manager.find_word(query)

        if found_word:
            word = found_word.get(self.word_manager.KEY_WORD, 'N/A')
            translation = found_word.get(self.word_manager.KEY_TRANSLATION, 'N/A')
            pos = found_word.get(self.word_manager.KEY_POS, 'N/A')
            
            info_text = f"""
            <h3>查找到的单词信息:</h3>
            <p><b>单词:</b> {word}</p>
            <p><b>翻译:</b> {translation}</p>
            <p><b>词性:</b> {pos}</p>
            """
            QMessageBox.information(self, "查找结果", info_text)
        else:
            QMessageBox.information(self, "未找到", f"词库中未找到 '{query}'。")

    def show_about_dialog(self):
        """显示关于对话框，包含应用和作者信息。"""
        name = "李政阳"
        student_id = "9116124039"
        class_info = "数据科学与大数据技术242班"
        github_user = "THINKER-ONLY"
        project_url = "https://github.com/THINKER-ONLY/word_learner"

        about_text = f"""
        <h2>英语背单词小工具 v1.0</h2>
        <p>一个帮助你记忆英语单词的简单应用。</p>
        <p><b>作者信息:</b></p>
        <ul>
            <li><b>姓名:</b> {name}</li>
            <li><b>学号:</b> {student_id}</li>
            <li><b>班级:</b> {class_info}</li>
        </ul>
        <p><b>在GitHub上找到此项目:</b></p>
        <p><a href="{project_url}">{project_url}</a></p>
        """
        QMessageBox.about(self, "关于", about_text)

    def show_history_dialog(self):
        """显示学习历史记录对话框。"""
        history = self.word_manager.get_history()
        history_info = self.word_manager.get_history_info()
        
        if not history:
            QMessageBox.information(self, "学习历史", "您还没有学习任何单词。")
            return
        
        # 创建历史记录对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("学习历史记录")
        dialog.resize(600, 500)
        self.center_dialog(dialog)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # 统计信息
        stats_label = QLabel()
        current_pos = history_info["current_index"] + 1 if history_info["current_index"] >= 0 else 0
        stats_text = f"""
        <h3>📊 学习统计</h3>
        <p><b>总学习次数：</b>{history_info["total_count"]} 次</p>
        <p><b>唯一单词数：</b>{history_info["unique_words"]} 个</p>
        <p><b>当前位置：</b>第 {current_pos} / {history_info["total_count"]} 个</p>
        """
        stats_label.setText(stats_text)
        stats_label.setStyleSheet("""
            background-color: #4a4a4a; 
            color: #ffffff;
            padding: 10px; 
            border-radius: 5px;
            border: 1px solid #666666;
        """)
        layout.addWidget(stats_label)
        
        # 历史记录列表
        history_label = QLabel("<h3>📚 学习历史（按时间顺序）</h3>")
        layout.addWidget(history_label)
        
        # 创建文本显示区域
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            font-family: 'Consolas', 'Monaco', monospace; 
            font-size: 12px;
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 8px;
        """)
        
        # 构建历史记录文本
        history_text = ""
        for i, word_data in enumerate(history, 1):
            word = word_data.get(self.word_manager.KEY_WORD, "N/A")
            translation = word_data.get(self.word_manager.KEY_TRANSLATION, "N/A")
            pos = word_data.get(self.word_manager.KEY_POS, "")
            
            # 标记当前位置
            is_current = i - 1 == history_info["current_index"]
            marker = " ← 当前位置" if is_current else ""
            pos_text = f" ({pos})" if pos else ""
            
            # 为当前位置添加特殊样式
            if is_current:
                history_text += f">> {i:2d}. {word:<15} → {translation}{pos_text}{marker}\n"
            else:
                history_text += f"   {i:2d}. {word:<15} → {translation}{pos_text}{marker}\n"
        
        text_edit.setText(history_text)
        
        # 滚动到当前位置
        if history_info["current_index"] >= 0:
            cursor = text_edit.textCursor()
            # 计算大概的行位置并滚动到那里
            lines_to_scroll = history_info["current_index"]
            for _ in range(lines_to_scroll):
                cursor.movePosition(cursor.MoveOperation.Down)
            text_edit.setTextCursor(cursor)
            text_edit.ensureCursorVisible()
        
        layout.addWidget(text_edit)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.setStyleSheet("""
            QPushButton {
                background-color: #5a5a5a;
                color: #ffffff;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.exec() 

    def toggle_chinese_display(self, checked):
        """切换中文显示状态。"""
        self.settings_manager.set_settings(self.settings_manager.KEY_SHOW_CHINESE, checked)
        # 只切换当前单词的中文显示状态，不跳转到下一个单词
        self.translation_label.setVisible(checked)
    
    def update_countdown(self):
        """更新倒计时显示。"""
        if self.remaining_time > 0:
            # 显示剩余时间
            self.countdown_label.setText(f"⏱️ {self.remaining_time}s")
            self.remaining_time -= 1
        else:
            # 时间到了，切换到下一个单词并重启计时
            self.countdown_timer.stop()
            self.show_next_word()  # 切换单词
            self.update_button_states()  # 更新按钮状态
            
            # 重新启动倒计时
            interval_seconds = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_INTERVAL)
            if interval_seconds > 0:
                self.remaining_time = interval_seconds
                self.countdown_timer.start(1000)
                self.update_countdown()
            else:
                self.countdown_label.setText("⏱️ --")

    def show_previous_word(self):
        """显示上一个单词。"""
        previous_word = self.word_manager.get_previous_word()
        if previous_word:
            self.current_word_data = previous_word
            show_chinese = self.settings_manager.get_settings(self.settings_manager.KEY_SHOW_CHINESE)
            
            self._set_display(
                previous_word.get(self.word_manager.KEY_WORD, "错误"),
                previous_word.get(self.word_manager.KEY_TRANSLATION, "键名不匹配"),
                previous_word.get(self.word_manager.KEY_POS, "")
            )
            
            self.translation_label.setVisible(show_chinese)
            
            # 停止自动切换计时器（用户在浏览历史时不应自动跳转）
            self.timer.stop()
            self.countdown_timer.stop()
            self.countdown_label.setText("⏱️ --")
        
        self.update_button_states()

    def show_next_word_smart(self):
        """智能显示下一个单词：优先从历史记录中获取，否则生成新单词。"""
        if self.word_manager.has_next_history_word():
            next_word = self.word_manager.get_next_history_word()
            if next_word:
                self.current_word_data = next_word
                show_chinese = self.settings_manager.get_settings(self.settings_manager.KEY_SHOW_CHINESE)
                
                self._set_display(
                    next_word.get(self.word_manager.KEY_WORD, "错误"),
                    next_word.get(self.word_manager.KEY_TRANSLATION, "键名不匹配"),
                    next_word.get(self.word_manager.KEY_POS, "")
                )
                
                self.translation_label.setVisible(show_chinese)
                
                if self.word_manager.is_at_history_end():
                    interval_seconds = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_INTERVAL)
                    if interval_seconds > 0:
                        self.timer.stop()
                        self.countdown_timer.stop()
                        self.remaining_time = interval_seconds
                        self.countdown_timer.start(1000)
                        self.update_countdown()
                    else:
                        self.countdown_label.setText("⏱️ --")
                else:
                    self.countdown_label.setText("⏱️ --")
        else:
            self.show_next_word_and_reset_timer()
        
        self.update_button_states()

    def update_button_states(self):
        """更新按钮的启用/禁用状态。"""
        # 根据是否有上一个单词来更新"上一个"按钮状态
        self.prev_button.setEnabled(self.word_manager.has_previous_word()) 