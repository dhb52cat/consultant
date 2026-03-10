# quant_program/notifications/wxpusher_notifier.py
import requests
from configparser import ConfigParser
from typing import List
from .base import BaseNotifier

class WxPusherNotifier(BaseNotifier):
    def __init__(self, config_path: str = 'config/settings.ini'):
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_path)
        self.app_token = self.config['NOTIFICATIONS']['WXPUSHER_APP_TOKEN']
        self.uids = [uid.strip() for uid in self.config['NOTIFICATIONS']['WXPUSHER_UIDS'].split(',') if uid.strip()]

        if not self.app_token:
            raise ValueError("WxPusher APP_TOKEN not found in config/settings.ini")
        if not self.uids:
            raise ValueError("WxPusher UIDs not found in config/settings.ini")

        self.url = "http://wxpusher.zjiecode.com/api/send/message"

    def send_message(self, title: str, content: str) -> bool:
        """
        通过 WxPusher 发送微信消息。
        """
        data = {
            "appToken": self.app_token,
            "content": f"## {title}\n\n{content}", # Markdown 格式
            "summary": title, # 消息摘要
            "contentType": 2, # 1表示文字，2表示html(支持md)，3表示url
            "uids": self.uids
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(self.url, json=data, headers=headers)
            response.raise_for_status() # 检查HTTP响应状态码
            result = response.json()
            if result.get('code') == 1000:
                print(f"WxPusher通知发送成功: {title}")
                return True
            else:
                print(f"WxPusher通知发送失败: {result.get('msg', '未知错误')}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"发送WxPusher通知时发生网络错误: {e}")
            return False
        except Exception as e:
            print(f"发送WxPusher通知时发生未知错误: {e}")
            return False
