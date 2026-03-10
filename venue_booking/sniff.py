import os
import re
import json
from scapy.all import *

# 配置文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, "config.txt")

def packet_callback(packet):
    if packet.haslayer(Raw):
        payload = packet[Raw].load.decode(errors="ignore")
        if "POST" in payload and "openId" in payload:
            match = re.search(r'\{.*\}', payload, re.DOTALL)
            if match:
                json_data = match.group(0)
                parsed_data = json.loads(json_data)
                open_id = parsed_data.get("openId")
                print(open_id)  # 输出: oIVg65rRnO0DVI-DHjR9ggZ29f5Y
                with open(config_file, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("openId="):
                        existing_values = line.strip().split("=")[1]
                        if open_id not in existing_values.split(","):
                            lines[i] = f"openId={existing_values},{open_id}\n" if existing_values!="" else f"openId={open_id}\n"
                        found = True
                        break
                with open(config_file, "w", encoding="utf-8") as file:
                    file.writelines(lines)
            else:
                print("No JSON data found.")

# 监听 80 端口（HTTP 流量）
sniff(filter="tcp", prn=packet_callback, store=False)

