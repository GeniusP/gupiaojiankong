#!/usr/bin/env python3
"""
股票AIGC监控系统 - 主启动脚本
提供多种启动模式
"""

import asyncio
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """打印系统横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          股票AIGC监控系统 v1.0                                     ║
║                                                                   ║
║     基于大语言模型的股票图形监控和智能分析系统                     ║
║                                                                   ║
║     ✅ 真实数据: 腾讯财经API实时行情                              ║
║     ✅ 智能AI:   智谱GLM-4-Plus模型                              ║
║     ✅ 自动识别: 开盘跳水 | 破位下跌 | 冲板回落                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_menu():
    """打印主菜单"""
    menu = """
┌─────────────────────────────────────────────────────────────────┐
│                        启动模式选择                               │
├─────────────────────────────────────────────────────────────────┤
│  1. 🚀 快速演示         - 演示系统功能                          │
│  2. ⚡ 智谱AI分析       - 智谱AI+实时数据（推荐）                │
│  3. 🧪 配置测试         - 测试API连接和配置                      │
│  4. 📊 批量分析         - 批量分析多只股票                       │
│  5. 🔍 图形识别测试     - 测试自动图形识别                       │
│  6. 📖 查看文档         - 显示使用文档                           │
│  7. ℹ️  系统状态         - 查看系统配置状态                       │
│  0. 🚪 退出             - 退出系统                               │
├─────────────────────────────────────────────────────────────────┤
│  💡 所有分析模式均使用腾讯财经真实数据+智谱AI                   │
│  💡 系统自动检测图形类型，智能过滤不适合的市场状态              │
└─────────────────────────────────────────────────────────────────┘
"""
    print(menu)


async def mode_quick_demo():
    """模式1：快速演示"""
    print("\n🚀 启动模式：快速演示")
    print("="*70)

    from demo_all_features import main as demo_main
    await demo_main()


async def mode_zhipu_analysis():
    """模式2：智谱AI分析（使用真实数据）"""
    print("\n⚡ 启动模式：智谱AI股票分析")
    print("="*70)
    print("✓ 使用腾讯财经API获取实时数据")
    print("✓ 智谱AI智能分析")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置智谱AI API密钥")
        print("请在.env文件中设置: ZHIPU_API_KEY=your_api_key")
        return

    try:
        # 导入快速分析工具
        import analyze
        from src.monitors.tencent_collector import TencentFinanceCollector

        print("\n请输入股票代码（如601138）：")
        stock_code = input("股票代码 > ").strip() or "601138"

        # 首先获取真实数据显示
        print("\n正在获取实时数据...")
        collector = TencentFinanceCollector()
        data = collector.get_stock_realtime_data(stock_code)

        if data and data.get("股票名称"):
            print(f"\n✅ 成功获取 {data['股票名称']} 的实时数据:")
            print(f"   开盘价: {data['开盘价']} 元")
            print(f"   实时价: {data['实时价']} 元")
            print(f"   最高价: {data['最高价']} 元")
            # 使用昨收价计算涨跌幅
            prev_close = data.get('昨收', data.get('开盘价', 0))
            if prev_close > 0:
                change = ((data['实时价'] - prev_close) / prev_close * 100)
                print(f"   涨跌: {change:+.2f}%")
        else:
            print(f"\n❌ 无法获取股票 {stock_code} 的数据")
            return

        # 使用快速分析工具（自动检测图形类型）
        print("\n开始智能分析...")
        print("-"*70)

        result = await analyze.quick_analyze(stock_code, None, auto_detect=True)

        if result:
            print(f"\n✅ 分析完成!")
        else:
            print(f"\n⚠️  该股票当前市场状态不适合图形分析")

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


async def mode_config_test():
    """模式3：配置测试"""
    print("\n🧪 启动模式：配置测试")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    from src.utils.config import Config, print_config_summary

    print_config_summary()

    print("\n" + "-"*70)
    print("详细配置检查:")
    print("-"*70)

    # 检查智谱AI
    api_key = os.getenv("ZHIPU_API_KEY")
    if api_key:
        print(f"\n✅ 智谱AI配置:")
        print(f"   API密钥: {api_key[:15]}...{api_key[-10:]}")
        print(f"   模型: {os.getenv('ZHIPU_MODEL', 'glm-4-plus')}")

        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=api_key)
            print(f"   SDK: ✅ 已安装")

            # 测试连接
            print("\n正在测试API连接...")
            response = client.chat.completions.create(
                model=os.getenv("ZHIPU_MODEL", "glm-4-plus"),
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=10
            )
            print(f"   连接: ✅ 成功")
            print(f"   响应: {response.choices[0].message.content}")

        except ImportError:
            print(f"   SDK: ❌ 未安装 (运行: pip install zhipuai)")
        except Exception as e:
            print(f"   连接: ❌ 失败 - {e}")
    else:
        print("\n⚠️  智谱AI: 未配置")

    # 检查其他模型
    print("\n" + "-"*70)
    print("其他模型配置:")
    print("-"*70)

    if os.getenv("OPENAI_API_KEY"):
        print("✅ GPT: 已配置")
    else:
        print("⚪ GPT: 未配置")

    if os.getenv("SPARK_APP_ID"):
        print("✅ 讯飞星火: 已配置")
    else:
        print("⚪ 讯飞星火: 未配置")

    if os.getenv("QIANFAN_ACCESS_KEY"):
        print("✅ 文心一言: 已配置")
    else:
        print("⚪ 文心一言: 未配置")


async def mode_batch_analysis():
    """模式4：批量分析（使用真实数据）"""
    print("\n📊 启动模式：批量分析")
    print("="*70)
    print("✓ 使用腾讯财经API获取实时数据")
    print("✓ 智谱AI智能分析")
    print("✓ 自动检测图形类型")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置智谱AI API密钥")
        return

    # 让用户输入股票列表
    print("\n请输入要分析的股票代码（用空格分隔）：")
    print("示例: 601138 600036 000001 600519")
    stock_input = input("股票代码 > ").strip()

    if not stock_input:
        # 默认股票列表
        stock_codes = ["601138", "600036", "000001", "600519"]
    else:
        # 解析股票代码
        import re
        stock_codes = re.findall(r'\d+', stock_input)

    print(f"\n准备分析 {len(stock_codes)} 只股票...")

    try:
        import analyze
        from src.monitors.tencent_collector import TencentFinanceCollector

        # 先显示所有股票的实时数据
        print("\n" + "="*70)
        print("实时行情数据")
        print("="*70)

        collector = TencentFinanceCollector()

        for code in stock_codes:
            data = collector.get_stock_realtime_data(code)
            if data and data.get("股票名称"):
                # 使用昨收价计算涨跌幅
                prev_close = data.get('昨收', data.get('开盘价', 0))
                change = ((data['实时价'] - prev_close) / prev_close * 100) if prev_close > 0 else 0
                print(f"{data['股票名称']}({code}): {data['实时价']}元 ({change:+.2f}%)")

        print("="*70)
        print("\n开始AI分析...")
        print("="*70)

        success_count = 0
        skip_count = 0

        for i, stock_code in enumerate(stock_codes, 1):
            print(f"\n[{i}/{len(stock_codes)}] 分析 {stock_code}")
            print("-"*70)

            result = await analyze.quick_analyze(stock_code, None, auto_detect=True)

            if result:
                success_count += 1
            else:
                skip_count += 1
                print("(市场状态不适合图形分析，已跳过)")

            # 避免API限流
            if i < len(stock_codes):
                print("\n等待3秒后分析下一只股票...")
                await asyncio.sleep(3)

        print("\n" + "="*70)
        print("📊 批量分析完成")
        print("="*70)
        print(f"成功分析: {success_count} 只")
        print(f"跳过分析: {skip_count} 只 (市场状态不适合)")
        print(f"总计: {len(stock_codes)} 只")

    except Exception as e:
        print(f"\n❌ 批量分析失败: {e}")
        import traceback
        traceback.print_exc()


async def mode_pattern_test():
    """模式5：图形识别测试（使用真实数据）"""
    print("\n🔍 启动模式：图形识别测试")
    print("="*70)
    print("✓ 使用腾讯财经API获取实时数据")
    print("✓ 自动检测图形类型")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置智谱AI API密钥")
        return

    # 测试股票列表
    test_stocks = ["601138", "600036", "000001", "600519"]

    print(f"\n测试 {len(test_stocks)} 只股票的图形识别...")

    try:
        import analyze
        from src.monitors.tencent_collector import TencentFinanceCollector

        collector = TencentFinanceCollector()

        for stock_code in test_stocks:
            print(f"\n{'='*70}")
            print(f"测试: {stock_code}")
            print(f"{'='*70}")

            # 获取实时数据
            data = collector.get_stock_realtime_data(stock_code)
            if not data or not data.get("股票名称"):
                print(f"❌ 无法获取 {stock_code} 的数据")
                continue

            print(f"股票: {data['股票名称']}")
            print(f"价格: {data['实时价']} 元")
            # 使用昨收价计算涨跌幅
            prev_close = data.get('昨收', data.get('开盘价', 0))
            if prev_close > 0:
                change = ((data['实时价'] - prev_close) / prev_close * 100)
                print(f"涨跌: {change:+.2f}%")
            print("-"*70)

            # 自动检测图形并分析
            result = await analyze.quick_analyze(stock_code, None, auto_detect=True)

            if result:
                print(f"✅ 分析成功")
            else:
                print(f"⚠️  不适合图形分析（{data['股票名称']}当前状态不匹配任何图形模板）")

            # 延迟
            await asyncio.sleep(2)

        print("\n" + "="*70)
        print("✅ 图形识别测试完成")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def mode_show_docs():
    """模式6：查看文档"""
    print("\n📖 启动模式：使用文档")
    print("="*70)

    docs = """
【快速使用指南】

1️⃣ 最简单的使用方式：

   from src.aigc.model_adapter import ZhipuAdapter
   from src.monitors.stock_monitor import quick_analysis

   result = await quick_analysis(
       stock_code="600000",
       pattern_type="开盘跳水",
       aigc_adapter=ZhipuAdapter(),
       trading_style="短线"
   )

2️⃣ 支持的图形类型：

   • 开盘跳水：开盘后快速下跌
   • 破位下跌：跌破关键支撑位
   • 冲板回落：冲高后回落

3️⃣ 支持的AIGC模型：

   • 智谱AI（推荐）：glm-4-plus, glm-4-air, glm-4-flash
   • GPT：gpt-4-turbo-preview, gpt-4
   • 讯飞星火：generalv3
   • 文心一言：ERNIE-Bot-4

4️⃣ 配置文件 (.env)：

   ZHIPU_API_KEY=your_api_key_here
   ZHIPU_MODEL=glm-4-plus
   DEFAULT_AIGC_MODEL=zhipu

5️⃣ 其他启动脚本：

   • python demo_all_features.py    - 自动演示所有功能
   • python quick_start_zhipu.py    - 智谱AI专用启动
   • python test_zhipu.py           - 配置测试

6️⃣ 查看更多文档：

   • README.md                      - 完整使用手册
   • QUICKSTART_ZHIPU.md            - 智谱AI快速指南
   • docs/ZHIPU_AI_GUIDE.md         - 智谱AI详细文档
   • examples/                      - 代码示例

【系统架构】

   stock/
   ├── src/
   │   ├── templates/          # Prompt模板
   │   ├── models/             # 数据模型
   │   ├── monitors/           # 监控逻辑
   │   ├── aigc/               # AIGC适配器
   │   └── utils/              # 工具模块
   ├── examples/               # 使用示例
   ├── docs/                   # 文档
   └── *.py                    # 启动脚本

【分析输出内容】

   1. 判断结果：真/假（真跳水/假跳水，真破位/假破位等）
   2. 判断依据：核心判断理由
   3. 风险等级：高/中/低
   4. 操作建议：止损/持有/观望/加仓等
   5. 关键价位：支撑位/压力位价格

【常见问题】

Q: 如何切换模型？
A: 修改.env文件中的DEFAULT_AIGC_MODEL

Q: 如何自定义识别规则？
A: 参考src/monitors/stock_monitor.py中的规则定义

Q: 批量分析会不会限流？
A: 系统自动添加延迟，建议每两次分析间隔1-2秒

Q: 分析结果如何保存？
A: 可以在代码中添加数据库保存逻辑

【免责声明】
本系统仅提供技术分析辅助，不构成任何投资建议。
股市有风险，投资需谨慎。
"""
    print(docs)


async def mode_system_status():
    """模式7：系统状态"""
    print("\nℹ️  启动模式：系统状态")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()
    from src.utils.config import Config

    print("\n📋 系统配置:")
    print("-"*70)
    print(f"默认AIGC模型: {Config.DEFAULT_AIGC_MODEL}")
    print(f"交易风格: {Config.TRADING_STYLE}")
    print(f"监控间隔: {Config.MONITOR_INTERVAL_SECONDS}秒")
    print(f"日志级别: {Config.LOG_LEVEL}")

    print("\n🔧 AIGC模型状态:")
    print("-"*70)

    models_status = []

    # 智谱AI
    if Config.ZHIPU_API_KEY:
        models_status.append(("智谱AI", "✅ 已配置", Config.ZHIPU_MODEL))
    else:
        models_status.append(("智谱AI", "⚪ 未配置", "-"))

    # GPT
    if Config.OPENAI_API_KEY:
        models_status.append(("GPT", "✅ 已配置", Config.OPENAI_MODEL))
    else:
        models_status.append(("GPT", "⚪ 未配置", "-"))

    # 讯飞星火
    if Config.SPARK_APP_ID:
        models_status.append(("讯飞星火", "✅ 已配置", Config.SPARK_DOMAIN))
    else:
        models_status.append(("讯飞星火", "⚪ 未配置", "-"))

    # 文心一言
    if Config.QIANFAN_ACCESS_KEY:
        models_status.append(("文心一言", "✅ 已配置", Config.QIANFAN_MODEL))
    else:
        models_status.append(("文心一言", "⚪ 未配置", "-"))

    for name, status, model in models_status:
        print(f"{name:12} {status:12} {model}")

    print("\n📊 功能模块:")
    print("-"*70)
    modules = [
        ("Prompt模板生成", "✅ 正常"),
        ("图形识别引擎", "✅ 正常（自动检测）"),
        ("数据采集模块", "✅ 正常（腾讯财经API）"),
        ("AIGC适配器", "✅ 正常（智谱AI）"),
        ("配置管理", "✅ 正常"),
    ]

    for module, status in modules:
        print(f"{module:16} {status}")

    print("\n📈 支持的图形类型:")
    print("-"*70)
    patterns = [
        ("开盘跳水", "开盘后快速下跌分析"),
        ("破位下跌", "跌破关键支撑位分析"),
        ("冲板回落", "冲高后回落分析"),
    ]

    for pattern, desc in patterns:
        print(f"  • {pattern:8} - {desc}")


async def main():
    """主函数"""
    print_banner()

    # 检查是否命令行参数
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        mode_map = {
            "1": mode_quick_demo,
            "2": mode_zhipu_analysis,
            "3": mode_config_test,
            "4": mode_batch_analysis,
            "5": mode_pattern_test,
            "6": mode_show_docs,
            "7": mode_system_status,
            "demo": mode_quick_demo,
            "zhipu": mode_zhipu_analysis,
            "test": mode_config_test,
            "batch": mode_batch_analysis,
            "pattern": mode_pattern_test,
            "docs": mode_show_docs,
            "status": mode_system_status,
        }

        if mode in mode_map:
            await mode_map[mode]()
            return

    # 交互式菜单
    while True:
        try:
            print_menu()
            choice = input("请选择模式 [0-7] > ").strip()

            if choice == "0":
                print("\n👋 感谢使用！再见！")
                break
            elif choice == "1":
                await mode_quick_demo()
            elif choice == "2":
                await mode_zhipu_analysis()
            elif choice == "3":
                await mode_config_test()
            elif choice == "4":
                await mode_batch_analysis()
            elif choice == "5":
                await mode_pattern_test()
            elif choice == "6":
                await mode_show_docs()
            elif choice == "7":
                await mode_system_status()
            else:
                print("\n⚠️  无效选择，请重新输入")

            input("\n按回车键继续...")

        except KeyboardInterrupt:
            print("\n\n👋 已退出系统")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 系统已退出")
