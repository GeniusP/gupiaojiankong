# 🚀 立即开始使用

## ✅ 您的配置已就绪

- **API密钥**：已配置 ✓
- **模型**：glm-4-plus（最强性能）✓
- **默认模型**：zhipu ✓

## 📝 2步快速开始

### 步骤1：安装SDK（如果还没安装）

```bash
pip install zhipuai
```

### 步骤2：运行快速开始脚本

```bash
python quick_start_zhipu.py
```

这将立即分析2个股票案例，展示系统功能！

## 🎯 其他启动方式

### 方式1：完整测试（推荐）
```bash
python test_zhipu.py
```

### 方式2：智谱AI专用示例
```bash
cd examples
python zhipu_example.py
```

### 方式3：交互式快速启动
```bash
python quick_start.py
```

## 💡 快速代码示例

```python
import asyncio
from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.stock_monitor import quick_analysis

async def main():
    result = await quick_analysis(
        stock_code="600000",
        pattern_type="开盘跳水",
        aigc_adapter=ZhipuAdapter(),  # 自动读取.env配置
        trading_style="短线",
        开盘分钟数=5,
        跌幅=3.2
    )
    print(result)

asyncio.run(main())
```

## 📚 更多文档

- [快速开始指南](QUICKSTART_ZHIPU.md)
- [智谱AI详细指南](docs/ZHIPU_AI_GUIDE.md)
- [完整文档](README.md)

---

**现在就运行：`python quick_start_zhipu.py`** 🎉
