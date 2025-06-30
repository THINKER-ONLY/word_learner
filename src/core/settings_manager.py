import json

class SettingsManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.defaults = {
            "display_interval": 3,
            "display_mode": "random",
            "show_chinese": True,
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
            print(f"错误: 无法写入配置文件 at {self.filepath}: {e}")