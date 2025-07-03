# -*- coding: utf-8 -*-
"""
设置管理器模块
=============

负责管理应用程序的配置设置，包括：
- 单词显示间隔时间
- 单词显示模式（随机/顺序）
- 中文翻译显示控制

设置数据以 JSON 格式存储在配置文件中。
"""

import json

class SettingsManager:
    """
    应用程序设置管理器
    
    负责加载、保存和管理应用程序的各项配置设置。
    所有设置都会持久化保存到 JSON 配置文件中。
    """
    
    # 配置项键名常量
    KEY_DISPLAY_INTERVAL = "display_interval"  # 显示间隔时间（秒）
    KEY_DISPLAY_MODE = "display_mode"          # 显示模式：random（随机）/ sequential（顺序）
    KEY_SHOW_CHINESE = "show_chinese"          # 是否显示中文翻译

    def __init__(self, filepath):
        """
        初始化设置管理器
        
        Args:
            filepath (str): 配置文件的路径，通常是 config.json
        """
        self.filepath = filepath
        
        # 默认设置值
        self.defaults = {
            self.KEY_DISPLAY_INTERVAL: 3,      # 默认3秒自动切换
            self.KEY_DISPLAY_MODE: "random",   # 默认随机模式
            self.KEY_SHOW_CHINESE: True,       # 默认显示中文
        }
        
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """
        从配置文件加载设置
        
        如果配置文件不存在或格式错误，则使用默认设置。
        用户设置会与默认设置合并，确保所有必要的配置项都存在。
        """
        try:
            # 尝试读取配置文件
            with open(self.filepath, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
            
            # 合并默认设置和用户设置
            self.settings = {**self.defaults, **user_settings}
            
        except (FileNotFoundError, json.JSONDecodeError):
            # 文件不存在或格式错误时使用默认设置
            self.settings = self.defaults.copy()

    def get_settings(self, key):
        """
        获取指定配置项的值
        
        Args:
            key (str): 配置项的键名
            
        Returns:
            配置项的值，如果不存在则返回 None
        """
        return self.settings.get(key)

    def set_settings(self, key, value):
        """
        设置指定配置项的值
        
        设置完成后会立即保存到配置文件。
        
        Args:
            key (str): 配置项的键名
            value: 配置项的值
        """
        self.settings[key] = value
        self._save_to_file()

    def _save_to_file(self):
        """
        将当前设置保存到配置文件
        
        使用 UTF-8 编码保存 JSON 格式的配置数据。
        如果保存失败会打印错误信息。
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"错误: 无法写入配置文件 {self.filepath}: {e}")