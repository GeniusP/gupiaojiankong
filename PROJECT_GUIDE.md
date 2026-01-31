# 股票AIGC监控系统 - 项目概览

## 📁 项目结构

```
stock/
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化文件
│   ├── templates/               # Prompt模板管理
│   │   ├── __init__.py
│   │   └── prompt_templates.py  # 三种图形的Prompt模板（核心）
│   ├── models/                  # 数据模型定义
│   │   ├── __init__.py
│   │   └── stock_data.py        # 股票数据、AIGC响应模型
│   ├── monitors/                # 监控逻辑实现
│   │   ├── __init__.py
│   │   ├── data_collector.py    # 数据采集器（可扩展）
│   │   └── stock_monitor.py     # 图形识别+触发判断（核心）
│   ├── aigc/                    # AIGC模型适配
│   │   ├── __init__.py
│   │   └── model_adapter.py     # GPT/讯飞/千帆适配器
│   └── utils/                   # 工具模块
│       ├── __init__.py
│       └── config.py            # 配置管理
├── examples/                    # 使用示例
│   └── basic_usage.py           # 完整使用示例
├── logs/                        # 日志目录（自动创建）
├── config/                      # 配置目录（预留）
├── requirements.txt             # 依赖列表
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git忽略文件
├── quick_start.py              # 快速启动脚本（推荐）
├── README.md                    # 项目文档
└── PROJECT_GUIDE.md            # 本文档
```

## 🎯 核心功能模块

### 1. Prompt模板管理器 (`prompt_templates.py`)

**功能**：为三种图形生成结构化Prompt

**核心类**：
- `PromptTemplateManager` - 模板管理器
- `generate_prompt()` - 便捷生成函数

**支持模板**：
- 完整版（150字，深度分析）
- 简化版（50字，快速响应）

**使用示例**：
```python
from src.templates.prompt_templates import generate_prompt

prompt = generate_prompt(
    chart_type="开盘跳水",
    stock_data={...},
    trading_style="短线",
    template_type="简化版"
)
```

### 2. 数据采集模块 (`data_collector.py`)

**功能**：采集股票实时数据、板块数据、大盘数据

**核心类**：
- `DataCollector` - 抽象基类（可继承扩展）
- `MockDataCollector` - 模拟数据采集器（测试用）
- `StockDataAggregator` - 数据聚合器

**扩展方式**：
```python
from src.monitors.data_collector import DataCollector

class MyDataCollector(DataCollector):
    def get_stock_realtime_data(self, stock_code: str):
        # 实现你的数据采集逻辑
        return {...}
```

### 3. 监控逻辑模块 (`stock_monitor.py`)

**功能**：图形识别、触发判断、AIGC分析

**核心类**：
- `StockPatternMonitor` - 主监控器
- `PatternRule` - 识别规则
- `PatternType` - 图形类型枚举
- `TradingStyle` - 交易风格枚举

**识别规则**：
- 开盘跳水：开盘5分钟跌超3% / 10分钟跌超2%
- 破位下跌：跌破均线+放量 / 跌破支撑位+3分钟未回弹
- 冲板回落：冲板后回落超5% / 冲高超8%后回落超3%

**使用示例**：
```python
from src.monitors.stock_monitor import quick_analysis

result = await quick_analysis(
    stock_code="600000",
    pattern_type="开盘跳水",
    aigc_adapter=your_adapter,
    trading_style="短线"
)
```

### 4. AIGC模型适配器 (`model_adapter.py`)

**功能**：统一接口调用多种大模型

**支持模型**：
- GPT (OpenAI)
- 讯飞星火
- 文心一言（百度千帆）

**核心类**：
- `AIGCModelAdapter` - 抽象基类
- `GPTAdapter` - GPT适配器
- `SparkAdapter` - 讯飞星火适配器
- `QianfanAdapter` - 千帆适配器
- `MockAIGCAdapter` - Mock适配器（测试用）

**使用示例**：
```python
from src.aigc.model_adapter import create_adapter, ModelProvider

adapter = create_adapter(
    ModelProvider.GPT,
    api_key="your_api_key",
    model="gpt-4-turbo-preview"
)
```

### 5. 配置管理 (`config.py`)

**功能**：从环境变量加载配置

**配置项**：
- AIGC模型API密钥
- 数据源配置
- 监控参数（间隔、交易风格）
- 日志配置

## 🚀 快速开始

### 步骤1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2：配置环境（可选，使用Mock可跳过）

```bash
cp .env.example .env
# 编辑.env，填入API密钥
```

### 步骤3：运行快速启动脚本

```bash
python quick_start.py
```

### 步骤4：选择功能体验

```
1. 查看Prompt模板 - 输入股票数据，查看生成的Prompt
2. 运行示例分析 - 使用Mock AIGC体验完整流程
3. 配置检查 - 检查API配置状态
4. 查看帮助 - 了解系统使用方法
```

## 📖 三种使用方式

### 方式1：仅使用Prompt模板

**适合场景**：已有数据采集和AIGC调用，只需Prompt模板

```python
from src.templates.prompt_templates import generate_prompt

# 准备数据
data = {
    "股票代码": "600000",
    "股票名称": "浦发银行",
    "触发时间": "09:35",
    "开盘分钟数": 5,
    "跌幅": 3.2,
    # ... 其他字段
}

# 生成Prompt
prompt = generate_prompt(
    chart_type="开盘跳水",
    stock_data=data,
    trading_style="短线"
)

# 调用你的AIGC接口
result = your_aigc_api(prompt)
```

### 方式2：使用监控器+自带AIGC

**适合场景**：使用系统提供的监控逻辑，自己配置AIGC

```python
from src.aigc.model_adapter import create_adapter, AIGCService, ModelProvider
from src.monitors.stock_monitor import StockPatternMonitor, PatternType
from src.monitors.data_collector import StockDataAggregator, MockDataCollector

# 创建监控器
aggregator = StockDataAggregator(MockDataCollector())
adapter = create_adapter(ModelProvider.GPT, api_key="your_key")
aigc_service = AIGCService(adapter)
monitor = StockPatternMonitor(aggregator, aigc_service)

# 执行监控
trigger_event = await monitor.analyze_pattern(
    stock_code="600000",
    pattern_type=PatternType.OPENING_DIVE
)
```

### 方式3：快速分析（最简单）

**适合场景**：快速测试、演示

```python
from src.aigc.model_adapter import MockAIGCAdapter
from src.monitors.stock_monitor import quick_analysis

result = await quick_analysis(
    stock_code="600000",
    pattern_type="开盘跳水",
    aigc_adapter=MockAIGCAdapter(),
    trading_style="短线"
)
```

## 🔧 实际部署流程

### 1. 数据接入

选择一种方式接入真实数据：

**选项A：实现自定义数据采集器**
```python
from src.monitors.data_collector import DataCollector

class RealDataCollector(DataCollector):
    def get_stock_realtime_data(self, stock_code: str):
        # 调用你的数据API（如东方财富、同花顺等）
        return {...}
```

**选项B：手动采集数据**
```python
# 已有数据源，直接传入字典
data = {...}  # 你的数据
prompt = generate_prompt("开盘跳水", data)
```

### 2. AIGC配置

选择一种模型并配置：

**GPT配置**：
```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
DEFAULT_AIGC_MODEL=gpt
```

**讯飞星火配置**：
```bash
SPARK_APP_ID=xxx
SPARK_API_KEY=xxx
SPARK_API_SECRET=xxx
DEFAULT_AIGC_MODEL=spark
```

**文心一言配置**：
```bash
QIANFAN_ACCESS_KEY=xxx
QIANFAN_SECRET_KEY=xxx
DEFAULT_AIGC_MODEL=qianfan
```

### 3. 监控运行

```python
import asyncio
from src.aigc.model_adapter import create_adapter, ModelProvider
from src.monitors.stock_monitor import StockPatternMonitor, PatternType

async def main():
    # 初始化（从环境变量自动加载配置）
    from src.utils.config import Config
    provider = ModelProvider(Config.DEFAULT_AIGC_MODEL)
    adapter = create_adapter(provider, **Config.get_model_config(provider))

    # 创建监控器
    monitor = StockPatternMonitor(data_aggregator, AIGCService(adapter))

    # 持续监控
    while True:
        # 检测目标股票
        for stock_code in target_stocks:
            result = await monitor.analyze_pattern(
                stock_code=stock_code,
                pattern_type=PatternType.OPENING_DIVE
            )
            if result:
                # 发送通知（钉钉/微信/邮件）
                send_alert(result)

        # 等待下一个检测周期
        await asyncio.sleep(Config.MONITOR_INTERVAL_SECONDS)

asyncio.run(main())
```

## 📊 数据字段详解

### 必填基础字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| 股票代码 | str | 6位股票代码 | "600000" |
| 股票名称 | str | 股票名称 | "浦发银行" |
| 触发时间 | str | HH:MM格式 | "09:35" |
| 图形类型 | str | 三选一 | "开盘跳水" |

### 行情数据

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| 开盘价 | float | 开盘价 | 是 |
| 实时价 | float | 当前价格 | 是 |
| 最高价 | float | 当日最高 | 是 |
| 涨停价 | float | 涨停价 | 否 |
| 5日均线 | float | 5日线价格 | 建议 |
| 20日均线 | float | 20日线价格 | 建议 |
| 前期平台支撑位 | float | 支撑位 | 建议 |

### 成交量数据

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| 触发成交额 | float | 时刻成交额（万元） | 是 |
| 成交额放大比例 | float | 较前5日均值% | 建议 |
| 当日成交额放大比例 | float | 较当日均值% | 否 |
| 分钟成交额放大比例 | float | 较前1分钟% | 否 |

### 市场环境

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| 板块名称 | str | 所属板块 | 建议 |
| 板块涨跌幅 | float | 板块今日涨跌% | 建议 |
| 大盘名称 | str | 指数名称 | 否 |
| 大盘涨跌幅 | float | 大盘涨跌% | 建议 |
| 最新消息 | str | 公告/消息 | 否 |

### 图形专属字段

**开盘跳水**：
- `开盘分钟数` (int): 触发时的开盘分钟数
- `跌幅` (float): 跌幅百分比
- `均线类型` (int): 5或20
- `均线价格` (float): 均线价格

**破位下跌**：
- `支撑位价格` (float): 跌破的支撑位
- `破位后未回弹分钟数` (int): 未回弹时长

**冲板回落**：
- `涨幅` (float): 冲板时的涨幅
- `回落幅度` (float): 回落百分比
- `封板挂单量` (int): 封板时买一挂单（手）

## 💡 常见问题

### Q1: 如何测试系统而无需配置API？

使用Mock AIGC适配器：
```python
from src.aigc.model_adapter import MockAIGCAdapter
adapter = MockAIGCAdapter()
```

### Q2: 如何自定义识别规则？

```python
from src.monitors.stock_monitor import PatternRule

custom_rule = PatternRule(
    name="自定义规则",
    condition=lambda data: your_logic(data),
    description="规则描述"
)
monitor.your_rules.append(custom_rule)
```

### Q3: 如何切换完整版/简化版模板？

```python
from src.templates.prompt_templates import TemplateType

# 完整版（150字）
template_type = TemplateType.FULL

# 简化版（50字）
template_type = TemplateType.SIMPLIFIED
```

### Q4: 支持批量监控吗？

```python
detected = monitor.batch_detect(
    stock_codes=["600000", "000001", "600036"],
    pattern_types=[PatternType.OPENING_DIVE, PatternType.BREAKDOWN_FALL]
)
```

### Q5: 如何集成到现有系统？

1. **仅使用Prompt模板**：导入`generate_prompt`函数
2. **使用监控逻辑**：导入`StockPatternMonitor`
3. **完整集成**：使用所有模块，参考`examples/basic_usage.py`

## 📚 更多资源

- [README.md](README.md) - 完整使用文档
- [examples/basic_usage.py](examples/basic_usage.py) - 代码示例
- [quick_start.py](quick_start.py) - 交互式快速启动

## ⚖️ 免责声明

本系统仅提供技术分析辅助，不构成任何投资建议。
股市有风险，投资需谨慎。

---

**版本**: v1.0.0
**更新日期**: 2025-01-27
