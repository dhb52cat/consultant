# quant_program/trading/base.py
import abc
from typing import Dict, Any

class BaseTrader(abc.ABC):
    @abc.abstractmethod
    def place_order(self, symbol: str, order_type: str, price: float, quantity: int) -> Dict[str, Any]:
        """
        下单操作。
        :param symbol: 股票代码
        :param order_type: 订单类型（'buy', 'sell'）
        :param price: 交易价格（市价单可忽略）
        :param quantity: 交易数量
        :return: 包含订单ID、状态等信息的字典
        """
        pass

    @abc.abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单。
        :param order_id: 订单ID
        :return: 布尔值，表示是否取消成功
        """
        pass

    @abc.abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账户信息（可用资金、总资产等）。
        :return: 包含账户信息的字典
        """
        pass

    @abc.abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """
        获取当前持仓信息。
        :return: 字典，键为股票代码，值为包含持仓量、成本等信息的字典
        """
        pass

    @abc.abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        查询订单状态。
        :param order_id: 订单ID
        :return: 包含订单状态的字典
        """
        pass
