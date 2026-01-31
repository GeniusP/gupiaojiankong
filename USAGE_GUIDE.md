# 🚀 股票AIGC监控系统 - 使用指南

## ✅ 系统已启动成功！

您的系统已完全配置并测试通过：
- ✅ 智谱AI API连接正常
- ✅ 所有功能模块正常
- ✅ Prompt模板工作正常
- ✅ 图形识别功能正常

## 📝 如何使用系统

### ⚠️ 重要提示

`start.py` 是**交互式脚本**，需要在**终端**中运行，不能在bash中直接运行！

### 方式1：在终端中运行（推荐）

1. 打开**终端**（Terminal）
2. 进入项目目录：
   ```bash
   cd /Users/xufengyu/Desktop/Ai/stock
   ```
3. 运行启动脚本：
   ```bash
   python3 start.py
   ```
4. 使用键盘选择菜单选项（输入0-7）

### 方式2：使用命令行参数（推荐）

在终端或bash中运行：

```bash
# 查看系统状态
python3 start.py status

# 快速演示
python3 start.py demo

# 配置测试
python3 start.py test

# 查看文档
python3 start.py docs

# 智谱AI分析（会要求输入股票代码）
python3 start.py zhipu

# 批量分析
python3 start.py batch

# 图形识别测试
python3 start.py pattern
```

## 🎯 快速开始示例

### 示例1：分析单只股票

创建文件 `analyze.py`：

```python
import asyncio
from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.stock_monitor import quick_analysis

async def main():
    result = await quick_analysis(
        stock_code="600000",           # 浦发银行
        pattern_type="开盘跳水",        # 图形类型
        aigc_adapter=ZhipuAdapter(),   # 使用智谱AI
        trading_style="短线",          # 交易风格
        开盘分钟数=5,
        跌幅=3.2
    )

    if result:
        print(f"分析结果:\n{result}")

asyncio.run(main())
```

运行：
```bash
python3 analyze.py
```

### 示例2：查看系统状态

```bash
python3 start.py status
```

输出：
```
智谱AI         ✅ 已配置        glm-4-plus
GPT            ⚪ 未配置        -
讯飞星火          ⚪ 未配置        -
文心一言          ⚪ 未配置        -
```

### 示例3：测试API连接

```bash
python3 start.py test
```

输出：
```
✅ 智谱AI配置:
   API密钥: 3390dd1e38a349f...ypULpn4uOp
   模型: glm-4-plus
   SDK: ✅ 已安装
正在测试API连接...
   连接: ✅ 成功
```

## 📊 可用的启动脚本

| 脚本 | 用途 | 运行方式 |
|------|------|---------|
| `start.py` | **主启动脚本** | `python3 start.py` (终端)<br>`python3 start.py status` (命令行) |
| `quick_start_zhipu.py` | 智谱AI快速启动 | `python3 quick_start_zhipu.py` |
| `demo_all_features.py` | 自动演示所有功能 | `python3 demo_all_features.py` |
| `test_zhipu.py` | 配置测试 | `python3 test_zhipu.py` |

## 💡 常用命令

```bash
# 查看系统状态
python3 start.py status

# 测试配置
python3 start.py test

# 快速演示
python3 start.py demo

# 查看文档
python3 start.py docs

# 智谱AI分析（交互式）
python3 start.py zhipu

# 自动演示
python3 demo_all_features.py

# 智谱AI快速启动
python3 quick_start_zhipu.py
```

## 🔧 如果想使用交互式菜单

在**终端**（Terminal）中运行：

```bash
cd /Users/xufengyu/Desktop/Ai/stock
python3 start.py
```

然后您会看到菜单：

```
┌─────────────────────────────────────────────────────────────────┐
│                        启动模式选择                               │
├─────────────────────────────────────────────────────────────────┤
│  1. 🚀 快速演示         - 自动演示所有功能（推荐新用户）         │
│  2. ⚡ 智谱AI分析       - 使用智谱AI分析股票                     │
│  3. 🧪 配置测试         - 测试API连接和配置                      │
│  4. 📊 批量分析         - 批量分析多个股票                       │
│  5. 🔍 图形识别测试     - 测试图形识别功能                       │
│  6. 📖 查看文档         - 显示使用文档                           │
│  7. ℹ️  系统状态         - 查看系统配置状态                       │
│  0. 🚪 退出             - 退出系统                               │
└─────────────────────────────────────────────────────────────────┘
```

输入数字选择对应的功能。

## 📚 更多资源

- [README.md](README.md) - 完整使用手册
- [QUICKSTART_ZHIPU.md](QUICKSTART_ZHIPU.md) - 智谱AI快速指南
- [docs/ZHIPU_AI_GUIDE.md](docs/ZHIPU_AI_GUIDE.md) - 智谱AI详细文档
- [examples/](examples/) - 代码示例

## ❓ 常见问题

### Q: 为什么不能直接运行 `python start.py`？

A: 因为它是交互式脚本，需要在终端中运行才能接收键盘输入。或者使用命令行参数（如 `python start.py status`）。

### Q: 如何快速分析股票？

A: 使用 `quick_start_zhipu.py` 或创建自己的分析脚本（见上面的示例1）。

### Q: 系统支持哪些功能？

A:
- ✅ 三种图形分析（开盘跳水、破位下跌、冲板回落）
- ✅ 智谱AI智能分析
- ✅ 批量分析
- ✅ 配置测试
- ✅ 文档查看

## 🎉 系统已就绪！

选择任意方式开始使用：

```bash
# 方式1：查看状态
python3 start.py status

# 方式2：快速演示
python3 start.py demo

# 方式3：智谱AI分析
python3 quick_start_zhipu.py

# 方式4：查看文档
python3 start.py docs
```

**开始分析股票吧！** 🚀
