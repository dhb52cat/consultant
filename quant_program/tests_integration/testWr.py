import time
from datetime import datetime, timezone, timedelta
import os

# 1. 配置：设置文件路径和中国时区
LOG_FILE = "execution_log.txt"
CHINA_TZ = timezone(timedelta(hours=8))
INTERVAL = 30  # 间隔秒数

def run_logger():
    count = 0
    print(f"🚀 程序启动，日志将写入: {os.path.abspath(LOG_FILE)}")
    
    try:
        while True:
            count += 1
            # 获取当前北京时间
            now_str = datetime.now(CHINA_TZ).strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"第 {count:04d} 次执行 | 时间: {now_str}\n"
            
            # 以追加模式 ('a') 写入文件
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
                # 强制将缓冲区数据写入磁盘，防止掉电/崩溃丢失数据
                f.flush()
                os.fsync(f.fileno())
            
            print(f"已记录: {log_entry.strip()}")
            
            # 倒计时
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 程序已由用户手动停止")
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    run_logger()