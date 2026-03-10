# quant_program/tests/test_indicators.py
import pandas as pd
import numpy as np
import pytest
from indicators.ta_lib_indicators import calculate_macd, calculate_rsi, calculate_sma

@pytest.fixture
def sample_data():
    dates = pd.date_range('2023-01-01', periods=100)
    data = pd.DataFrame({
        'close': np.random.uniform(10, 20, size=100),
        'open': np.random.uniform(10, 20, size=100),
        'high': np.random.uniform(10, 20, size=100),
        'low': np.random.uniform(10, 20, size=100),
        'volume': np.random.uniform(1000, 5000, size=100)
    }, index=dates)
    return data

def test_calculate_sma(sample_data):
    period = 10
    df = calculate_sma(sample_data.copy(), timeperiod=period)
    assert f'sma_{period}' in df.columns
    assert not df[f'sma_{period}'].dropna().empty

def test_calculate_macd(sample_data):
    df = calculate_macd(sample_data.copy())
    assert 'macd' in df.columns
    assert 'macdsignal' in df.columns
    assert 'macdhist' in df.columns

def test_calculate_rsi(sample_data):
    df = calculate_rsi(sample_data.copy())
    assert 'rsi' in df.columns
