import sys
import os
import unittest
import pandas as pd
import datetime

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from data_sources.akshare_source import AkShareSource
from data_sources.yfinance_source import YFinanceSource

class TestDataSourcesIntegration(unittest.TestCase):
    def setUp(self):
        self.ak_source = AkShareSource()
        self.yf_source = YFinanceSource()
        self.end_date = datetime.date.today().strftime('%Y-%m-%d')
        self.start_date = (datetime.date.today() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')

    def test_akshare_daily_data(self):
        """测试 AkShare 获取 A 股日线数据 (真实调用)"""
        symbol = "300308.SZ"
        df = self.ak_source.get_daily_data(symbol, self.start_date, self.end_date)
        print(f"\nAkShare Daily Data for {symbol}:\n{df.head()}")
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            self.assertTrue(all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']))

    def test_yfinance_daily_data(self):
        """测试 yfinance 获取指数日线数据 (真实调用)"""
        symbol = "^GSPC"
        df = self.yf_source.get_daily_data(symbol, self.start_date, self.end_date)
        print(f"\nyfinance Daily Data for {symbol}:\n{df.head()}")
        self.assertIsInstance(df, pd.DataFrame)
        if not df.empty:
            self.assertTrue(all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']))

    def test_akshare_realtime_quotes(self):
        """测试 AkShare 获取实时行情 (真实调用)"""
        symbols = ["300308.SZ"]
        quotes = self.ak_source.get_realtime_quotes(symbols)
        print(f"\nAkShare Realtime Quotes: {quotes}")
        self.assertIsInstance(quotes, dict)
        if symbols[0] in quotes:
            self.assertIn('price', quotes[symbols[0]])

    def test_yfinance_realtime_quotes(self):
        """测试 yfinance 获取实时行情 (真实调用)"""
        symbols = ["^GSPC", "^IXIC"]
        quotes = self.yf_source.get_realtime_quotes(symbols)
        print(f"\nyfinance Realtime Quotes: {quotes}")
        self.assertIsInstance(quotes, dict)
        for s in symbols:
            if s in quotes:
                self.assertIn('price', quotes[s])

if __name__ == '__main__':
    unittest.main()
