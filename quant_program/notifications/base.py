# quant_program/notifications/base.py
import abc

class BaseNotifier(abc.ABC):
    @abc.abstractmethod
    def send_message(self, title: str, content: str) -> bool:
        """
        发送通知消息。
        :param title: 消息标题
        :param content: 消息内容
        :return: 布尔值，表示是否发送成功
        """
        pass
