# quant_program/notifications/serverchan_notifier.py
import requests
from configparser import ConfigParser
from .base import BaseNotifier

class ServerChanNotifier(BaseNotifier):
    def __init__(self, config_path: str = 'config/settings.ini'):
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_path)
        self.sckey = self.config['API_KEYS']['SERVERCHAN_SCKEY']
        if not self.sckey:
            raise ValueError("Server酱 SCKEY not found in config/settings.ini")
        self.url = f"https://sctapi.ftqq.com/{self.sckey}.send"

    def send_message(self, title: str, content: str) -> bool:
        """
        通过 Server酱 发送微信消息。
        """
        data = {
            "title": title,
            "desp": content
        }
        try:
            response = requests.post(self.url, data=data)
            response.raise_for_status() # 检查HTTP响应状态码
            result = response.json()
            if result.get('code') == 0:
                print(f"Server酱通知发送成功: {title}")
                return True
            else:
                print(f"Server酱通知发送失败: {result.get('message', '未知错误')}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"发送Server酱通知时发生网络错误: {e}")
            return False
        except Exception as e:
            print(f"发送Server酱通知时发生未知错误: {e}")
            return False
