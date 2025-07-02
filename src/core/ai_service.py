import json
import requests
from typing import Dict, Any, Optional

class DeepSeekAIService:
    """DeepSeek AI服务类，用于处理AI对话和单词学习助手功能。"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek AI服务。
        :param api_key: DeepSeek API密钥
        :param base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = "deepseek-chat"  # DeepSeek的对话模型
        
    def set_api_key(self, api_key: str):
        """设置API密钥。"""
        self.api_key = api_key
    
    def is_configured(self) -> bool:
        """检查AI服务是否已正确配置。"""
        return self.api_key is not None and len(self.api_key.strip()) > 0
    
    def call_ai(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        调用DeepSeek API进行对话。
        :param messages: 对话消息列表
        :param temperature: 温度参数，控制回答的随机性
        :param max_tokens: 最大token数
        :return: AI回复内容
        """
        if not self.is_configured():
            return "❌ AI服务未配置。请在设置中添加DeepSeek API密钥。"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"API调用失败，状态码: {response.status_code}"
                try:
                    error_detail = response.json()
                    if "error" in error_detail:
                        error_msg += f"，错误信息: {error_detail['error'].get('message', '未知错误')}"
                except:
                    pass
                return f"❌ {error_msg}"
                
        except requests.exceptions.Timeout:
            return "❌ 请求超时，请检查网络连接或稍后重试。"
        except requests.exceptions.ConnectionError:
            return "❌ 网络连接错误，请检查网络设置。"
        except Exception as e:
            return f"❌ 发生错误: {str(e)}"
    
    def get_word_explanation(self, word: str, translation: str, pos: str = "") -> str:
        """获取单词解释。"""
        pos_text = f"，词性是{pos}" if pos else ""
        
        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的英语学习助手。请用简洁、友好的语言帮助用户学习英语单词。"
            },
            {
                "role": "user", 
                "content": f"请详细解释英语单词 '{word}'（中文含义：{translation}{pos_text}）的含义、用法和使用场景。"
            }
        ]
        
        return self.call_ai(messages)
    
    def get_memory_tips(self, word: str, translation: str, pos: str = "") -> str:
        """获取单词记忆技巧。"""
        pos_text = f"，词性是{pos}" if pos else ""
        
        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的英语学习助手，擅长提供单词记忆技巧。"
            },
            {
                "role": "user", 
                "content": f"请为英语单词 '{word}'（中文含义：{translation}{pos_text}）提供有效的记忆技巧，包括联想记忆、词根词缀、发音特点等方法。"
            }
        ]
        
        return self.call_ai(messages)
    
    def get_example_sentences(self, word: str, translation: str, pos: str = "") -> str:
        """获取例句。"""
        pos_text = f"，词性是{pos}" if pos else ""
        
        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的英语学习助手，擅长创建实用的例句。"
            },
            {
                "role": "user", 
                "content": f"请为英语单词 '{word}'（中文含义：{translation}{pos_text}）生成5个实用的例句，包含中文翻译，并尽量覆盖不同的使用场景。"
            }
        ]
        
        return self.call_ai(messages)
    
    def create_word_test(self, word: str, translation: str, pos: str = "") -> str:
        """创建单词测试。"""
        pos_text = f"，词性是{pos}" if pos else ""
        
        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的英语学习助手，擅长设计学习测试。"
            },
            {
                "role": "user", 
                "content": f"请为英语单词 '{word}'（中文含义：{translation}{pos_text}）设计一个小测试，包括词义选择、填空、造句等不同类型的题目。"
            }
        ]
        
        return self.call_ai(messages)
    
    def chat_with_context(self, user_message: str, word: str = "", translation: str = "", pos: str = "") -> str:
        """基于当前单词上下文的自由对话。"""
        system_content = "你是一个友好的英语学习助手，专注于帮助用户学习和记忆英语单词。"
        
        if word:
            pos_text = f"，词性是{pos}" if pos else ""
            context = f"当前用户正在学习单词 '{word}'（中文含义：{translation}{pos_text}）。"
            system_content += f" {context}"
        
        messages = [
            {
                "role": "system", 
                "content": system_content
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
        
        return self.call_ai(messages) 