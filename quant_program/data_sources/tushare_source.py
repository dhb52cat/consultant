# quant_program/data_sources/tushare_source.py
import tushare as ts
import pandas as pd
from typing import List, Dict
from configparser import ConfigParser
from .base import BaseDataSource
import os

class TushareSource(BaseDataSource):
    def __init__(self, config_path: str = 'config/settings.ini'):
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_path)
        self.token = self.config['API_KEYS']['TUSHARE_PRO_TOKEN']
        if not self.token:
            raise ValueError("Tushare Pro Token not found in config/settings.ini")
        ts.set_token(self.token)
        self.pro = ts.pro_api()

    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从 Tushare Pro 获取指定股票的日线数据。
        注意：Tushare 的日期格式通常是 YYYYMMDD
        """
        df = self.pro.daily(ts_code=symbol, start_date=start_date.replace('-', ''), end_date=end_date.replace('-', ''))
        if df is None or df.empty:
            return pd.DataFrame()
        df.rename(columns={'trade_date': 'date', 'vol': 'volume'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']].sort_index()

    def get_minute_data(self, symbol: str, trade_date: str, interval: str) -> pd.DataFrame:
        """
        从 Tushare Pro 获取指定股票的分时数据。
        Tushare 分时数据通常是 1min, 5min, 15min, 30min, 60min
        免费用户可能需要积分获取高频数据，或有调用限制。
        """
        # Tushare 的 bar 接口可能需要特定权限或积分
        # 这里假设可以获取，实际需要根据您的Tushare权限调整
        df = ts.get_k_data(symbol.split('.')[0], ktype=interval.replace('min', ''), autype='qfq', start=trade_date, end=trade_date)
        if df is None or df.empty:
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['date'] + ' ' + df['time']) # 假设可以获取到时间
        df.set_index('date', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']].sort_index()

    def get_realtime_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        从 Tushare Pro 获取实时行情（通常有延迟）。
        Tushare 实时行情可能需要高级接口。
        这里使用最简单的获取方式，可能包含延迟。
        """
        quotes = {}
        for symbol in symbols:
            df = ts.get_realtime_quotes(symbol.split('.')[0]) # tushare get_realtime_quotes接受的是纯代码
            if df is not None and not df.empty:
                quotes[symbol] = {
                    'price': float(df['price'].iloc[0]),
                    'volume': float(df['volume'].iloc[0]),
                    'open': float(df['open'].iloc[0]),
                    'high': float(df['high'].iloc[0]),
                    'low': float(df['low'].iloc[0]),
                    'prev_close': float(df['pre_close'].iloc[0]),
                    'time': df['time'].iloc[0]
                }
        return quotes
