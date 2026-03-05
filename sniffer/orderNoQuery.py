import requests
import threading
import json
import time
from datetime import datetime, timedelta

import math




# 存储结果的字典，用于保存每个日期的预约信息
results = {}
# 锁，用于线程同步，确保多线程操作时数据安全
lock = threading.Lock()

# 预约接口的 URL
order_url = "http://www.ruanjiezh.cn:8081/api/mobile/order/create"
# 配置文件路径
config_file = "confignew.txt"
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
interval = 0.2

# 读取配置文件，解析内容并赋值到对应变量
with open(config_file, "r", encoding="utf-8") as file:
    lines = file.readlines()
    for i, line in enumerate(lines):
        print(line)
        # 解析用户名
        if line.startswith("name"):
            name = line.strip().split("=")[1]
        
        # 解析手机号
        if line.startswith("phone"):
            phone = line.strip().split("=")[1]
        # 解析 openId 列表
        if line.startswith("openIds"):
            openIds = line.strip().split("=")[1].split(",")
        # 解析日期和时段映射
        if line.startswith("datetimes"):
            tdatetimes = line.strip().split("=")[1].split(",")
            for t in tdatetimes:
                print(t)
                day_t = t.strip().split("#")
                datetimes[day_t[0]] = day_t[1]

# 初始化成功标志和尝试次数
success = 0
tryin = 0

date='2025-05-27'  # 指定日期
try:
    # 构造请求 URL
    url = f'http://www.ruanjiezh.cn:8081/api/mobile/reservation/tag/{date}'
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        # 获取锁，确保线程安全
        lock.acquire()
        try:
            # 将结果存入字典
            rjson = json.loads(response.text)
            results[date] = rjson.get('data').get("items")
        finally:
            # 释放锁
            lock.release()
    else:
        print(f"请求 {date} 失败，状态码: {response.status_code}")
except Exception as e:
    print(f"请求 {date} 时发生错误: {e}")
#print(results)
playgrounds = results.get(date)
#获取playgrounds最后一个元素
if playgrounds:
    last_playground = playgrounds[0]
    print(f"第一个元素: {last_playground}")


# 剩余 openId 数量
oi = 0
# 以天为单位遍历预约配置,
for k, v in datetimes.items():

    # 获取当前日期的预约的时间数组
    arr = v.strip().split("@")
    # 指定的预约时段列表
    tlist = []
    l = len(tlist)
    
    print(tlist)
    i = 0
    
    
print(oi)

