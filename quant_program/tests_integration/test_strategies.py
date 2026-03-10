import sys
import os
import unittest
import pandas as pd
import datetime

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from data_sources.akshare_source import AkShareSource
from indicators.ta_lib_indicators import calculate_sma
from strategy.trend_following import TrendFollowingStrategy
from strategy.intraday_t0 import IntradayT0Strategy

class TestStrategiesIntegration(unittest.TestCase):
    def setUp(self):
        self.ak_source = AkShareSource()
        # 加载历史数据
        self.end_date = datetime.date.today().strftime('%Y-%m-%d')
        self.start_date = (datetime.date.today() - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
        self.symbol = "300308.SZ"
        self.df = self.ak_source.get_daily_data(self.symbol, self.start_date, self.end_date)
        
        # 预计算指标
        self.df = calculate_sma(self.df.copy(), 5)
        self.df = calculate_sma(self.df, 20)
        
        # 准备 indicators 字典 (模拟 main_executor.py 的行为)
        self.indicators = {
            'sma_5': self.df['sma_5'],
            'sma_20': self.df['sma_20']
        }

    def test_trend_following_signal(self):
        """测试趋势跟踪策略逻辑 (使用真实数据)"""
        if self.df.empty:
            self.skipTest("Data source empty")

        strategy = TrendFollowingStrategy({'SHORT_MA_PERIOD': 5, 'LONG_MA_PERIOD': 20})
        # 我们可以传入不同的历史片段来模拟不同时期的信号
        signal = strategy.generate_signals(self.symbol, self.df, self.indicators)
        print(f"\nTrend Following Signal for {self.symbol}: {signal}")
        self.assertIsInstance(signal, dict)
        self.assertIn('action', signal)
        self.assertIn('reason', signal)

    def test_intraday_t0_signal(self):
        """测试日内 T0 策略逻辑 (使用真实数据)"""
        if self.df.empty:
            self.skipTest("Data source empty")

        strategy = IntradayT0Strategy({'T0_THRESHOLD': 0.005})
        # 模拟有底仓
        strategy.positions[self.symbol] = {'quantity': 1000, 'cost_price': self.df['close'].iloc[0]}
        
        signal = strategy.generate_signals(self.symbol, self.df, self.indicators)
        print(f"\nIntraday T0 Signal for {self.symbol}: {signal}")
        self.assertIsInstance(signal, dict)
        self.assertIn('action', signal)

if __name__ == '__main__':
    unittest.main()
