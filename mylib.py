from machine_lib import *
import logging;
def getLog():
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别
        format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式，包含时间
        datefmt="%Y-%m-%d %H:%M:%S",  # 时间格式
        filename="app.log",  # 指定日志文件
        filemode="a"  # 写入模式，"w"表示覆盖，"a"表示追加
    )
REGION_LIST = ['USA', 'GLB', 'EUR', 'ASI', 'CHN', 'KOR', 'TWN', 'JPN', 'HKG', 'AMR']
DELAY_LIST = [1, 0]
INSTRUMENT_TYPE_LIST = ['EQUITY', 'CRYPTO']
UNIVERSE_DICT = {
    "instrumentType": {
        "EQUITY": {
            "region": {
                "USA": [
                    "TOP3000", "TOP1000", "TOP500", "TOP200", "ILLIQUID_MINVOL1M", "TOPSP500",
                ],
                "GLB": [
                    "TOP3000", "MINVOL1M",
                ],
                "EUR": [
                    "TOP1200", "TOP800", "TOP400", "ILLIQUID_MINVOL1M",
                ],
                "ASI": [
                    "MINVOL1M", "ILLIQUID_MINVOL1M",
                ],
                "CHN": [
                    "TOP2000U",
                ],
                "KOR": [
                    "TOP600",
                ],
                "TWN": [
                    "TOP500", "TOP100",
                ],
                "HKG": [
                    "TOP800", "TOP500",
                ],
                "JPN": [
                    "TOP1600", "TOP1200",
                ],
                "AMR": [
                    "TOP600",
                ]
            }
        },
        "CRYPTO": {
            "region": {
                "GLB": [
                    "TOP50", "TOP20", "TOP10", "TOP5",
                ]
            }
        }
    }
}
def loadtxt():
    # 打开文件并读取所有行到列表中
    with open('/Users/donghongbin/py/job.txt', 'r', encoding='utf-16') as file:
        lines=[]
        for line in file:
            line=line.strip()
            if line!='':
                lines.append(line)

    # 输出列表
    print(lines)
    return lines
def printlist(list):
    for i in list:
        print(i)

def submitalpha(s, alpha_id):
    brain_api_url ='https://api.worldquantbrain.com'
    print (1)
    result =s.post(brain_api_url + "/alphas/" + alpha_id + "/submit")
    print (result)
    while True:
        if "retry-after" in result.headers:
            time.sleep(float(result.headers["Retry-After"]))
            result =s.get(brain_api_url + "/alphas/"+ alpha_id + "/submit")
        else:
            break
    return result.status_code== 200
class Map:
    def __init__(self):
        # 使用内部字典来存储键值对
        self.data = {}
    
    # 插入键值对
    def put(self, key, value):
        self.data[key] = value
    
    # 获取某个键的值
    def get(self, key):
        return self.data.get(key, None)
    
    # 删除某个键
    def remove(self, key):
        if key in self.data:
            del self.data[key]
    
    # 判断键是否存在
    def contains(self, key):
        return key in self.data
    
    # 获取所有键
    def keys(self):
        return list(self.data.keys())
    
    # 获取所有值
    def values(self):
        return list(self.data.values())
    
    # 获取键值对
    def items(self):
        return list(self.data.items())
    
    # 显示Map对象的字符串表示
    def __repr__(self):
        return f"Map({self.data})"
