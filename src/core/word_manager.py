import json
import random

class WordManager:
    def __init__(self, filepath):
        """
        初始化 WordManager。
        :param filepath: words.json 文件的路径。
        """
        self.filepath = filepath
        self.words = []
        self.current_index = -1
        self.is_dirty = False
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
                # indent=4 使json文件格式化，便于阅读
                # ensure_ascii=False 确保中文字符能正确写入
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
            # 提供了key，执行精确查找
            for word in self.words:
                if word.get(key) == value_to_find:
                    return word
        else:
            for word in self.words:
                if word.get('word') == value_to_find or word.get('translation') == value_to_find:
                    return word
        return None

    def get_random_word(self):
        """
        从单词库中随机返回一个单词。
        :return: 一个随机的单词字典，如果库为空则返回 None。
        """
        if not self.words:
            return None
        return random.choice(self.words)

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
        
        return self.words[self.current_index]

    def reset_sequential_index(self):
        """
        重置顺序播放的索引，下次调用 get_next_word 将从头开始。
        """
        self.current_index = -1

    def get_all_words(self):
        """
        获取当前加载的所有单词。
        :return: 包含所有单词字典的列表。
        """
        return self.words

    def add_word(self, word, translation, part_of_speech=""):
        """
        向单词库中添加一个新单词。
        :param word: 英文单词。
        :param translation: 中文释义。
        :param part_of_speech: 词性。
        :return: 如果添加成功返回 True，如果单词已存在则返回 False。
        """
        if self.find_word(word, key='word'):
            print(f"添加失败: 单词 '{word}' 已存在。")
            return False

        new_word = {
            'word': word,
            'translation': translation,
            'partOfSpeech': part_of_speech
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

        word_to_edit = self.find_word(original_word, key='word')

        if not word_to_edit:
            print(f"编辑失败: 在库中未找到单词 '{original_word}'。")
            return False

        # 如果要修改英文单词本身，需要确保新单词不会与库中其他单词重复。
        new_word = updates.get('word')
        if new_word and new_word != original_word:
            if self.find_word(new_word, key='word'):
                print(f"编辑失败: 新单词 '{new_word}' 已经存在于库中。")
                return False

        # 在内存中应用更新
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
        self.words = [word for word in self.words if word.get('word') != word_to_delete]
        
        if len(self.words) < original_count:
            self.is_dirty = True
            return True
        else:
            print(f"删除失败: 未找到单词 '{word_to_delete}'。")
            return False