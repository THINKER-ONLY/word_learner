import json

class SettingsManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.defaults = {
            "display_interval": 3,
            "display_mode": "random",
            "show_chinese": True,
        }

    def load_settings(self):
        pass

    def get_settings(self, key):
        pass

    def set_settings(self, key, value):
        pass

    def _save_to_file(self):
        pass