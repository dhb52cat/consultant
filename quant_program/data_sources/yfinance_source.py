# quant_program/data_sources/yfinance_source.py
import yfinance as yf
import pandas as pd
import logging
import time
from typing import List, Dict
from .base import BaseDataSource

logger = logging.getLogger(__name__)

class YFinanceSource(BaseDataSource):
    def __init__(self):
        pass # yfinance 不需要API Key

    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从 yfinance 获取指定指数的日线数据。
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if df is None or df.empty:
                logger.warning(f"yfinance 未能获取到 {symbol} 的历史数据。")
                return pd.DataFrame()
            
            # 统一列名映射
            mapping = {
                'Open': 'open', 
                'High': 'high', 
                'Low': 'low', 
                'Close': 'close', 
                'Volume': 'volume'
            }
            # 检查哪些列存在
            df.rename(columns={k: v for k, v in mapping.items() if k in df.columns}, inplace=True)
            
            # 确保返回标准列
            target_cols = ['open', 'high', 'low', 'close', 'volume']
            available_cols = [c for c in target_cols if c in df.columns]
            
            return df[available_cols].sort_index()
        except Exception as e:
            logger.error(f"从 yfinance 获取 {symbol} 历史数据时发生错误: {e}")
            return pd.DataFrame()

    def get_minute_data(self, symbol: str, trade_date: str, interval: str) -> pd.DataFrame:
        """
        从 yfinance 获取指定指数的分时数据。
        """
        start_datetime = pd.to_datetime(trade_date)
        if pd.isna(start_datetime):
            return pd.DataFrame()
        end_datetime = start_datetime + pd.Timedelta(days=1) - pd.Timedelta(minutes=1)

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_datetime.strftime('%Y-%m-%d'), end=end_datetime.strftime('%Y-%m-%d'), interval=interval)
        if df is None or df.empty:
            return pd.DataFrame()
        df.rename(columns={
            'Open': 'open', 
            'High': 'high', 
            'Low': 'low', 
            'Close': 'close', 
            'Volume': 'volume'
        }, inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']].sort_index()

    def get_realtime_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        从 yfinance 获取实时行情（通常有延迟）。
        yfinance 的实时数据也是通过历史数据接口模拟的最新价。
        """
        quotes = {}
        data = yf.download(symbols, period="1d", interval="1m") # 获取最近一分钟数据
        if data is None or data.empty:
            return quotes
        
        for symbol in symbols:
            if symbol in data['Close'].columns:
                latest_close = data['Close'][symbol].iloc[-1]
                latest_volume = data['Volume'][symbol].iloc[-1]
                latest_open = data['Open'][symbol].iloc[-1]
                latest_high = data['High'][symbol].iloc[-1]
                latest_low = data['Low'][symbol].iloc[-1]
                quotes[symbol] = {
                    'price': float(latest_close),
                    'volume': float(latest_volume),
                    'open': float(latest_open),
                    'high': float(latest_high),
                    'low': float(latest_low),
                    'time': data['Close'][symbol].index[-1].strftime('%H:%M:%S')
                }
        return quotes
