# quant_program/tests/test_data_sources.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from data_sources.akshare_source import AkShareSource
from data_sources.yfinance_source import YFinanceSource

def test_akshare_source_daily():
    with patch('akshare.stock_zh_a_hist') as mock_hist:
        mock_df = pd.DataFrame({
            '日期': ['2023-01-01'],
            '开盘': [10.0], '最高': [11.0], '最低': [9.0], '收盘': [10.5], '成交量': [1000]
        })
        mock_hist.return_value = mock_df
        
        source = AkShareSource()
        df = source.get_daily_data('000001.SZ', '20230101', '20230101')
        
        assert not df.empty
        assert 'close' in df.columns
        assert df.iloc[0]['close'] == 10.5

def test_yfinance_source_daily():
    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = mock_ticker.return_value
        mock_df = pd.DataFrame({
            'Open': [10.0], 'High': [11.0], 'Low': [9.0], 'Close': [10.5], 'Volume': [1000]
        }, index=pd.to_datetime(['2023-01-01']))
        mock_instance.history.return_value = mock_df
        
        source = YFinanceSource()
        df = source.get_daily_data('^GSPC', '2023-01-01', '2023-01-02')
        
        assert not df.empty
        assert 'close' in df.columns
        assert df.iloc[0]['close'] == 10.5
