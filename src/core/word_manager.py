# -*- coding: utf-8 -*-
"""
单词管理器模块
=============

负责管理单词数据的核心模块，包括：
- 单词的加载和保存
- 随机/顺序获取单词
- 单词的增删改查
- 学习历史记录管理

单词数据以 JSON 格式存储，支持英文单词、中文翻译和词性信息。
"""

import json
import random

class WordManager:
    """
    单词管理器
    
    负责管理单词数据的核心类，提供单词的存储、检索、
    随机/顺序播放以及历史记录等功能。
    """
    
    # 单词字典中的键名常量
    KEY_WORD = 'word'                # 英文单词
    KEY_TRANSLATION = 'translation'  # 中文翻译
    KEY_POS = 'partOfSpeech'         # 词性

    def __init__(self, filepath):
        """
        初始化单词管理器
        
        Args:
            filepath (str): 单词数据文件的路径，通常是 words.json
        """
        self.filepath = filepath
        self.words = []                # 所有单词列表
        self.current_index = -1        # 当前顺序播放索引
        
        # 脏位标记，用于标记内存中的数据是否被修改但尚未保存
        self.is_dirty = False
        
        # 历史记录，用于支持"上一个"功能
        self.history = []              # 历史记录列表
        self.history_index = -1        # 历史记录索引
        
        # 加载单词数据
        self._load_words()

    def _load_words(self):
        """
        从单词数据文件加载单词列表
        
        如果文件不存在或内容损坏，则会创建一个空的列表，
        并尝试创建一个空的 JSON 文件。
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 文件不存在或格式错误时创建空列表
            self.words = []
            self._save_words()

    def _save_words(self):
        """
        将当前的单词列表保存到 JSON 文件
        
        使用 UTF-8 编码保存，确保中文字符正确显示。
        保存成功后会清除脏位标记。
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, indent=4, ensure_ascii=False)
            self.is_dirty = False
        except IOError as e:
            print(f"错误: 无法将单词保存到 {self.filepath}: {e}")

    def save_changes(self):
        """
        保存数据更改到文件
        
        这是一个公共方法，只有当数据被修改时（is_dirty 为 True）
        才会执行保存操作。通常在程序退出时调用。
        """
        if self.is_dirty:
            self._save_words()

    def find_word(self, value_to_find, key=None):
        """
        灵活查找单词
        
        支持两种查找模式：
        1. 指定键名查找：在指定的字段中进行精确匹配
        2. 模糊查找：在英文单词和中文翻译字段中查找
        
        Args:
            value_to_find (str): 要查找的值（英文或中文）
            key (str, optional): 要匹配的键名，如 'word' 或 'translation'
            
        Returns:
            dict: 匹配的单词字典，如果未找到则返回 None
        """
        if key:
            # 在指定字段中查找
            for word in self.words:
                if word.get(key) == value_to_find:
                    return word
        else:
            # 在英文单词和中文翻译字段中查找
            for word in self.words:
                if (word.get(self.KEY_WORD) == value_to_find or 
                    word.get(self.KEY_TRANSLATION) == value_to_find):
                    return word
        return None

    def get_random_word(self):
        """
        从单词库中随机获取一个单词
        
        随机选择一个单词并将其添加到历史记录中。
        适用于随机学习模式。
        
        Returns:
            dict: 随机选择的单词字典，如果单词库为空则返回 None
        """
        if not self.words:
            return None
            
        # 随机选择一个单词
        word = random.choice(self.words)
        self._add_to_history(word)
        return word

    def get_next_word(self):
        """
        按顺序获取下一个单词
        
        按照单词列表的顺序依次获取单词，到达末尾时会循环到开头。
        适用于顺序学习模式。
        
        Returns:
            dict: 下一个单词的字典，如果单词库为空则返回 None
        """
        if not self.words:
            return None
        
        # 移动到下一个索引
        self.current_index += 1
        if self.current_index >= len(self.words):
            self.current_index = 0  # 循环到开头
        
        word = self.words[self.current_index]
        self._add_to_history(word)
        return word

    def reset_sequential_index(self):
        """
        重置顺序播放的索引
        
        将当前索引重置为 -1，下次调用 get_next_word() 
        将从列表的第一个单词开始。
        """
        self.current_index = -1

    def _add_to_history(self, word):
        """
        将单词添加到历史记录中。
        :param word: 要添加的单词字典。
        """
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        if not self.history or self.history[-1].get(self.KEY_WORD) != word.get(self.KEY_WORD):
            self.history.append(word.copy())
            if len(self.history) > 100:
                self.history.pop(0)
                if self.history_index >= len(self.history):
                    self.history_index = len(self.history) - 1
            
        self.history_index = len(self.history) - 1

    def get_previous_word(self):
        """
        获取历史记录中的上一个单词。
        :return: 上一个单词的字典，如果没有上一个单词则返回 None。
        """
        if not self.history or self.history_index <= 0:
            return None
        
        self.history_index -= 1
        return self.history[self.history_index].copy()

    def has_previous_word(self):
        """
        检查是否有上一个单词可用。
        :return: 如果有上一个单词返回 True，否则返回 False。
        """
        return len(self.history) > 0 and self.history_index > 0

    def get_next_history_word(self):
        """
        获取历史记录中的下一个单词（用于用户在历史记录中浏览时）。
        :return: 历史记录中的下一个单词，如果没有则返回 None。
        """
        if not self.history or self.history_index >= len(self.history) - 1:
            return None
        
        self.history_index += 1
        return self.history[self.history_index].copy()

    def has_next_history_word(self):
        """
        检查历史记录中是否有下一个单词。
        :return: 如果有下一个历史单词返回 True，否则返回 False。
        """
        return len(self.history) > 0 and self.history_index < len(self.history) - 1

    def is_at_history_end(self):
        """
        检查是否在历史记录的末尾。
        :return: 如果在历史记录末尾返回 True，否则返回 False。
        """
        return len(self.history) > 0 and self.history_index == len(self.history) - 1

    def get_all_words(self):
        """
        获取当前加载的所有单词。
        :return: 包含所有单词字典的列表。
        """
        return self.words

    def get_history(self):
        """
        获取学习历史记录。
        :return: 包含历史记录的列表，按时间顺序排列（最早的在前）。
        """
        return self.history.copy()

    def get_history_info(self):
        """
        获取历史记录的统计信息。
        :return: 包含历史记录统计信息的字典。
        """
        if not self.history:
            return {
                "total_count": 0,
                "current_index": -1,
                "unique_words": 0
            }
        
        # 统计唯一单词数量
        unique_words = set()
        for word in self.history:
            unique_words.add(word.get(self.KEY_WORD, ""))
        
        return {
            "total_count": len(self.history),
            "current_index": self.history_index,
            "unique_words": len(unique_words)
        }

    def add_word(self, word, translation, part_of_speech=""):
        """
        向单词库中添加一个新单词。
        :param word: 英文单词。
        :param translation: 中文释义。
        :param part_of_speech: 词性。
        :return: 如果添加成功返回 True，如果单词已存在则返回 False。
        """
        if self.find_word(word, key=self.KEY_WORD):
            print(f"添加失败: 单词 '{word}' 已存在。")
            return False

        new_word = {
            self.KEY_WORD: word,
            self.KEY_TRANSLATION: translation,
            self.KEY_POS: part_of_speech
        }
        self.words.append(new_word)
        self.is_dirty = True
        return True

    def edit_word(self, original_word, updates):
        """
        编辑一个现有的单词。
        此版本遵循"缓冲区"模式，只修改内存中的数据并设置脏位。

        :param original_word: 要编辑的单词的原始英文 (例如: 'apple')。
        :param updates: 一个包含更新信息的字典。
                         例如: {'translation': '苹果公司'} 或 {'word': 'apples', 'partOfSpeech': 'n. pl.'}
        :return: 如果编辑成功返回 True，如果发生错误则返回 False。
        """
        if not isinstance(updates, dict):
            print("编辑失败: 'updates' 参数必须是一个字典。")
            return False

        word_to_edit = self.find_word(original_word, key=self.KEY_WORD)

        if not word_to_edit:
            print(f"编辑失败: 在库中未找到单词 '{original_word}'。")
            return False

        new_word = updates.get(self.KEY_WORD)
        if new_word and new_word != original_word:
            if self.find_word(new_word, key=self.KEY_WORD):
                print(f"编辑失败: 新单词 '{new_word}' 已经存在于库中。")
                return False

        word_to_edit.update(updates)
        self.is_dirty = True
        return True

    def delete_word(self, word_to_delete):
        """
        根据英文单词从库中删除一个单词。
        :param word_to_delete: 要删除的单词的英文。
        :return: 如果删除成功返回 True，否则返回 False。
        """
        original_count = len(self.words)
        self.words = [word for word in self.words if word.get(self.KEY_WORD) != word_to_delete]
        
        if len(self.words) < original_count:
            self.is_dirty = True
            return True
        else:
            print(f"删除失败: 未找到单词 '{word_to_delete}'。")
            return False