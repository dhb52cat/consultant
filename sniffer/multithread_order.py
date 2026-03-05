import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

class MultiThreadOrder:
    def __init__(self, order_url: str, openid: str, name: str, phone: str):
        self.order_url = order_url
        self.openid = openid
        self.name = name
        self.phone = phone
        
    def send_order(self, reservation_id: str, date: str) -> dict:
        """发送单个预约请求"""
        param = {
            "openId": self.openid,
            "reservationId": reservation_id,
            "userName": self.name,
            "userPhone": self.phone,
            "date": date
        }
        try:
            response = requests.post(self.order_url, json=param)
            return response.json()
        except Exception as e:
            print(f"预约请求失败: {e}")
            return {"success": False, "error": str(e)}

    def batch_order(self, ids: List[str], date: str, max_workers: int = 50):
        """批量发送预约请求"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.send_order, str(id), date)
                for id in ids
            ]
            results = []
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"线程执行失败: {e}")
                    results.append({"success": False, "error": str(e)})
        
        return results

# 使用示例
if __name__ == "__main__":
    # 配置信息
    ORDER_URL = "http://www.ruanjiezh.cn:8081/api/mobile/order/create"
    openid = "your_openid"
    name = "your_name"
    phone = "your_phone"
    
    # 创建抢票实例
    order_client = MultiThreadOrder(ORDER_URL, openid, name, phone)
    
    # 要预约的ID列表
    ids_to_order = ["1", "2", "3", "4"]  # 替换为实际的预约ID
    date = "2025-05-31"
    
    # 执行批量预约
    results = order_client.batch_order(ids_to_order, date)
    
    # 打印结果
    for i, result in enumerate(results):
        print(f"ID {ids_to_order[i]} 预约结果: {result}")
