from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QInputDialog, QLineEdit, QHBoxLayout, QCheckBox, QDialog, QTextEdit, QDialogButtonBox, QScrollArea, QFrame
from PyQt6.QtCore import Qt, QTimer

from src.core.word_manager import WordManager
from src.core.settings_manager import SettingsManager
from src.core.ai_service import DeepSeekAIService
from src.ui.word_editor_dialog import WordEditorDialog
from src.ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("背单词小工具")
        self.setGeometry(100, 100, 675, 375)
        self.setMinimumSize(600, 375)

        self.settings_manager = SettingsManager("config.json")
        self.word_manager = WordManager("assets/words.json")
        self.current_word_data = None
        
        # 初始化AI服务
        api_key = self.settings_manager.get_settings(self.settings_manager.KEY_DEEPSEEK_API_KEY)
        self.ai_service = DeepSeekAIService(api_key) 

        # 将搜索组件创建为实例变量，以便在多个方法中访问
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("查找单词...")
        self.search_input.setMaximumWidth(375) # 限制搜索框最大宽度
        self.search_button = QPushButton("🔍")

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

    def resizeEvent(self, event):
        """Handle window resize to make fonts responsive."""

        base_height = self.height()
        word_font_size = max(18, int(base_height / 7))
        pos_font_size = max(12, int(base_height / 14))
        translation_font_size = max(14, int(base_height / 10))

        font_word = self.word_label.font()
        font_word.setPointSize(word_font_size)
        self.word_label.setFont(font_word)

        font_pos = self.pos_label.font()
        font_pos.setPointSize(pos_font_size)
        self.pos_label.setFont(font_pos)

        font_translation = self.translation_label.font()
        font_translation.setPointSize(translation_font_size)
        self.translation_label.setFont(font_translation)
        
        if event:
            super().resizeEvent(event)

    def show_next_word_and_reset_timer(self):
        """显示一个新单词，并根据配置重置定时器。"""
        self.show_next_word()
        self.update_button_states()  # 更新按钮状态

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
        """根据设置获取并显示下一个单词。"""

        display_mode = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_MODE)
        show_chinese = self.settings_manager.get_settings(self.settings_manager.KEY_SHOW_CHINESE)

        if display_mode == 'random':
            self.current_word_data = self.word_manager.get_random_word()
        else:
            self.current_word_data = self.word_manager.get_next_word()

        if self.current_word_data:
            self._set_display(
                self.current_word_data.get(self.word_manager.KEY_WORD, "错误"),
                self.current_word_data.get(self.word_manager.KEY_TRANSLATION, "键名不匹配"),
                self.current_word_data.get(self.word_manager.KEY_POS, "")
            )
        else:
            self._set_display("没有单词", "请先添加单词。", "")
            self.timer.stop() 

        self.translation_label.setVisible(show_chinese)

    def _set_display(self, word, translation, pos):
        """辅助方法：设置单词、翻译和词性标签的文本。"""
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
        study_menu.addSeparator()
        ai_action = study_menu.addAction("AI学习助手(&A)...")
        ai_action.triggered.connect(self.show_ai_dialog)

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
            # 更新AI服务的API密钥
            api_key = self.settings_manager.get_settings(self.settings_manager.KEY_DEEPSEEK_API_KEY)
            self.ai_service.set_api_key(api_key)
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
        dialog.setGeometry(200, 200, 600, 500)
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

    def show_ai_dialog(self):
        """显示AI学习助手对话框。"""
        # 创建AI对话窗口
        dialog = QDialog(self)
        dialog.setWindowTitle("🤖 AI学习助手")
        dialog.setGeometry(300, 200, 700, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # 欢迎信息和当前单词显示
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_frame)
        
        welcome_label = QLabel("🎯 AI学习助手")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        welcome_layout.addWidget(welcome_label)
        
        # 显示当前单词信息
        if self.current_word_data:
            current_word = self.current_word_data.get(self.word_manager.KEY_WORD, "")
            current_translation = self.current_word_data.get(self.word_manager.KEY_TRANSLATION, "")
            current_pos = self.current_word_data.get(self.word_manager.KEY_POS, "")
            
            current_info = f"当前单词: {current_word}"
            if current_translation:
                current_info += f" → {current_translation}"
            if current_pos:
                current_info += f" ({current_pos})"
            
            current_label = QLabel(current_info)
            current_label.setStyleSheet("font-size: 14px; color: #81C784; margin-top: 5px;")
            welcome_layout.addWidget(current_label)
        
        layout.addWidget(welcome_frame)
        
        # 聊天历史显示区域
        self.chat_scroll = QScrollArea()
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_widget)
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555555;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
        """)
        layout.addWidget(self.chat_scroll)
        
        # 快捷功能按钮
        quick_actions_frame = QFrame()
        quick_actions_layout = QHBoxLayout(quick_actions_frame)
        
        actions = [
            ("📝 解释单词", "explain"),
            ("💡 记忆技巧", "memory"),
            ("📖 生成例句", "examples"),
            ("🎯 单词测试", "test")
        ]
        
        for action_text, action_type in actions:
            btn = QPushButton(action_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            btn.clicked.connect(lambda checked, t=action_type: self.send_ai_quick_action(t))
            quick_actions_layout.addWidget(btn)
        
        layout.addWidget(quick_actions_frame)
        
        # 输入区域
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("请输入您的问题，比如：如何记住这个单词？")
        self.ai_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.ai_input.returnPressed.connect(self.send_ai_message)
        input_layout.addWidget(self.ai_input)
        
        send_btn = QPushButton("发送")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        send_btn.clicked.connect(self.send_ai_message)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_frame)
        
        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # 添加欢迎消息
        self.add_ai_message("👋 你好！我是您的AI学习助手。我可以帮助您：\n\n"
                           "• 解释单词的含义和用法\n"
                           "• 提供记忆技巧和联想方法\n"
                           "• 生成实用的例句\n"
                           "• 创建单词测试和练习\n\n"
                           "您可以点击上方的快捷按钮，或者直接输入问题！", is_ai=True)
        
        # 存储对话框引用以便在其他方法中使用
        self.ai_dialog = dialog
        
        dialog.exec()

    def add_ai_message(self, message, is_ai=True):
        """添加AI对话消息到聊天区域。"""
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(10, 5, 10, 5)
        
        if is_ai:
            # AI消息样式
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #2E7D32;
                    border-radius: 10px;
                    margin: 5px 50px 5px 5px;
                }
            """)
            sender_label = QLabel("🤖 AI助手")
            sender_label.setStyleSheet("font-weight: bold; color: #A5D6A7; font-size: 12px;")
        else:
            # 用户消息样式
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #1565C0;
                    border-radius: 10px;
                    margin: 5px 5px 5px 50px;
                }
            """)
            sender_label = QLabel("👤 您")
            sender_label.setStyleSheet("font-weight: bold; color: #BBDEFB; font-size: 12px;")
        
        message_layout.addWidget(sender_label)
        
        content_label = QLabel(message)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #ffffff; font-size: 13px; line-height: 1.4;")
        message_layout.addWidget(content_label)
        
        self.chat_layout.addWidget(message_frame)
        
        # 滚动到底部
        QTimer.singleShot(50, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()))

    def send_ai_message(self):
        """发送用户输入的消息给AI。"""
        user_message = self.ai_input.text().strip()
        if not user_message:
            return
        
        # 添加用户消息
        self.add_ai_message(user_message, is_ai=False)
        self.ai_input.clear()
        
        # 模拟AI响应（这里可以集成真实的AI API）
        self.simulate_ai_response(user_message)

    def send_ai_quick_action(self, action_type):
        """处理快捷功能按钮。"""
        if not self.current_word_data:
            self.add_ai_message("请先选择一个单词再使用快捷功能。", is_ai=True)
            return
        
        word = self.current_word_data.get(self.word_manager.KEY_WORD, "")
        translation = self.current_word_data.get(self.word_manager.KEY_TRANSLATION, "")
        
        if action_type == "explain":
            user_msg = f"请详细解释单词 '{word}' 的含义和用法"
        elif action_type == "memory":
            user_msg = f"请为单词 '{word}' 提供记忆技巧"
        elif action_type == "examples":
            user_msg = f"请为单词 '{word}' 生成一些例句"
        elif action_type == "test":
            user_msg = f"请为单词 '{word}' 创建一个测试"
        
        # 添加用户消息
        self.add_ai_message(user_msg, is_ai=False)
        
        # 模拟AI响应
        self.simulate_ai_response(user_msg, action_type)

    def simulate_ai_response(self, user_message, action_type=None):
        """使用DeepSeek AI进行实际对话。"""
        # 检查AI服务是否配置
        if not self.ai_service.is_configured():
            response = "❌ DeepSeek AI未配置。请在设置中添加您的API密钥。\n\n" \
                      "💡 获取API密钥：\n" \
                      "1. 访问 https://platform.deepseek.com/\n" \
                      "2. 注册并登录账户\n" \
                      "3. 在API密钥页面创建新密钥\n" \
                      "4. 复制密钥到应用设置中"
            QTimer.singleShot(500, lambda: self.add_ai_message(response, is_ai=True))
            return
        
        # 显示"AI正在思考"的提示
        thinking_response = "🤔 正在思考中..."
        QTimer.singleShot(200, lambda: self.add_ai_message(thinking_response, is_ai=True))
        
        # 准备单词信息
        word = ""
        translation = ""
        pos = ""
        if self.current_word_data:
            word = self.current_word_data.get(self.word_manager.KEY_WORD, "")
            translation = self.current_word_data.get(self.word_manager.KEY_TRANSLATION, "")
            pos = self.current_word_data.get(self.word_manager.KEY_POS, "")
        
        # 根据操作类型调用相应的AI方法
        def get_ai_response():
            try:
                if not self.current_word_data and action_type in ["explain", "memory", "examples", "test"]:
                    return "我需要知道当前的单词才能更好地帮助您。请先选择一个单词。"
                
                if action_type == "explain":
                    return self.ai_service.get_word_explanation(word, translation, pos)
                elif action_type == "memory":
                    return self.ai_service.get_memory_tips(word, translation, pos)
                elif action_type == "examples":
                    return self.ai_service.get_example_sentences(word, translation, pos)
                elif action_type == "test":
                    return self.ai_service.create_word_test(word, translation, pos)
                else:
                    return self.ai_service.chat_with_context(user_message, word, translation, pos)
            except Exception as e:
                return f"❌ AI服务调用失败: {str(e)}"
        
        # 在后台线程中调用AI（避免界面卡顿）
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class AIWorker(QThread):
            response_ready = pyqtSignal(str)
            
            def __init__(self, ai_func):
                super().__init__()
                self.ai_func = ai_func
            
            def run(self):
                response = self.ai_func()
                self.response_ready.emit(response)
        
        def on_response_ready(response):
            # 移除"正在思考"的消息
            if self.chat_layout.count() > 0:
                last_item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
                if last_item and last_item.widget():
                    last_widget = last_item.widget()
                    if hasattr(last_widget, 'findChild'):
                        labels = last_widget.findChildren(QLabel)
                        for label in labels:
                            if "正在思考中" in label.text():
                                self.chat_layout.removeWidget(last_widget)
                                last_widget.deleteLater()
                                break
            
            # 添加真实的AI响应
            self.add_ai_message(response, is_ai=True)
        
        # 启动AI工作线程
        self.ai_worker = AIWorker(get_ai_response)
        self.ai_worker.response_ready.connect(on_response_ready)
        self.ai_worker.start()

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
        # 如果用户在历史记录中浏览，且历史记录中有下一个单词
        if self.word_manager.has_next_history_word():
            # 从历史记录中获取下一个单词，不重启计时器
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
                
                # 如果回到了历史记录的末尾，可以重新启动计时器
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
                    # 仍在历史记录中，保持计时器停止状态
                    self.countdown_label.setText("⏱️ --")
        else:
            # 没有历史记录中的下一个单词，生成新单词并重启计时器
            self.show_next_word_and_reset_timer()
        
        self.update_button_states()

    def update_button_states(self):
        """更新按钮的启用/禁用状态。"""
        # 根据是否有上一个单词来更新"上一个"按钮状态
        self.prev_button.setEnabled(self.word_manager.has_previous_word()) 