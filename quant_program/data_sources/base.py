# quant_program/data_sources/base.py
import abc
import pandas as pd
from typing import List, Dict

class BaseDataSource(abc.ABC):
    @abc.abstractmethod
    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指定股票/指数的日线数据。
        :param symbol: 股票/指数代码
        :param start_date: 开始日期 (YYYYMMDD 或 YYYY-MM-DD)
        :param end_date: 结束日期 (YYYYMMDD 或 YYYY-MM-DD)
        :return: 包含 ['open', 'high', 'low', 'close', 'vol'] 的 DataFrame
        """
        pass

    @abc.abstractmethod
    def get_minute_data(self, symbol: str, trade_date: str, interval: str) -> pd.DataFrame:
        """
        获取指定股票/指数在某交易日的指定频率分时数据。
        :param symbol: 股票/指数代码
        :param trade_date: 交易日期 (YYYYMMDD 或 YYYY-MM-DD)
        :param interval: 分时频率 (例如 '1min', '5min')
        :return: 包含 ['open', 'high', 'low', 'close', 'vol'] 的 DataFrame，索引为时间戳
        """
        pass

    @abc.abstractmethod
    def get_realtime_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        获取指定股票/指数的实时行情。
        :param symbols: 股票/指数代码列表
        :return: 字典，键为股票代码，值为包含实时行情的字典 (例如 {'price': 10.5, 'volume': 1000})
        """
        pass
