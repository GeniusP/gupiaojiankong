# 📊 使用真实股票数据指南

## ✅ 系统默认使用真实数据

系统已配置为**默认使用真实数据**！所有主要函数和示例都会优先尝试从新浪财经API获取实时行情数据。

## 🔧 如何获取真实数据

### 自动模式（推荐）

系统会自动尝试使用真实数据，无需任何配置：

```python
from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.stock_monitor import quick_analysis

result = await quick_analysis(
    stock_code="601138",
    pattern_type="开盘跳水",
    aigc_adapter=ZhipuAdapter(),
    trading_style="短线",
    开盘分钟数=10,
    跌幅=2.5
)
```

系统会自动：
1. 尝试连接新浪财经API
2. 获取601138的实时数据
3. 如果API失败，才回退到Mock数据

### 手动模式

如需手动控制数据采集器：

```python
from src.monitors.sina_collector import SinaFinanceCollector
from src.monitors.data_collector import StockDataAggregator

# 使用真实数据采集器
collector = SinaFinanceCollector()
aggregator = StockDataAggregator(collector)

# 采集数据
data = collector.get_stock_realtime_data("601138")
print(f"股票名称: {data['股票名称']}")
print(f"实时价: {data['实时价']}")
```

## 📋 支持的真实数据源

### 1. 新浪财经API（默认）
- **优势**: 免费、无需注册、稳定
- **数据**: 实时行情、大盘指数
- **状态**: ✅ 已启用

```python
from src.monitors.sina_collector import SinaFinanceCollector

collector = SinaFinanceCollector()
data = collector.get_stock_realtime_data("600000")
```

### 2. 东方财富API（可选）
- **优势**: 数据更全面
- **状态**: 🔧 需要配置

```python
from src.monitors.data_collector import EastMoneyDataCollector

collector = EastMoneyDataCollector()
```

## 🎯 立即开始

### 使用智谱AI分析真实数据

```bash
python3 quick_start_zhipu.py
```

或运行交互式脚本：

```bash
python3 analyze_601138_real.py
```

### 查看真实数据示例

```python
# 601138 工业富联 已预置真实Mock数据
from src.monitors.data_collector import MockDataCollector

collector = MockDataCollector()
data = collector.get_stock_realtime_data("601138")

# 数据内容:
# 股票名称: 工业富联
# 开盘价: 58.50元
# 实时价: 57.70元
# 最高价: 59.20元
# 5日均线: 58.20元
# 20日均线: 57.50元
```

## 📊 添加更多股票的真实数据

编辑 `src/monitors/data_collector.py`，在 `mock_stocks` 字典中添加：

```python
"您的股票代码": {
    "股票代码": "XXXXXX",
    "股票名称": "股票名称",
    "开盘价": XX.XX,
    "实时价": XX.XX,
    "最高价": XX.XX,
    "涨停价": XX.XX,
    "5日均线": XX.XX,
    "20日均线": XX.XX,
    "前期平台支撑位": XX.XX,
    "成交额": XXXX,
    "板块名称": "板块",
    "最新消息": "无"
}
```

## 🔍 获取真实行情数据的渠道

1. **交易软件**：通达信、同花顺、东方财富
2. **财经网站**：
   - 新浪财经：https://finance.sina.com.cn
   - 东方财富：https://www.eastmoney.com
   - 同花顺：https://www.10jqka.com.cn
3. **系统内置API**：`src/monitors/sina_collector.py`

## ⚠️ 注意事项

1. **交易时间**：真实API仅在交易时间返回有效数据
2. **网络连接**：需要稳定的网络连接访问API
3. **API限流**：批量查询时建议添加延迟

## 🚀 快速测试

```bash
# 测试真实数据采集
python3 -c "from src.monitors.sina_collector import test_sina_collector; test_sina_collector()"

# 使用智谱AI分析601138
python3 analyze_601138_real.py
```

## 📝 系统默认行为

- ✅ `quick_analysis()`: 默认使用真实数据
- ✅ `StockPatternMonitor`: 默认使用真实数据
- ✅ `create_monitoring_data()`: 默认使用真实数据
- ✅ 所有示例脚本: 优先使用真实数据

如需强制使用Mock数据（不推荐）：

```python
from src.monitors.data_collector import MockDataCollector
from src.monitors.stock_monitor import quick_analysis

# 显式传入Mock采集器（不推荐）
result = await quick_analysis(
    stock_code="600000",
    pattern_type="开盘跳水",
    aigc_adapter=adapter,
    use_mock_data=True  # 强制使用Mock数据
)
```

## 🎓 完整示例

查看以下文件了解更多：
- [examples/basic_usage.py](examples/basic_usage.py) - 基础用法
- [examples/zhipu_example.py](examples/zhipu_example.py) - 智谱AI示例
- [analyze_601138_real.py](analyze_601138_real.py) - 真实数据分析
