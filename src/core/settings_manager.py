import json

class SettingsManager:
    # 用于在 setting 字典中访问各项设置的键
    KEY_DISPLAY_INTERVAL = "display_interval"
    KEY_DISPLAY_MODE = "display_mode"
    KEY_SHOW_CHINESE = "show_chinese"
    # ---

    def __init__(self, filepath):
        """
        初始化设置管理器。
        :param filepath: config.json 文件的路径。
        """
        self.filepath = filepath
        self.defaults = {
            self.KEY_DISPLAY_INTERVAL: 3,
            self.KEY_DISPLAY_MODE: "random",
            self.KEY_SHOW_CHINESE: True,
        }
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """
        从 JSON 文件加载设置。
        如果文件不存在或数据损坏，则使用默认设置。
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
            # 使用默认设置填充用户设置中缺失的键，确保配置的完整性
            self.settings = {**self.defaults, **user_settings}
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = self.defaults.copy()

    def get_settings(self, key):
        """获取指定键的设置值。"""
        return self.settings.get(key)

    def set_settings(self, key, value):
        """设置指定键的值，并立即保存到文件。"""
        self.settings[key] = value
        self._save_to_file()

    def _save_to_file(self):
        """将当前设置保存到 JSON 文件。"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"错误: 无法写入配置文件于 {self.filepath}: {e}")