import requests
import threading
import json
import time

# 存储结果的字典，用于保存每个日期的预约信息
results = {}
# 锁，用于线程同步，确保多线程操作时数据安全
lock = threading.Lock()

# 预约接口的 URL
order_url = "http://www.ruanjiezh.cn:8081/api/mobile/order/create"
# 配置文件路径
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, "config.txt")
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
        # 解析刷新间隔时间
        if line.startswith("interval"):
            interval = float(line.strip().split("=")[1])
        # 解析用户名
        if line.startswith("name"):
            name = line.strip().split("=")[1]
        # 解析星期二标识
        if line.startswith("Tuesday"):
            Tuesday = line.strip().split("=")[1]
        # 解析手机号
        if line.startswith("phone"):
            phone = line.strip().split("=")[1]
        # 解析 openId 列表
        if line.startswith("openIds"):
            openIds = line.strip().split("=")[1].split(",")
        # 解析日期和时段映射，每个日期配置以逗号分隔，
        if line.startswith("datetimes"):
            tdatetimes = line.strip().split("=")[1].split(",")
            for t in tdatetimes:
                print(t)
                day_t = t.strip().split("#")
                datetimes[day_t[0]] = day_t[1]

# 初始化成功标志和尝试次数
success = 0
tryin = 0

# 不断刷新预约状态，直到成功获取可用状态 查询周二标志位数据
while success == 0:
    # 构造请求 URL
    url = f'http://www.ruanjiezh.cn:8081/api/mobile/reservation/tag/{Tuesday}'
    response = requests.get(url)
    tryin += 1
    # 如果响应中包含 "true"，表示预约开放
    if "true" in response.text:
        success = 1
    time.sleep(interval)
    print(f"等待刷新{tryin}")

# 定义发送请求的函数，用于获取指定日期的预约信息，并将结果存入字典results，results的key为日期
def send_request(date):
    global results
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

# 遍历日期配置，获取每个日期的预约信息
for key, value in datetimes.items():
    send_request(key)
    print(key)
    print(value)

# 剩余 openId 数量
open_id_left = len(openIds)
oi = 0
# 以天为单位遍历预约配置,
for k, v in datetimes.items():
    # 获取当前日期的预约信息
    pglist = results[k]
    arr = v.strip().split("@")
    # 当日可预约时长
    t2p = int(arr[1])
    harr = arr[0].strip().split("-")
    # 指定的预约时段列表
    tlist = []
    l = len(tlist)
    for i in harr:
        tlist.append(f'{k}T{i}:00:00')
    print(t2p)
    print(tlist)
    i = 0
    
    # 遍历预约时段，发送预约请求
    while oi < open_id_left and t2p > 0 and i < len(tlist):
        print(tlist[i])
        order = 0
        for pg in pglist:
            # 匹配预约时段
            if pg.get("startTime") == tlist[i] and order == 0:
                print(pg)
                # 构造预约请求参数
                param = {
                    "openId": openIds[oi],
                    "reservationId": pg.get("reservationId"),
                    "userName": name,
                    "userPhone": phone
                }
                # 发送预约请求
                orderresponse = requests.post(order_url, json=param)
                print(orderresponse.text)

                # 如果请求成功，更新状态
                if "true" in orderresponse.text:
                    t2p -= 1
                    order += 1
                    oi += 1
        i += 1
print(oi)
