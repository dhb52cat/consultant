# quant_program/strategy/base.py
import abc
import pandas as pd
from typing import Dict, Any, Mapping

class BaseStrategy(abc.ABC):
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.positions: Dict[str, float] = {} # 记录持仓情况，例如 {'000001.SZ': 100}

    @abc.abstractmethod
    def generate_signals(self, symbol: str, data: pd.DataFrame, indicators: Mapping[str, Any]) -> Dict[str, Any]:
        """
        根据数据和指标生成交易信号。
        :param symbol: 股票/指数代码
        :param data: 原始行情数据 DataFrame
        :param indicators: 计算好的指标，键为指标名称，值为 Series
        :return: 交易信号字典，例如 {'action': 'buy', 'price': 10.5, 'quantity': 100} 或 {'action': 'hold'}
        """
        pass

    def update_position(self, symbol: str, quantity: float):
        """更新策略内部的持仓记录"""
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        if abs(self.positions[symbol]) < 1e-6: # 如果持仓接近0，则清除
            del self.positions[symbol]

    def get_current_position(self, symbol: str) -> float:
        """获取当前指定股票的持仓量"""
        return self.positions.get(symbol, 0)

    def get_all_positions(self) -> Dict[str, float]:
        """获取所有持仓"""
        return self.positions
