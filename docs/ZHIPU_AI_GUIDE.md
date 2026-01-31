# 智谱AI（ChatGLM）快速开始指南

## 📌 为什么选择智谱AI？

- ✅ **国内模型**：无需翻墙，访问稳定
- ✅ **速度快**：glm-4-flash 响应迅速，适合实时监控
- ✅ **效果好**：ChatGLM系列模型在中文场景表现优异
- ✅ **性价比高**：价格远低于GPT，新用户有免费额度
- ✅ **简单易用**：API兼容OpenAI格式，集成方便

## 🚀 快速开始

### 步骤1：获取API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入 [API密钥管理页面](https://open.bigmodel.cn/usercenter/apikeys)
4. 创建新的API密钥
5. 复制密钥（格式：`id.secret`，例如：`1234.abcdefg1234567890`）

### 步骤2：安装SDK

```bash
pip install zhipuai
```

### 步骤3：配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 复制配置模板
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 智谱AI配置
ZHIPU_API_KEY=your_api_key_here  # 替换为你的API密钥
ZHIPU_MODEL=glm-4-flash          # 推荐使用快速响应模型

# 设置为默认模型
DEFAULT_AIGC_MODEL=zhipu
```

### 步骤4：测试连接

运行快速测试：

```bash
cd examples
python zhipu_example.py
```

或使用Python交互式测试：

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="your_api_key")
response = client.chat.completions.create(
    model="glm-4-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

## 💡 模型选择指南

智谱AI提供以下模型：

| 模型 | 特点 | 适用场景 | 推荐度 |
|------|------|---------|--------|
| **glm-4-plus** | 最强模型 | 复杂分析、深度研究 | ⭐⭐⭐⭐ |
| **glm-4-air** | 高性价比 | 日常使用、批量分析 | ⭐⭐⭐⭐⭐ |
| **glm-4-flash** | 快速响应 | 实时监控、快速响应 | ⭐⭐⭐⭐⭐ |
| **glm-3-turbo** | 低成本 | 简单任务、测试开发 | ⭐⭐⭐ |

**推荐配置**：
- 股票监控系统：`glm-4-flash`（速度快，足够好）
- 深度分析场景：`glm-4-air`（性价比高）
- 复杂研究场景：`glm-4-plus`（最强性能）

## 📖 使用示例

### 示例1：基础使用

```python
import asyncio
from src.aigc.model_adapter import ZhipuAdapter, AIGCService
from src.templates.prompt_templates import generate_prompt

async def analyze_stock():
    # 创建智谱AI适配器
    adapter = ZhipuAdapter(
        api_key="your_api_key",
        model="glm-4-flash"
    )

    # 创建服务
    service = AIGCService(adapter)

    # 生成Prompt
    prompt = generate_prompt(
        chart_type="开盘跳水",
        stock_data={
            "股票代码": "600000",
            "股票名称": "浦发银行",
            "触发时间": "09:35",
            "开盘分钟数": 5,
            "跌幅": 3.2,
            "成交额放大比例": 35.5,
            "板块名称": "银行",
            "板块涨跌幅": -1.2,
            "大盘涨跌幅": -0.8
        },
        trading_style="短线"
    )

    # 调用分析
    result = await service.async_analyze_stock_pattern(prompt)
    print(result)

asyncio.run(analyze_stock())
```

### 示例2：使用快速分析函数

```python
from src.monitors.stock_monitor import quick_analysis
from src.aigc.model_adapter import ZhipuAdapter

async def quick_test():
    result = await quick_analysis(
        stock_code="600000",
        pattern_type="开盘跳水",
        aigc_adapter=ZhipuAdapter(api_key="your_api_key"),
        trading_style="短线",
        开盘分钟数=5,
        跌幅=3.2
    )
    print(result)

asyncio.run(quick_test())
```

### 示例3：集成到监控流程

```python
from src.aigc.model_adapter import create_adapter, ModelProvider, AIGCService
from src.monitors.stock_monitor import StockPatternMonitor, PatternType
from src.monitors.data_collector import MockDataCollector, StockDataAggregator

async def main():
    # 创建智谱AI适配器
    adapter = create_adapter(
        ModelProvider.ZHIPU,
        api_key="your_api_key",
        model="glm-4-flash"
    )

    # 创建监控器
    aggregator = StockDataAggregator(MockDataCollector())
    aigc_service = AIGCService(adapter)
    monitor = StockPatternMonitor(aggregator, aigc_service)

    # 执行监控
    trigger_event = await monitor.analyze_pattern(
        stock_code="600000",
        pattern_type=PatternType.OPENING_DIVE
    )

    if trigger_event:
        print(f"触发事件: {trigger_event.事件ID}")
        print(f"分析结果: {trigger_event.AIGC分析结果.原始回复}")

asyncio.run(main())
```

## 🔧 高级配置

### 使用不同的模型

```python
# 快速响应（推荐）
adapter = ZhipuAdapter(api_key="your_key", model="glm-4-flash")

# 高性价比
adapter = ZhipuAdapter(api_key="your_key", model="glm-4-air")

# 最强性能
adapter = ZhipuAdapter(api_key="your_key", model="glm-4-plus")
```

### 调整参数

```python
service = AIGCService(adapter)

# 自定义温度和token限制
result = adapter.chat(
    prompt="你的prompt",
    temperature=0.3,  # 0.0-1.0，越低越确定性
    max_tokens=500    # 最大输出token数
)
```

## 💰 费用说明

智谱AI采用按量计费：

- **glm-4-flash**: ¥0.1/千tokens（输入）
- **glm-4-air**: ¥1/千tokens（输入）
- **glm-4-plus**: ¥5/千tokens（输入）

**预估成本**：
- 每次股票分析约消耗 200-300 tokens
- 使用 glm-4-flash，单次成本约 ¥0.02-0.03
- 1000次分析成本约 ¥20-30

**免费额度**：
- 新用户通常有免费额度
- 具体以官方公告为准

## ⚠️ 常见问题

### Q1: API密钥格式错误？

确保API密钥格式为 `id.secret`，例如：`1234.abcdefg1234567890`

### Q2: 调用超时怎么办？

```python
# 增加超时时间
import zhipuai
client = zhipuai.ZhipuAI(
    api_key="your_key",
    timeout=60  # 增加到60秒
)
```

### Q3: 如何避免限流？

```python
import asyncio

# 批量分析时添加延迟
for stock in stocks:
    result = await analyze(stock)
    await asyncio.sleep(1)  # 每次间隔1秒
```

### Q4: 返回结果为空？

检查：
1. API密钥是否正确
2. 账户是否有余额
3. 模型名称是否正确

## 📚 更多资源

- [智谱AI官方文档](https://open.bigmodel.cn/dev/api)
- [模型对比](https://open.bigmodel.cn/pricing)
- [Python SDK](https://github.com/MetaGLM/ChatGLM)
- [系统完整文档](../README.md)

## 🎯 最佳实践

1. **模型选择**：日常监控使用 `glm-4-flash`，深度分析使用 `glm-4-air`
2. **错误处理**：添加重试机制处理临时故障
3. **成本控制**：使用简化版模板减少token消耗
4. **性能优化**：批量分析时控制并发数

```python
# 完整示例：带错误处理和重试
async def analyze_with_retry(stock_code, max_retries=3):
    adapter = ZhipuAdapter(api_key="your_key", model="glm-4-flash")

    for attempt in range(max_retries):
        try:
            result = await quick_analysis(
                stock_code=stock_code,
                pattern_type="开盘跳水",
                aigc_adapter=adapter
            )
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避

    return None
```

---

**下一步**：运行 [智谱AI示例](../examples/zhipu_example.py) 体验完整功能！
