# quant_program/data_sources/akshare_source.py
import akshare as ak
import pandas as pd
import logging
from typing import List, Dict
from .base import BaseDataSource

logger = logging.getLogger(__name__)

class AkShareSource(BaseDataSource):
    """
    AkShare 数据源类，用于从 AkShare 获取 A 股行情数据。
    该类实现了 BaseDataSource 接口。
    """
    def __init__(self):
        logger.info("初始化 AkShare 数据源...")

    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取 A 股日线数据。增加随机延迟模仿人工。
        """
        import time
        import random
        time.sleep(random.uniform(1, 3)) # 模仿人工操作前的停顿
        
        code = symbol.split('.')[0]
        s_date = start_date.replace('-', '')
        e_date = end_date.replace('-', '')
        
        logger.debug(f"正在从 AkShare 获取 {symbol} 日线数据 ({s_date} 至 {e_date})...")
        
        try:
            df = ak.stock_zh_a_hist(
                symbol=code, 
                period="daily", 
                start_date=s_date, 
                end_date=e_date, 
                adjust="qfq"
            )
            
            if df is None or df.empty:
                logger.warning(f"AkShare 未能获取到 {symbol} 的日线数据。")
                return pd.DataFrame()
            
            # 统一列名映射
            df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            }, inplace=True)
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            logger.info(f"成功获取 {symbol} 日线数据，条数: {len(df)}")
            return df[['open', 'high', 'low', 'close', 'volume']].sort_index()
            
        except Exception as e:
            logger.error(f"从 AkShare 获取 {symbol} 日线数据时发生错误: {e}")
            return pd.DataFrame()

    def get_minute_data(self, symbol: str, trade_date: str, interval: str) -> pd.DataFrame:
        """
        获取 A 股分时 K 线数据。
        
        :param symbol: 股票代码
        :param trade_date: 交易日期
        :param interval: K 线周期，可选 '1', '5', '15', '30', '60' 等
        :return: 指定日期的分时 DataFrame
        """
        code = symbol.split('.')[0]
        period = interval.replace('min', '')
        
        logger.debug(f"正在从 AkShare 获取 {symbol} {interval} 分时数据...")
        
        try:
            df = ak.stock_zh_a_hist_min_em(symbol=code, period=period, adjust="qfq")
            
            if df is None or df.empty:
                logger.warning(f"AkShare 未能获取到 {symbol} 的分时数据。")
                return pd.DataFrame()

            df.rename(columns={
                '时间': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            }, inplace=True)
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 过滤指定日期的数据
            target_date = pd.to_datetime(trade_date).date()
            df = df[df.index.date == target_date]
            
            logger.info(f"成功获取 {symbol} {trade_date} 的分时数据，条数: {len(df)}")
            return df[['open', 'high', 'low', 'close', 'volume']].sort_index()
            
        except Exception as e:
            logger.error(f"从 AkShare 获取 {symbol} 分时数据时发生错误: {e}")
            return pd.DataFrame()

    def get_realtime_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        批量获取 A 股实时行情。
        
        :param symbols: 股票代码列表
        :return: 实时行情字典
        """
        logger.debug(f"正在从 AkShare 获取实时行情，股票列表: {symbols}")
        
        try:
            # 获取全量 A 股实时快照
            df = ak.stock_zh_a_spot_em()
            
            if df is None or df.empty:
                logger.warning("AkShare 未能获取到实时快照数据。")
                return {}
            
            quotes = {}
            codes = [s.split('.')[0] for s in symbols]
            
            # 过滤出需要的股票
            target_df = df[df['代码'].isin(codes)]
            
            for _, row in target_df.iterrows():
                code = row['代码']
                # 寻找原始输入的完整 symbol (带 .SZ/.SH)
                full_symbol = next((s for s in symbols if s.startswith(code)), code)
                
                quotes[full_symbol] = {
                    'price': float(row['最新价']),
                    'volume': float(row['成交量']),
                    'open': float(row['今开']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'prev_close': float(row['昨收']),
                    'time': row['最新交易时间'] if '最新交易时间' in row else ''
                }
            
            logger.debug(f"成功解析 {len(quotes)} 条实时行情。")
            return quotes
            
        except Exception as e:
            logger.error(f"从 AkShare 获取实时行情时发生错误: {e}")
            return {}
