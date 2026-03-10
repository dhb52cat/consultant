# quant_program/notifications/wecom_notifier.py
import requests
from configparser import ConfigParser
from .base import BaseNotifier

class WeComNotifier(BaseNotifier):
    def __init__(self, config_path: str = 'config/settings.ini'):
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_path)
        self.webhook_url = self.config['NOTIFICATIONS']['WECOM_WEBHOOK_URL']
        print(f"企业微信 Webhook URL: {self.webhook_url}")
        if not self.webhook_url:
            raise ValueError("WeCom Webhook URL not found in config/settings.ini")

    def send_message(self, title: str, content: str) -> bool:
        """
        通过企业微信群机器人发送 Markdown 格式消息。
        """
        print(f"发送企业微信通知: {title}")
        message = f"## {title}\n\n{content}"
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": message
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(self.webhook_url, json=data, headers=headers)
            response.raise_for_status() # 检查HTTP响应状态码
            result = response.json()
            if result.get('errcode') == 0:
                print(f"企业微信通知发送成功: {title}")
                return True
            else:
                print(f"企业微信通知发送失败: {result.get('errmsg', '未知错误')}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"发送企业微信通知时发生网络错误: {e}")
            return False
        except Exception as e:
            print(f"发送企业微信通知时发生未知错误: {e}")
            return False
