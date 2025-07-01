from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QInputDialog, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

from src.core.word_manager import WordManager
from src.core.settings_manager import SettingsManager
from src.ui.word_editor_dialog import WordEditorDialog
from src.ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("背单词小工具")
        self.setGeometry(100, 100, 450, 250)
        self.setMinimumSize(400, 250)

        self.settings_manager = SettingsManager("config.json")
        self.word_manager = WordManager("assets/words.json")
        self.current_word_data = None 

        # 将搜索组件创建为实例变量，以便在多个方法中访问
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("查找单词...")
        self.search_input.setMaximumWidth(250) # 限制搜索框最大宽度
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


        self.next_button = QPushButton("下一个")
        self.next_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.next_button.clicked.connect(self.show_next_word_and_reset_timer)
        main_layout.addWidget(self.next_button)

        # 信号连接
        self.search_button.clicked.connect(self._perform_search)
        self.search_input.returnPressed.connect(self._perform_search)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_word)

        self.show_next_word_and_reset_timer()
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

        interval_seconds = self.settings_manager.get_settings(self.settings_manager.KEY_DISPLAY_INTERVAL)
        if interval_seconds > 0:
            self.timer.start(interval_seconds * 1000)  

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