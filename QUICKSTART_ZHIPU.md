# 智谱AI快速使用指南

## ✅ 已配置信息

您的智谱AI配置已自动设置：

- **API密钥**：3390dd1e38a3...bXcRz1ypULpn4uOp
- **使用模型**：glm-4-plus（最新最强模型）
- **默认模型**：zhipu（系统将优先使用智谱AI）

## 🚀 快速开始（3步）

### 步骤1：安装SDK

```bash
pip install zhipuai
```

### 步骤2：测试配置

```bash
python test_zhipu.py
```

这将验证：
- ✓ API密钥是否有效
- ✓ 模型连接是否正常
- ✓ 完整的股票分析流程

### 步骤3：开始使用

#### 方式A：使用测试脚本（推荐）

```bash
python test_zhipu.py
```

#### 方式B：使用完整示例

```bash
cd examples
python zhipu_example.py
```

#### 方式C：快速启动

```bash
python quick_start.py
```

## 💡 代码示例

### 示例1：快速分析（最简单）

```python
import asyncio
from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.stock_monitor import quick_analysis

async def main():
    result = await quick_analysis(
        stock_code="600000",
        pattern_type="开盘跳水",
        aigc_adapter=ZhipuAdapter(),  # 自动从.env读取配置
        trading_style="短线",
        开盘分钟数=5,
        跌幅=3.2
    )
    print(result)

asyncio.run(main())
```

### 示例2：完整监控流程

```python
import asyncio
from src.aigc.model_adapter import create_adapter, ModelProvider, AIGCService
from src.monitors.stock_monitor import StockPatternMonitor, PatternType
from src.monitors.data_collector import MockDataCollector, StockDataAggregator

async def main():
    # 从环境变量自动加载配置
    from src.utils.config import Config

    # 创建智谱AI适配器
    adapter = create_adapter(
        ModelProvider.ZHIPU,
        **Config.get_model_config(ModelProvider.ZHIPU)
    )

    # 创建监控器
    aggregator = StockDataAggregator(MockDataCollector())
    aigc_service = AIGCService(adapter)
    monitor = StockPatternMonitor(aggregator, aigc_service)

    # 执行分析
    result = await monitor.analyze_pattern(
        stock_code="600000",
        pattern_type=PatternType.OPENING_DIVE
    )

    if result:
        print(f"分析结果: {result.AIGC分析结果.原始回复}")

asyncio.run(main())
```

### 示例3：仅使用Prompt模板

```python
from src.templates.prompt_templates import generate_prompt

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

# 调用智谱AI
from zhipuai import ZhipuAI
client = ZhipuAI()  # 自动从.env读取配置
response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[{"role": "user", "content": prompt}]
)
print(response.choices[0].message.content)
```

## 📊 支持的图形类型

| 图形类型 | 图形名称 | 说明 |
|---------|---------|------|
| `开盘跳水` | 开盘跳水 | 开盘后快速下跌 |
| `破位下跌` | 破位下跌 | 跌破关键支撑位 |
| `冲板回落` | 冲板回落 | 冲高后回落 |

## 🔧 配置说明

您的 `.env` 文件配置：

```bash
# 智谱AI配置
ZHIPU_API_KEY=''
ZHIPU_MODEL=glm-4-plus  # 最强模型
DEFAULT_AIGC_MODEL=zhipu  # 默认使用智谱AI
```

### 切换模型

如果想使用其他模型，修改 `.env` 文件中的 `ZHIPU_MODEL`：

```bash
# 快速响应（推荐实时监控）
ZHIPU_MODEL=glm-4-flash

# 高性价比（推荐日常使用）
ZHIPU_MODEL=glm-4-air

# 最强性能（当前配置）
ZHIPU_MODEL=glm-4-plus

# 低成本（测试开发）
ZHIPU_MODEL=glm-3-turbo
```

## 📈 模型对比

| 模型 | 速度 | 质量 | 成本 | 推荐场景 |
|------|------|------|------|---------|
| **glm-4-flash** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ¥ | 实时监控 |
| **glm-4-air** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ¥¥ | 日常使用 |
| **glm-4-plus** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ¥¥¥ | 深度分析 |
| **glm-3-turbo** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ¥ | 测试开发 |

## 🎯 下一步

1. **运行测试**：`python test_zhipu.py`
2. **查看示例**：`python examples/zhipu_example.py`
3. **阅读文档**：`docs/ZHIPU_AI_GUIDE.md`
4. **开始监控**：根据实际需求集成到您的系统

## ❓ 常见问题

### Q: 如何查看账户余额和使用量？

访问：https://open.bigmodel.cn/usercenter/balance

### Q: API调用失败怎么办？

1. 检查网络连接
2. 验证API密钥是否正确
3. 查看账户余额是否充足
4. 运行 `python test_zhipu.py` 诊断

### Q: 如何限制调用成本？

- 使用 `glm-4-flash` 或 `glm-3-turbo` 降低成本
- 使用简化版模板减少token消耗
- 添加调用频率限制

### Q: 支持批量分析吗？

是的，示例代码：

```python
stocks = ["600000", "000001", "600036"]

for stock in stocks:
    result = await quick_analysis(
        stock_code=stock,
        pattern_type="开盘跳水",
        aigc_adapter=ZhipuAdapter()
    )
    print(f"{stock}: {result}")
    await asyncio.sleep(1)  # 避免限流
```

## 📞 获取帮助

- **智谱AI文档**：https://open.bigmodel.cn/dev/api
- **系统文档**：[README.md](README.md)
- **快速指南**：[docs/ZHIPU_AI_GUIDE.md](docs/ZHIPU_AI_GUIDE.md)

---

**开始使用**：运行 `python test_zhipu.py` 测试您的配置！
