import json
import random

class WordManager:
    # 用于在单词字典中访问各项信息的键
    KEY_WORD = 'word'
    KEY_TRANSLATION = 'translation'
    KEY_POS = 'partOfSpeech'

    def __init__(self, filepath):
        """
        初始化 WordManager。
        :param filepath: words.json 文件的路径。
        """
        self.filepath = filepath
        self.words = []
        self.current_index = -1
        # 脏位 (dirty bit)，用于标记内存中的数据是否被修改但尚未保存
        self.is_dirty = False
        # 历史记录，用于支持"上一个"功能
        self.history = []
        self.history_index = -1
        self._load_words()

    def _load_words(self):
        """
        从 JSON 文件加载单词列表。
        如果文件不存在或内容损坏，则会创建一个空的列表，并尝试写入一个空的json文件。
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.words = []
            self._save_words()

    def _save_words(self):
        """
        将当前的单词列表保存回 JSON 文件。
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, indent=4, ensure_ascii=False)
            self.is_dirty = False
        except IOError as e:
            print(f"错误: 无法将单词保存到 {self.filepath}: {e}")

    def save_changes(self):
        """
        如果数据发生过修改 (is_dirty 为 True)，则将其保存到文件。
        这是一个公共方法，提供给外部调用者 (例如UI层) 在适当时机保存。
        """
        if self.is_dirty:
            self._save_words()

    def find_word(self, value_to_find, key=None):
        """
        灵活查找单词。
        - 如果提供了 key (如 'word' 或 'translation')，则进行精确的键值匹配。
        - 如果未提供 key，则默认在 'word' 和 'translation' 两个字段中查找。
        :param value_to_find: 要查找的值 (英文或中文)。
        :param key: (可选) 要匹配的键, 例如 'word' 或 'translation'。
        :return: 匹配的单词字典，如果未找到则返回 None。
        """
        if key:
            for word in self.words:
                if word.get(key) == value_to_find:
                    return word
        else:
            for word in self.words:
                if word.get(self.KEY_WORD) == value_to_find or word.get(self.KEY_TRANSLATION) == value_to_find:
                    return word
        return None

    def get_random_word(self):
        """
        从单词库中随机返回一个单词。
        :return: 一个随机的单词字典，如果库为空则返回 None。
        """
        if not self.words:
            return None
        word = random.choice(self.words)
        self._add_to_history(word)
        return word

    def get_next_word(self):
        """
        按顺序获取下一个单词，到达末尾时会循环到开头。
        :return: 下一个单词的字典，如果库为空则返回 None。
        """
        if not self.words:
            return None
        
        self.current_index += 1
        if self.current_index >= len(self.words):
            self.current_index = 0
        
        word = self.words[self.current_index]
        self._add_to_history(word)
        return word

    def reset_sequential_index(self):
        """
        重置顺序播放的索引，下次调用 get_next_word 将从头开始。
        """
        self.current_index = -1

    def _add_to_history(self, word):
        """
        将单词添加到历史记录中。
        :param word: 要添加的单词字典。
        """
        # 如果当前不在历史记录的末尾（用户使用了"上一个"功能），
        # 则删除当前位置之后的所有历史记录
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # 避免连续重复的单词
        if not self.history or self.history[-1].get(self.KEY_WORD) != word.get(self.KEY_WORD):
            self.history.append(word.copy())
            # 限制历史记录长度，避免内存过度使用
            if len(self.history) > 100:
                self.history.pop(0)
                # 删除第一个元素后，索引位置相对不变，但要确保不超出边界
                if self.history_index >= len(self.history):
                    self.history_index = len(self.history) - 1
            
        # 更新历史索引到最新位置
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

        # 如果要修改英文单词本身，需要确保新单词不会与库中其他单词重复
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