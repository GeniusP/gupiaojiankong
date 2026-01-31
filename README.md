# 股票AIGC监控系统

基于大语言模型的股票图形监控和分析系统，支持**开盘跳水、破位下跌、冲板回落**三类核心场景的自动识别、误触发甄别、风险分析和操作建议生成。

## ✨ 核心特性

- 🎯 **三种核心图形识别**：开盘跳水、破位下跌、冲板回落
- 🤖 **多模型支持**：适配讯飞星火、GPT、文心一言、智谱AI等主流大模型
- 📊 **结构化数据采集**：自动整合行情、成交量、市场环境等多维数据
- 🔄 **双模板模式**：完整版（深度分析）+ 简化版（快速响应）
- ⚡ **即插即用**：提供Prompt模板、监控逻辑、AIGC接口完整封装

## 📋 系统架构

```
stock/
├── src/
│   ├── templates/          # Prompt模板管理器
│   │   └── prompt_templates.py
│   ├── models/             # 数据模型定义
│   │   └── stock_data.py
│   ├── monitors/           # 监控逻辑
│   │   ├── data_collector.py    # 数据采集
│   │   └── stock_monitor.py      # 图形识别与触发
│   ├── aigc/               # AIGC模型适配器
│   │   └── model_adapter.py
│   └── utils/              # 工具模块
│       └── config.py
├── examples/               # 使用示例
│   └── basic_usage.py
├── requirements.txt        # 依赖列表
├── .env.example           # 配置文件模板
└── README.md              # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 根据使用的模型安装对应SDK

# GPT
pip install openai

# 讯飞星火
pip install spark-ai

# 文心一言（百度千帆）
pip install qianfan

# 智谱AI（ChatGLM）- 推荐
pip install zhipuai
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# 例如配置GPT:
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_AIGC_MODEL=gpt
TRADING_STYLE=short
```

### 3. 运行示例

```bash
cd examples
python basic_usage.py
```

## 📖 使用指南

### 方式1：直接使用Prompt模板

适合已有数据采集系统，只需Prompt模板的场景。

```python
from src.templates.prompt_templates import generate_prompt

# 准备股票数据
stock_data = {
    "股票代码": "600000",
    "股票名称": "浦发银行",
    "触发时间": "09:35",
    "开盘分钟数": 5,
    "跌幅": 3.2,
    "均线类型": 5,
    "均线价格": 10.30,
    "成交额放大比例": 35.5,
    "板块名称": "银行",
    "板块涨跌幅": -1.2,
    "大盘涨跌幅": -0.8,
    "最新消息": "无"
}

# 生成Prompt（简化版）
prompt = generate_prompt(
    chart_type="开盘跳水",
    stock_data=stock_data,
    trading_style="短线",
    template_type="简化版"  # 或"完整版"
)

print(prompt)
# 输出: 股票600000 浦发银行，09:35开盘5分钟跌3.2%，跌破5日均线10.30...
```

### 方式2：快速分析（适合快速调用）

```python
import asyncio
from src.aigc.model_adapter import MockAIGCAdapter
from src.monitors.stock_monitor import quick_analysis

async def main():
    # 使用Mock适配器测试，实际使用替换为真实适配器
    result = await quick_analysis(
        stock_code="600000",
        pattern_type="开盘跳水",
        aigc_adapter=MockAIGCAdapter(),
        trading_style="短线",
        开盘分钟数=5,
        跌幅=3.2
    )

    print(result)

asyncio.run(main())
```

### 方式3：完整监控流程

适合生产环境，包含自动数据采集、图形识别、AIGC分析全流程。

```python
import asyncio
from src.monitors.data_collector import MockDataCollector, StockDataAggregator
from src.aigc.model_adapter import create_adapter, ModelProvider, AIGCService
from src.monitors.stock_monitor import StockPatternMonitor, PatternType, TradingStyle

async def main():
    # 1. 创建数据采集器（实际使用替换为真实数据源）
    data_aggregator = StockDataAggregator(MockDataCollector())

    # 2. 创建AIGC服务（使用GPT）
    adapter = create_adapter(
        ModelProvider.GPT,
        api_key="your_openai_api_key",
        model="gpt-4-turbo-preview"
    )
    aigc_service = AIGCService(adapter)

    # 3. 创建监控器
    monitor = StockPatternMonitor(
        data_aggregator=data_aggregator,
        aigc_service=aigc_service,
        trading_style=TradingStyle.SHORT
    )

    # 4. 执行监控分析
    trigger_event = await monitor.analyze_pattern(
        stock_code="600000",
        pattern_type=PatternType.OPENING_DIVE,
        position_status="已持仓",
        trigger_time="09:35",
        开盘分钟数=5,
        跌幅=3.2
    )

    if trigger_event:
        print(f"触发事件: {trigger_event.事件ID}")
        print(f"AIGC分析: {trigger_event.AIGC分析结果.原始回复}")

asyncio.run(main())
```

## 🎨 三种图形类型

### 1. 开盘跳水

**识别规则**：
- 开盘5分钟内跌幅超3%
- 开盘10分钟内跌幅超2%
- 跌破5日/20日均线

**分析重点**：
- ✓ 真假跳水甄别（主动出逃 vs 被动下跌）
- ✓ 风险等级判定（高/中/低）
- ✓ 操作建议（规避/持有/止损）

### 2. 破位下跌

**识别规则**：
- 跌破5日/20日均线且放量（>20%）
- 跌破前期平台支撑位且3分钟未回弹

**分析重点**：
- ✓ 真假破位判断（趋势走坏 vs 洗盘误杀）
- ✓ 下跌原因分析（资金面/板块/消息面）
- ✓ 短期走势预判（反弹/继续下跌/横盘）

### 3. 冲板回落

**识别规则**：
- 冲至涨停板后回落超5%
- 冨高超8%后回落超3%

**分析重点**：
- ✓ 抛压强度判断（强/中/弱）
- ✓ 核心原因分析（抛压过大/主力诱多/资金分流）
- ✓ 后续走势影响（偏空/中性/偏多）

## 🔧 配置说明

### AIGC模型配置

支持的模型：

| 模型 | 说明 | 配置字段 |
|------|------|---------|
| **GPT** | OpenAI GPT系列 | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` |
| **讯飞星火** | 科大讯飞星火认知大模型 | `SPARK_APP_ID`, `SPARK_API_KEY`, `SPARK_API_SECRET` |
| **文心一言** | 百度千帆大模型平台 | `QIANFAN_ACCESS_KEY`, `QIANFAN_SECRET_KEY` |
| **智谱AI** | 智谱AI ChatGLM系列（推荐） | `ZHIPU_API_KEY`, `ZHIPU_MODEL` |

### 交易风格配置

- `short` - 短线交易（日内或T+1）
- `medium` - 波段交易（数天至数周）
- `long` - 长线交易（数月至数年）

### 模板类型

- **完整版**：深度分析，输出150字左右，包含详细判断依据和理由
- **简化版**：快速响应，输出50字左右，核心结论为主

## 📊 数据字段说明

### 必填字段

```python
{
    "股票代码": "600000",
    "股票名称": "浦发银行",
    "触发时间": "09:35",
    "图形类型": "开盘跳水"  # 或"破位下跌"、"冲板回落"
}
```

### 行情数据

```python
{
    "开盘价": 10.50,
    "实时价": 10.20,
    "最高价": 10.50,
    "涨停价": 11.55,
    "5日均线": 10.30,
    "20日均线": 10.15,
    "前期平台支撑位": 10.00
}
```

### 成交量数据

```python
{
    "触发成交额": 12500,          # 万元
    "成交额放大比例": 35.5,       # 较前5日均值的放大比例%
    "当日成交额放大比例": 20.3,   # 较当日均值的放大比例%
    "分钟成交额放大比例": 50.0    # 较前1分钟的放大比例%
}
```

### 市场环境

```python
{
    "板块名称": "银行",
    "板块涨跌幅": -1.2,           # %
    "大盘名称": "上证指数",
    "大盘涨跌幅": -0.8,           # %
    "最新消息": "无"              # 或具体消息内容
}
```

### 图形专属字段

**开盘跳水**：
```python
{
    "开盘分钟数": 5,
    "跌幅": 3.2,
    "均线类型": 5,      # 5或20
    "均线价格": 10.30
}
```

**破位下跌**：
```python
{
    "支撑位价格": 10.00,
    "破位后未回弹分钟数": 5
}
```

**冲板回落**：
```python
{
    "涨幅": 9.8,
    "回落幅度": 5.2,
    "封板挂单量": 15000
}
```

## 🔄 工作流程

```
┌─────────────────┐
│  采集股票数据    │
│ (行情/成交量/   │
│  板块/大盘/消息)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  图形识别检测    │
│ (开盘跳水/      │
│  破位下跌/      │
│  冲板回落)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  生成结构化Prompt│
│ (完整版/简化版)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  调用AIGC分析    │
│ (讯飞星火/GPT/  │
│  文心一言)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  输出分析结果    │
│ (判断/风险/     │
│  操作建议)      │
└─────────────────┘
```

## 💡 最佳实践

### 1. 数据质量控制

- ✓ 确保数据字段完整性，缺失字段填"无"或0
- ✓ 成交额放大比例需准确计算（基准为前5日均值）
- ✓ 触发时间格式统一为"HH:MM"

### 2. Prompt选择策略

- **实时监控**：使用简化版模板，响应速度优先
- **深度分析**：使用完整版模板，分析质量优先
- **批量处理**：建议使用简化版，避免token消耗过大

### 3. 模型选择建议

- **国内使用**：推荐智谱AI（glm-4-flash），速度快且效果好
- **国际使用**：选择GPT-4，分析质量更优
- **成本敏感**：智谱AI性价比最高，文心一言次之
- **快速响应**：智谱AI glm-4-flash或讯飞星火

### 4. 错误处理

```python
try:
    result = await monitor.analyze_pattern(
        stock_code="600000",
        pattern_type=PatternType.OPENING_DIVE
    )
except Exception as e:
    print(f"分析失败: {e}")
    # 降级处理：使用规则引擎或人工复核
```

## 🛠️ 扩展开发

### 自定义数据采集器

```python
from src.monitors.data_collector import DataCollector

class MyDataCollector(DataCollector):
    def get_stock_realtime_data(self, stock_code: str):
        # 实现你的数据采集逻辑
        return {...}

    def get_sector_data(self, sector_name: str):
        # 实现板块数据采集
        return {...}

    def get_market_index_data(self, index_name: str):
        # 实现大盘数据采集
        return {...}
```

### 自定义识别规则

```python
from src.monitors.stock_monitor import PatternRule

# 添加自定义规则
custom_rule = PatternRule(
    name="自定义规则",
    condition=lambda data: your_logic_here(data),
    description="规则描述"
)

monitor.opening_dive_rules.append(custom_rule)
```

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至项目维护者

---

**免责声明**：本系统仅提供技术分析辅助，不构成任何投资建议。股市有风险，投资需谨慎。
# gupiaojiankong
