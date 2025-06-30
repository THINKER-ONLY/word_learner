import json
import random

class WordManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.words = []
        self.current_index = -1
        self._load_words()

    def _load_words(self):
        pass

    def _save_words(self):
        pass

    def find_word(self, key, value):
        pass
    
    def get_random_word(self):
        pass

    def get_next_word(self):
        pass

    def reset_sequential_index(self):
        pass

    def get_all_word(self):
        pass

    def add_word(self, en, cn, mean):
        pass

    def edit_word(self, origin, new_en, new_cn):
        pass

    def delete_word(self, key):
        pass