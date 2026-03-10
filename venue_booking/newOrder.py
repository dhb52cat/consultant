import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List
import requests
import threading
import json
import time
from datetime import datetime, timedelta
import math
import os

def read_info_file_simple() -> dict:
    """
    简洁版本：读取info.txt文件并返回字典
    """
    import os
    from pathlib import Path

    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    file_path = script_dir / 'info.txt'
    
    if not file_path.exists():
        return {}
    
    result = {}
    result2={}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line:
                date, ids_str = line.split('=', 1)
                result[date.strip()] = [id_str.strip() for id_str in ids_str.split(',')]
                #遍历result的keys和values
                for k, v in result.items():
                    for timeStr in v:
                        time,ids = timeStr.split('#')
                        result2[k+time] = ids.split('@')
    return result2

def simple_write_appointment_info(date_str, appointment_ids):
    """
    简单版本：直接追加到文件末尾
    """
    
    output_content = appointment_ids
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'info.txt')
    
    try:
        # 以追加模式写入文件
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f" 成功追加到文件: {file_path}")
        print(f" 写入内容: {output_content.strip()}")
        
    except Exception as e:
        print(f" 写入文件时出错: {e}")


# 存储结果的字典，用于保存每个日期的预约信息
results = {}


# 预约接口的 URL
order_url = "http://www.ruanjiezh.cn:8081/api/mobile/order/create"
# 配置文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, "confignew.txt")
# 用户的 openId 列表
openIds = []
# 日期和时段的映射
datetimes = {}

# 用户名
name = ''
# 用户手机号
phone = ''
# 星期二的标识
Tuesday = ''
# 刷新间隔时间
interval = 0.1
start=''
read='0'
order='0'

# 读取配置文件，解析内容并赋值到对应变量 
# 读取配置到 datetimes 字典 {'2025-05-31': ['17', '18'], '2025-06-01': ['17']}
with open(config_file, "r", encoding="utf-8") as file:
    lines = file.readlines()
    for i, line in enumerate(lines):
        print(line)
        # 解析用户名
        if line.startswith("name"):
            name = line.strip().split("=")[1]
        # 解析手机号
        if line.startswith("start"):
            start = line.strip().split("=")[1]
        # 解析手机号
        if line.startswith("read"):
            read = line.strip().split("=")[1]
        # 解析手机号
        if line.startswith("order"):
            order = line.strip().split("=")[1]
        # 解析手机号
        if line.startswith("phone"):
            phone = line.strip().split("=")[1]
        if line.startswith("interval"):
            #字符串转数字

            interval = float(line.strip().split("=")[1])
        # 解析 openId 列表
        if line.startswith("openIds"):
            openIds = line.strip().split("=")[1].split(",")
        # 解析日期和时段映射
        if line.startswith("datetimes"):
            tdatetimes = line.strip().split("=")[1].split(",")
            for t in tdatetimes:
                print(t)
                day_t = t.strip().split("#")
                datetimes[day_t[0]] = day_t[1].split('@')

print(f"配置文件读取完成，用户: {name}, 手机号: {phone}, openIds: {openIds}, 刷新间隔: {interval}, 日期和时段: {datetimes}")

# 等待到指定时间点
while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    if current_time >= start:
        print(f"当前时间 {current_time} 达到或超过设定的开始时间 {start}，开始执行预约任务。")
        break
    # 每秒检查一次
    time.sleep(0.1)


print("开始执行预约任务...")
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
            if interval > 0:
                time.sleep(interval)

            #如果响应包含IP字符则打印响应
            if "IP" in response.text:
                print(f"预约请求响应: {response.text}")
            else:
                print(f"预约请求发送: {param}, 响应: {response.text}")
            res=response.json();

            return response.json()
        except Exception as e:
            # print(f"预约请求失败: {e}")
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
#根据第一个日期获取需要抢票的id数组
def getIds(d,timeinday,first_playground):

    ids_str = ''
    for t in timeinday:
        ids = []
        res=(int(t)-7)*4+int(first_playground)
        id=int(first_playground)+(int(t)-7)*4
        ids.append(id)
        ids.append(id+1)
        ids.append(id+2)
        ids.append(id+3)
        ids_str +=','+t+'#'+ '@'.join(map(str, ids))
    # 构建输出内容
    ids_str = ids_str.lstrip(',')
    output_content = f"{d}={ids_str}\n"
    return output_content


# 使用线程池来并发请求每个日期的预约信息
import requests
from concurrent.futures import ThreadPoolExecutor
# 定义线程池大小
THREAD_POOL_SIZE = 100
# 创建线程池
executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
# 定义请求函数
def fetch_reservation(d,t,isWrite):
    """获取指定日期的预约信息"""
    global results
    firstId=0
    n=0;
    while True:
        # 构造请求 URL
        # print(f"正在获取 {d} 的预约信息...")
        url = f'http://www.ruanjiezh.cn:8081/api/mobile/reservation/tag/{d}'
        # print(url)
        try:
            n=n+1
            response = requests.get(url)
            print(f"获取 {d} 的预约信息响应: {response.text}, 尝试次数: {n}")
            #text中包含IP字符则打印响应文
            if "IP" in response.text:
                print(f"获取 {d} 的预约信息响应: {response.text}, 尝试次数: {n}")
            if response.status_code == 200:
                # 将结果存入字典
                rjson = json.loads(response.text)
                status=rjson.get('status')
                if status:
                    res = rjson.get('data').get("items")
                    firstId=res[0].get("reservationId")
        except Exception as e:
            print(f"请求 {d} 时发生错误: {e}")
        if firstId != 0:
            break
        time.sleep(interval)
    # print(f"获取 {d} 的预约信息成功，firstId: {firstId}")
    ids =getIds(d,t,firstId)   
    print(f"日期 {d} 的预约信息: {ids}")   
    if isWrite==1:
        simple_write_appointment_info(d, ids)
        
    
    
    
    # 要预约的ID列表
    
    
    

    
# 提交任务到线程池
# # 遍历 datetimes 字典中，每个日期一个线程请求当日场地信息
# for d,t in datetimes.items():
#     print(f"提交任务获取 {d} 的预约信息...")
#     executor.submit(fetch_reservation, d,t)
# 等待所有线程完成
# executor.shutdown(wait=True)

#循环20次
if(read=='1'):
    #datetimes第一个元素
    d,t=list(datetimes.items())[0]
    fetch_reservation(d,t,0)
    for d,t in datetimes.items():
        print(f"提交任务获取 {d} 的预约信息...")
        executor.submit(fetch_reservation, d,t,1)

if(order=='1'):
     # 创建抢票实例
    order_client = MultiThreadOrder(order_url, openIds[0], name, phone)
    # 读取预约信息直到appointment_data的size大于6
    while True:
        appointment_data = read_info_file_simple()
        if len(appointment_data) > 6:
            break
        time.sleep(0.1)

    print(f"读取到的预约数据: {appointment_data}")
    # 执行批量预约
    #appointment_data的
    #遍历datetimes的keys，value

    for d,t in datetimes.items():
        for tt in t:

            appointment_ids = appointment_data.get(d+tt, [])
            if appointment_ids:
                print(f"开始预约日期 {d} 的场地，预约ID: {appointment_ids}")
                results = order_client.batch_order(appointment_ids, d)
                print(f"日期 {d} 的预约结果: {results}")
            else:
                print(f"日期 {d} 没有找到预约ID，跳过预约。")

    # 打印结果
    # for i, result in enumerate(results):
        # print(f"ID {ids[i]} 预约结果: {result}")  




