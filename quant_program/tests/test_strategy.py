# quant_program/tests/test_strategy.py
import pandas as pd
import pytest
from strategy.trend_following import TrendFollowingStrategy
from strategy.intraday_t0 import IntradayT0Strategy

@pytest.fixture
def strategy_data():
    dates = pd.date_range('2023-01-01', periods=50)
    data = pd.DataFrame({
        'close': [10.0 + i * 0.1 for i in range(50)], # Up trend
        'open': [10.0 + i * 0.1 for i in range(50)],
        'high': [10.5 + i * 0.1 for i in range(50)],
        'low': [9.5 + i * 0.1 for i in range(50)],
        'volume': [1000] * 50
    }, index=dates)
    return data

def test_trend_following_signal(strategy_data):
    params = {'SHORT_MA_PERIOD': 5, 'LONG_MA_PERIOD': 20}
    strategy = TrendFollowingStrategy(params)
    
    # Mock indicators
    indicators = {
        'sma_5': strategy_data['close'].rolling(5).mean(),
        'sma_20': strategy_data['close'].rolling(20).mean()
    }
    
    # For trend following, we need a crossover. 
    # Our sample data is always up, so sma_5 > sma_20 eventually.
    # We test the signal generation at the end.
    signal = strategy.generate_signals('TEST', strategy_data, indicators)
    assert 'action' in signal

def test_intraday_t0_signal(strategy_data):
    params = {'T0_THRESHOLD': 0.001}
    strategy = IntradayT0Strategy(params)
    strategy.update_position('TEST', 100) # Give it some base position
    
    indicators = {} # T0 doesn't use indicators in our current implementation
    
    # Modify last price to trigger a sell (price up)
    strategy_data.loc[strategy_data.index[-1], 'close'] = strategy_data.loc[strategy_data.index[-1], 'open'] * 1.05
    
    signal = strategy.generate_signals('TEST', strategy_data, indicators)
    assert signal['action'] == 'sell'
