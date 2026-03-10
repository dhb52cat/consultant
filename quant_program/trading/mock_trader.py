# quant_program/trading/mock_trader.py
import uuid
import time
import logging
from typing import Dict, Any
from configparser import ConfigParser
from .base import BaseTrader

logger = logging.getLogger(__name__)

class MockTrader(BaseTrader):
    """
    模拟交易执行器，用于在不连接真实券商的情况下测试策略。
    它维护一个虚拟的账户余额、持仓和订单历史。
    """
    def __init__(self, config_path: str = 'config/settings.ini'):
        self.config = ConfigParser(interpolation=None)
        self.config.read(config_path)
        
        # 加载交易配置
        try:
            self.initial_cash = float(self.config['TRADING']['MOCK_INITIAL_CASH'])
            self.commission_rate = float(self.config['TRADING']['MOCK_COMMISSION_RATE'])
            logger.info(f"初始化模拟交易器：初始资金={self.initial_cash}, 佣金率={self.commission_rate}")
        except KeyError as e:
            logger.error(f"配置文件缺失交易参数: {e}")
            self.initial_cash = 100000.0
            self.commission_rate = 0.0003

        self.cash = self.initial_cash
        self.positions: Dict[str, Dict[str, Any]] = {} # 格式: {'symbol': {'quantity': 100, 'cost_price': 10.0}}
        self.orders: Dict[str, Dict[str, Any]] = {} # 存储订单记录

    def place_order(self, symbol: str, order_type: str, price: float, quantity: int) -> Dict[str, Any]:
        """
        模拟下单。该方法会立即计算盈亏并更新持仓。
        
        :param symbol: 证券代码
        :param order_type: 'buy' 或 'sell'
        :param price: 成交价格
        :param quantity: 成交数量
        :return: 包含订单执行信息的字典
        """
        order_id = str(uuid.uuid4())
        timestamp = time.time()
        status = 'filled' # 模拟模式下单即成交

        cost = price * quantity
        commission = cost * self.commission_rate
        total_outlay = cost + commission

        logger.info(f"执行模拟订单: {order_type.upper()} {symbol}, 数量: {quantity}, 价格: {price:.2f}")

        if order_type == 'buy':
            if self.cash >= total_outlay:
                self.cash -= total_outlay
                
                # 更新持仓 logic: 加权平均成本
                if symbol not in self.positions:
                    self.positions[symbol] = {'quantity': 0, 'cost_price': 0.0}
                
                curr_pos = self.positions[symbol]
                new_quantity = curr_pos['quantity'] + quantity
                total_cost = (curr_pos['quantity'] * curr_pos['cost_price']) + cost
                
                curr_pos['quantity'] = new_quantity
                curr_pos['cost_price'] = total_cost / new_quantity if new_quantity > 0 else 0.0

                logger.info(f"买入成功。余额: {self.cash:.2f}, 当前持仓: {new_quantity}")
            else:
                status = 'rejected'
                logger.warning(f"买入失败: 资金不足。所需: {total_outlay:.2f}, 现有: {self.cash:.2f}")
        
        elif order_type == 'sell':
            if symbol in self.positions and self.positions[symbol]['quantity'] >= quantity:
                revenue = cost - commission
                self.cash += revenue
                
                self.positions[symbol]['quantity'] -= quantity
                if self.positions[symbol]['quantity'] <= 0:
                    del self.positions[symbol]
                    
                logger.info(f"卖出成功。余额: {self.cash:.2f}, 剩余持仓: {self.positions.get(symbol, {'quantity':0})['quantity']}")
            else:
                status = 'rejected'
                logger.warning(f"卖出失败: 持仓不足。请求: {quantity}, 现有: {self.positions.get(symbol, {'quantity':0})['quantity']}")
        
        else:
            status = 'rejected'
            logger.error(f"不支持的订单类型: {order_type}")

        order_info = {
            'order_id': order_id,
            'symbol': symbol,
            'order_type': order_type,
            'price': price,
            'quantity': quantity,
            'timestamp': timestamp,
            'status': status,
            'commission': commission,
            'remaining_cash': self.cash
        }
        self.orders[order_id] = order_info
        return order_info

    def cancel_order(self, order_id: str) -> bool:
        """模拟撤单"""
        if order_id in self.orders:
            if self.orders[order_id]['status'] == 'filled':
                logger.warning(f"撤单失败: 订单 {order_id} 已成交。")
                return False
            self.orders[order_id]['status'] = 'cancelled'
            logger.info(f"订单 {order_id} 已取消。")
            return True
        logger.error(f"撤单失败: 未找到订单 {order_id}")
        return False

    def get_account_info(self) -> Dict[str, Any]:
        """获取账户概览，包括总市值（基于成本价估算）"""
        total_market_value = sum(p['quantity'] * p['cost_price'] for p in self.positions.values())
        return {
            'cash': round(self.cash, 2),
            'market_value': round(total_market_value, 2),
            'total_assets': round(self.cash + total_market_value, 2),
            'initial_cash': self.initial_cash
        }

    def get_positions(self) -> Dict[str, Any]:
        return self.positions

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        return self.orders.get(order_id, {'status': 'not_found'})
