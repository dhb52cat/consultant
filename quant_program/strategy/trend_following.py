# quant_program/strategy/trend_following.py
import pandas as pd
from typing import Dict, Any, Mapping
from .base import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        self.short_ma_period = int(self.params.get('SHORT_MA_PERIOD', 5))
        self.long_ma_period = int(self.params.get('LONG_MA_PERIOD', 20))

    def generate_signals(self, symbol: str, data: pd.DataFrame, indicators: Mapping[str, Any]) -> Dict[str, Any]:
        """
        趋势跟踪策略：
        当短期均线（SMA_short）上穿长期均线（SMA_long）时，生成买入信号。
        当短期均线（SMA_short）下穿长期均线（SMA_long）时，生成卖出信号。
        """
        if f'sma_{self.short_ma_period}' not in indicators or f'sma_{self.long_ma_period}' not in indicators:
            return {'action': 'hold', 'reason': 'Missing MA indicators'}

        short_ma = indicators[f'sma_{self.short_ma_period}']
        long_ma = indicators[f'sma_{self.long_ma_period}']

        if len(short_ma) < 2 or len(long_ma) < 2:
            return {'action': 'hold', 'reason': 'Insufficient data for MA crossover'}

        # 获取最新的两个均线值
        current_short_ma = short_ma.iloc[-1]
        prev_short_ma = short_ma.iloc[-2]
        current_long_ma = long_ma.iloc[-1]
        prev_long_ma = long_ma.iloc[-2]

        current_price = data['close'].iloc[-1]

        # 金叉：短期均线上穿长期均线
        if prev_short_ma <= prev_long_ma and current_short_ma > current_long_ma:
            if self.get_current_position(symbol) <= 0: # 避免重复买入
                return {'action': 'buy', 'price': current_price, 'quantity': 100, 'reason': 'Golden Cross'}
        # 死叉：短期均线下穿长期均线
        elif prev_short_ma >= prev_long_ma and current_short_ma < current_long_ma:
            if self.get_current_position(symbol) > 0: # 避免重复卖出或卖空
                return {'action': 'sell', 'price': current_price, 'quantity': self.get_current_position(symbol), 'reason': 'Dead Cross'}
        
        return {'action': 'hold', 'reason': 'No significant MA crossover'}
