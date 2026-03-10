# quant_program/tests/test_trading.py
import pytest
from trading.mock_trader import MockTrader

@pytest.fixture
def mock_config(tmp_path):
    config_file = tmp_path / "settings.ini"
    config_file.write_text("""
[TRADING]
MOCK_INITIAL_CASH = 100000
MOCK_COMMISSION_RATE = 0.0003
""")
    return str(config_file)

def test_mock_trader_buy_sell(mock_config):
    trader = MockTrader(mock_config)
    
    # Test Buy
    order = trader.place_order('000001.SZ', 'buy', 10.0, 100)
    assert order['status'] == 'filled'
    assert trader.cash < 100000
    assert trader.get_positions()['000001.SZ']['quantity'] == 100
    
    # Test Sell
    order = trader.place_order('000001.SZ', 'sell', 11.0, 50)
    assert order['status'] == 'filled'
    assert trader.get_positions()['000001.SZ']['quantity'] == 50
    
    # Test insufficient funds
    order = trader.place_order('600000.SH', 'buy', 1000000, 1)
    assert order['status'] == 'rejected'
