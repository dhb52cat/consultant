# quant_program/strategy/intraday_t0.py
import pandas as pd
from typing import Dict, Any, Mapping
from .base import BaseStrategy

class IntradayT0Strategy(BaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        self.t0_threshold = float(self.params.get('T0_THRESHOLD', 0.005)) # 0.5% 波动
        self.base_position: Dict[str, float] = {} # 记录做T的基准持仓

    def generate_signals(self, symbol: str, data: pd.DataFrame, indicators: Mapping[str, Any]) -> Dict[str, Any]:
        """
        盘中做T策略：
        在有底仓的情况下，当股价在盘中达到一定跌幅时买入，在一定涨幅时卖出。
        简化版本：基于日内价格波动。
        """
        if data.empty or len(data) < 2:
            return {'action': 'hold', 'reason': 'Insufficient data for T0'}

        current_price = data['close'].iloc[-1]
        
        # 假设我们有底仓（这里简化为如果当前持仓>0）
        current_position = self.get_current_position(symbol)

        if current_position == 0:
            # 如果没有底仓，不做T，可以考虑在这里添加建仓逻辑
            return {'action': 'hold', 'reason': 'No base position for T0'}

        # 计算日内涨跌幅（相对于今日开盘价）
        open_price = data['open'].iloc[0] # 今日开盘价
        if open_price == 0: # 避免除零
             return {'action': 'hold', 'reason': 'Open price is zero'}

        intraday_change = (current_price - open_price) / open_price

        # 如果价格跌破阈值，且当前持仓足够做T（可买入更多）
        if intraday_change < -self.t0_threshold:
            # 假设每次做T买入100股
            buy_quantity = 100
            return {'action': 'buy', 'price': current_price, 'quantity': buy_quantity, 'reason': f'Intraday T0 Buy: Price down {intraday_change:.2%}'}
        
        # 如果价格涨超阈值，且当前持仓足够做T（可卖出部分）
        elif intraday_change > self.t0_threshold:
            # 假设每次做T卖出100股，但不能超过当前持仓
            sell_quantity = min(100, current_position)
            if sell_quantity > 0:
                return {'action': 'sell', 'price': current_price, 'quantity': sell_quantity, 'reason': f'Intraday T0 Sell: Price up {intraday_change:.2%}'}
        
        return {'action': 'hold', 'reason': 'No T0 signal'}
