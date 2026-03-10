# quant_program/core/main_executor.py
import sys
import os

# 修复导入路径问题：将项目根目录添加到 sys.path
# 这允许在 core/ 目录下直接运行脚本时，能正确找到 data_sources 等模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
import datetime
import logging
import random
from configparser import ConfigParser
import pandas as pd
from typing import Dict, Any

from data_sources.tushare_source import TushareSource
from data_sources.yfinance_source import YFinanceSource
from data_sources.akshare_source import AkShareSource
from indicators.ta_lib_indicators import calculate_macd, calculate_rsi, calculate_sma
from strategy.trend_following import TrendFollowingStrategy
from strategy.intraday_t0 import IntradayT0Strategy
from notifications.wxpusher_notifier import WxPusherNotifier
from notifications.wecom_notifier import WeComNotifier
from trading.mock_trader import MockTrader

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainExecutor:
    """
    量化交易主执行器。
    负责初始化各组件、加载历史数据、运行实时循环、调度指标计算、触发策略及执行交易。
    """
    def __init__(self, config_path: str = None):
        # 默认配置路径：项目根目录下的 config/settings.ini
        if config_path is None:
            config_path = os.path.join(project_root, 'config', 'settings.ini')
            
        logger.info(f"正在从 {config_path} 加载配置并初始化执行器...")
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_path)

        # 1. 初始化数据源 (A股 & 全球指数)
        a_share_type = self.config['DATA'].get('A_SHARE_SOURCE_TYPE', 'akshare').lower()
        if a_share_type == 'tushare':
            self.a_share_source = TushareSource(config_path)
            logger.info("使用 Tushare 作为 A 股数据源。")
        else:
            self.a_share_source = AkShareSource()
            logger.info("使用 AkShare 作为 A 股数据源。")
            
        self.yfinance_source = YFinanceSource()
        logger.info("使用 yfinance 作为全球指数数据源。")
        
        # 2. 初始化通知器
        notifier_type = self.config['NOTIFICATIONS'].get('NOTIFIER_TYPE', 'wxpusher').lower()
        if notifier_type == 'wecom':
            self.notifier = WeComNotifier(config_path)
            logger.info("已配置企业微信群机器人作为通知器。")
        elif notifier_type == 'wxpusher':
            self.notifier = WxPusherNotifier(config_path)
            logger.info("已配置 WxPusher 作为通知器。")
        else:
            logger.error(f"不支持的通知器类型: {notifier_type}")
            raise ValueError(f"Unsupported notifier type: {notifier_type}")

        # 3. 初始化交易执行器 (默认使用模拟交易)
        self.trader = MockTrader(config_path)

        # 4. 加载业务配置
        self.stock_symbols = [s.strip() for s in self.config['DATA']['STOCK_SYMBOLS'].split(',') if s.strip()]
        self.index_symbols = [s.strip() for s in self.config['DATA']['INDEX_SYMBOLS'].split(',') if s.strip()]
        self.data_interval = self.config['DATA']['DATA_INTERVAL']
        self.history_days = int(self.config['DATA']['HISTORY_DAYS'])
        
        logger.info(f"监控股票列表: {self.stock_symbols}")
        logger.info(f"监控指数列表: {self.index_symbols}")

        # 5. 初始化策略实例
        self.trend_following_params = dict(self.config.items('STRATEGY_PARAMS_TREND_FOLLOWING'))
        self.intraday_t0_params = dict(self.config.items('STRATEGY_PARAMS_INTRADAY_T0'))
        
        self.trend_strategy = TrendFollowingStrategy(self.trend_following_params)
        self.t0_strategy = IntradayT0Strategy(self.intraday_t0_params)
        logger.info("策略初始化完成。")

        self.market_data: Dict[str, pd.DataFrame] = {} # 内存数据库
        self.last_index_update = 0 # 上次指数更新时间

    def load_historical_data(self):
        """
        程序启动时的预加载步骤。
        获取过去 N 天的日线数据，用于初始化均线等滞后指标。
        """
        end_date = datetime.date.today().strftime('%Y-%m-%d')
        start_date = (datetime.date.today() - datetime.timedelta(days=self.history_days)).strftime('%Y-%m-%d')
        
        logger.info(f"--- 启动历史数据预加载 ({start_date} 至 {end_date}) ---")

        # 加载 A 股历史数据
        for symbol in self.stock_symbols:
            try:
                data = self.a_share_source.get_daily_data(symbol, start_date, end_date)
                if not data.empty:
                    self.market_data[symbol] = data
                    logger.info(f"已加载 {symbol} 历史数据: {len(data)} 条。")
                else:
                    logger.warning(f"{symbol} 历史数据为空。")
            except Exception as e:
                logger.error(f"加载 {symbol} 失败: {e}")

        # 加载全球指数历史数据
        for symbol in self.index_symbols:
            try:
                time.sleep(1) # 避免 yfinance 频率限制
                data = self.yfinance_source.get_daily_data(symbol, start_date, end_date)
                if not data.empty:
                    self.market_data[symbol] = data
                    logger.info(f"已加载指数 {symbol} 历史数据: {len(data)} 条。")
            except Exception as e:
                logger.error(f"加载指数 {symbol} 失败: {e}")

    def fetch_and_process_realtime_data(self):
        """
        核心循环逻辑：分级获取行情，降低频率
        """
        # 1. 获取 A 股实时行情 (每轮都获取)
        realtime_quotes = {}
        try:
            time.sleep(random.uniform(2, 5)) # 模拟人工观察延迟
            realtime_quotes = self.a_share_source.get_realtime_quotes(self.stock_symbols)
        except Exception as e:
            logger.error(f"获取 A 股行情失败: {e}")

        # 2. 获取全球指数行情 (降低频率：每 5 分钟更新一次)
        current_time = time.time()
        if current_time - self.last_index_update > 300: # 300秒 = 5分钟
            try:
                logger.info("正在更新全球指数行情...")
                time.sleep(random.uniform(3, 6))
                index_quotes = self.yfinance_source.get_realtime_quotes(self.index_symbols)
                if index_quotes:
                    realtime_quotes.update(index_quotes)
                    self.last_index_update = current_time
            except Exception as e:
                logger.error(f"获取指数行情失败: {e}")
        
        if not realtime_quotes:
            return

        all_symbols = list(realtime_quotes.keys())
        for symbol in all_symbols:
            quote = realtime_quotes[symbol]
            
            # 构造当前 Tick 的伪 K 线数据
            now = pd.to_datetime(datetime.datetime.now())
            latest_tick = pd.DataFrame([{
                'open': quote.get('open'),
                'high': quote.get('high'),
                'low': quote.get('low'),
                'close': quote.get('price'),
                'volume': quote.get('volume')
            }], index=[now])

            # 合并入本地数据集，保持窗口大小防止内存溢出
            if symbol in self.market_data:
                self.market_data[symbol] = pd.concat([self.market_data[symbol], latest_tick]).tail(1000) 
                self.market_data[symbol].drop_duplicates(inplace=True) 
            else:
                self.market_data[symbol] = latest_tick
                
                # 更新技术指标 (MACD, RSI, SMA)
                current_df = self.market_data.get(symbol)
                if current_df is not None and len(current_df) > 1:
                    short_period = int(self.trend_following_params.get('SHORT_MA_PERIOD', 5))
                    long_period = int(self.trend_following_params.get('LONG_MA_PERIOD', 20))
                    
                    # 重新计算该标的的指标列
                    current_df = calculate_sma(current_df, short_period)
                    current_df = calculate_sma(current_df, long_period)
                    current_df = calculate_macd(current_df)
                    current_df = calculate_rsi(current_df)
                    self.market_data[symbol] = current_df
                
                    # 准备指标字典供策略使用
                    latest_indicators = {
                        col: current_df[col] 
                        for col in current_df.columns 
                        if col not in ['open', 'high', 'low', 'close', 'volume']
                    }
                    
                    # 触发策略 A: 趋势跟踪
                    trend_sig = self.trend_strategy.generate_signals(symbol, current_df, latest_indicators)
                    self.execute_signal(symbol, trend_sig, "趋势跟踪")

                    # 触发策略 B: 盘中做T
                    t0_sig = self.t0_strategy.generate_signals(symbol, current_df, latest_indicators)
                    self.execute_signal(symbol, t0_sig, "盘中做T")


    def execute_signal(self, symbol: str, signal: Dict[str, Any], strategy_name: str):
        """
        信号执行中心。
        将策略生成的逻辑信号转化为真实的交易指令并推送通知。
        """
        action = signal.get('action')
        if action == 'hold':
            return # 无操作，跳过

        reason = signal.get('reason', '')
        current_price = signal.get('price')

        if action in ['buy', 'sell'] and current_price is not None:
            quantity_val = signal.get('quantity')
            if quantity_val is None:
                return

            quantity = int(quantity_val)
            # 执行下单 (模拟环境)
            order_info = self.trader.place_order(symbol, action, float(current_price), quantity)
            
            if order_info.get('status') == 'filled':
                # 构造消息标题和内容
                title = f"💡 策略触发: {strategy_name}"
                content = (f"标的代码: {symbol}\n"
                           f"操作类型: {'🔴 买入' if action == 'buy' else '🟢 卖出'}\n"
                           f"成交价格: {current_price:.2f}\n"
                           f"成交数量: {quantity}\n"
                           f"触发原因: {reason}\n"
                           f"系统时间: {datetime.datetime.now().strftime('%H:%M:%S')}")
                
                # 发送远程推送
                self.notifier.send_message(title, content)
                logger.info(f"信号已处理并发送通知: {symbol} -> {action}")
                
                # 同步更新策略内部的持仓计数
                delta = float(quantity) if action == 'buy' else -float(quantity)
                self.trend_strategy.update_position(symbol, delta)
                self.t0_strategy.update_position(symbol, delta)
            else:
                logger.error(f"下单失败! 标的: {symbol}, 状态: {order_info.get('status')}")

    def run(self):
        """启动主循环"""
        logger.info("========================================")
        logger.info("   量化交易系统启动 (实时监控模式)      ")
        logger.info("========================================")
        
        self.load_historical_data() 

        try:
            while True:
                try:
                    self.fetch_and_process_realtime_data()
                    # 显著降低频率：每 2-3 分钟轮询一次
                    wait_time = random.uniform(120, 180)
                    logger.debug(f"等待 {wait_time:.2f} 秒后进行下一次轮询...")
                    time.sleep(wait_time) 
                except KeyboardInterrupt:
                    logger.info("接收到停止指令，程序正在安全退出...")
                    break
                except Exception as e:
                    logger.error(f"循环内发生错误: {e}", exc_info=True)
                    time.sleep(10) # 发生错误时稍作等待
        except Exception as e:
            logger.critical(f"程序运行发生致命错误: {e}", exc_info=True)

if __name__ == '__main__':
    executor = MainExecutor()
    executor.run()
