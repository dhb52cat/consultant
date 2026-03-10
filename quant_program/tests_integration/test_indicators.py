import sys
import os
import unittest
import pandas as pd
import datetime

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from data_sources.akshare_source import AkShareSource
from indicators.ta_lib_indicators import calculate_macd, calculate_rsi, calculate_sma

class TestIndicatorsIntegration(unittest.TestCase):
    def setUp(self):
        self.ak_source = AkShareSource()
        # 加载30天历史数据以确保指标有足够的历史值
        self.end_date = datetime.date.today().strftime('%Y-%m-%d')
        self.start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        self.symbol = "300308.SZ"
        self.df = self.ak_source.get_daily_data(self.symbol, self.start_date, self.end_date)

    def test_sma_calculation(self):
        """测试 SMA 指标计算 (非 Mock)"""
        if self.df.empty:
            self.skipTest("Data source empty")
        
        df_sma = calculate_sma(self.df.copy(), timeperiod=5)
        self.assertIn('sma_5', df_sma.columns)
        # 检查是否生成了非空值（SMA前面会有NaN）
        self.assertTrue(df_sma['sma_5'].notna().any())
        print(f"\nSMA(5) results for {self.symbol}:\n{df_sma[['close', 'sma_5']].tail()}")

    def test_macd_calculation(self):
        """测试 MACD 指标计算 (非 Mock)"""
        if self.df.empty:
            self.skipTest("Data source empty")
            
        df_macd = calculate_macd(self.df.copy())
        self.assertTrue(all(col in df_macd.columns for col in ['macd', 'macdsignal', 'macdhist']))
        self.assertTrue(df_macd['macd'].notna().any())
        print(f"\nMACD results for {self.symbol}:\n{df_macd[['close', 'macd', 'macdsignal', 'macdhist']].tail()}")

    def test_rsi_calculation(self):
        """测试 RSI 指标计算 (非 Mock)"""
        if self.df.empty:
            self.skipTest("Data source empty")
            
        df_rsi = calculate_rsi(self.df.copy(), timeperiod=14)
        self.assertIn('rsi', df_rsi.columns)
        self.assertTrue(df_rsi['rsi'].notna().any())
        print(f"\nRSI results for {self.symbol}:\n{df_rsi[['close', 'rsi']].tail()}")

if __name__ == '__main__':
    unittest.main()
