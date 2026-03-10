# quant_program/indicators/ta_lib_indicators.py
import pandas as pd
import numpy as np
# 尝试导入 ta-lib，如果失败则使用 pandas_ta 或自行实现
try:
    import talib
except ImportError:
    print("TA-Lib not installed. Using pandas_ta for indicators.")
    import pandas_ta as ta

def calculate_macd(df: pd.DataFrame, fastperiod=12, slowperiod=26, signalperiod=9) -> pd.DataFrame:
    """计算 MACD 指标"""
    if 'talib' in globals():
        macd, macdsignal, macdhist = talib.MACD(df['close'],
                                                fastperiod=fastperiod,
                                                slowperiod=slowperiod,
                                                signalperiod=signalperiod)
        df['macd'] = macd
        df['macdsignal'] = macdsignal
        df['macdhist'] = macdhist
    else:
        df.ta.macd(close='close', fast=fastperiod, slow=slowperiod, signal=signalperiod, append=True)
        df.rename(columns={
            f'MACD_{fastperiod}_{slowperiod}_{signalperiod}': 'macd',
            f'MACDH_{fastperiod}_{slowperiod}_{signalperiod}': 'macdhist',
            f'MACDS_{fastperiod}_{slowperiod}_{signalperiod}': 'macdsignal'
        }, inplace=True)
    return df

def calculate_rsi(df: pd.DataFrame, timeperiod=14) -> pd.DataFrame:
    """计算 RSI 指标"""
    if 'talib' in globals():
        df['rsi'] = talib.RSI(df['close'], timeperiod=timeperiod)
    else:
        df.ta.rsi(close='close', length=timeperiod, append=True)
        df.rename(columns={f'RSI_{timeperiod}': 'rsi'}, inplace=True)
    return df

def calculate_sma(df: pd.DataFrame, timeperiod=10) -> pd.DataFrame:
    """计算简单移动平均线 (SMA)"""
    if 'talib' in globals():
        df[f'sma_{timeperiod}'] = talib.SMA(df['close'], timeperiod=timeperiod)
    else:
        df.ta.sma(close='close', length=timeperiod, append=True)
        df.rename(columns={f'SMA_{timeperiod}': f'sma_{timeperiod}'}, inplace=True)
    return df

# 可以继续添加其他常用指标，例如 Bollinger Bands, KDJ, MA 等
# ...
