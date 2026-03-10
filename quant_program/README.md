# Quant Program

这是一个模块化的量化交易程序，旨在提供实时数据获取、量化指标计算、策略执行、微信通知和实时下单功能。

## 功能特性

- **模块化设计:** 支持灵活替换数据源、通知渠道和交易平台。
- **多数据源支持:**
    - 沪深北个股数据 (通过 Tushare Pro)
    - 全球主要市场大盘指数 (通过 yfinance)
- **技术指标:** 集成常用技术分析指标 (MACD, RSI, SMA 等)。
- **交易策略:** 实现趋势跟踪和盘中做T策略。
- **微信通知:** 通过 Server酱 实时推送交易信号和警报。
- **实时下单:** 预留真实交易平台接口，目前提供模拟交易功能。
- **配置化:** 所有关键参数通过 `config/settings.ini` 进行管理。

## 项目结构

```
quant_program/
├── config/                  # 配置文件
├── data_sources/            # 数据获取模块
├── indicators/              # 技术指标计算模块
├── strategy/                # 交易策略模块
├── notifications/           # 通知模块
├── trading/                 # 交易执行模块
├── core/                    # 核心调度与集成
├── tests/                   # 单元测试
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明
```

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd quant_program
```

### 2. 设置虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
# 注意：TA-Lib 的安装可能需要一些系统级别的依赖，如果遇到问题，请参考 TA-Lib 官方文档。
# 或者可以尝试安装 pandas_ta 作为替代：
# pip install pandas_ta
```

### 4. 配置 `settings.ini`

打开 `config/settings.ini` 文件，填入您的 API Keys 和其他配置信息：

- `TUSHARE_PRO_TOKEN`: 从 Tushare Pro 官网获取。
- `SERVERCHAN_SCKEY`: 从 Server酱 官网获取。
- 配置您关注的 `STOCK_SYMBOLS` 和 `INDEX_SYMBOLS`。
- 其他策略参数和模拟交易参数。

### 5. 运行程序

```bash
python core/main_executor.py
```

## 扩展与定制

- **更换数据源:** 实现新的 `BaseDataSource` 子类，并在 `main_executor.py` 中替换数据源实例。
- **更换通知渠道:** 实现新的 `BaseNotifier` 子类，并在 `main_executor.py` 中替换通知器实例。
- **接入真实交易平台:** 实现新的 `BaseTrader` 子类 (例如 `JoinQuantTrader.py`)，并在 `main_executor.py` 中替换交易器实例。
- **添加新策略:** 实现新的 `BaseStrategy` 子类，并在 `main_executor.py` 中集成。
