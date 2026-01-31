#!/usr/bin/env python3
"""
智谱AI快速开始脚本
立即测试您的配置！
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("\n" + "="*70)
    print(" " * 15 + "🚀 智谱AI股票分析 - 快速开始")
    print("="*70)

    # 加载配置
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    model = os.getenv("ZHIPU_MODEL", "glm-4-plus")

    print(f"\n📋 配置信息:")
    print(f"   模型: {model}")
    print(f"   API密钥: {api_key[:15]}...{api_key[-10:] if api_key else 'None'}")

    if not api_key:
        print("\n❌ 未配置API密钥！")
        return

    # 检查SDK
    try:
        import zhipuai
        print("   SDK: ✓ 已安装")
    except ImportError:
        print("   SDK: ✗ 未安装")
        print("\n⚠️  请先安装SDK:")
        print("   pip install zhipuai")
        return

    print("\n" + "-"*70)
    print("开始分析股票...")
    print("-"*70)

    try:
        from src.aigc.model_adapter import ZhipuAdapter, AIGCService
        from src.monitors.stock_monitor import quick_analysis

        # 创建适配器
        adapter = ZhipuAdapter(api_key=api_key, model=model)

        # 测试案例1：开盘跳水
        print("\n【案例1】浦发银行 - 开盘跳水分析")
        print("-"*70)

        result1 = await quick_analysis(
            stock_code="600000",
            pattern_type="开盘跳水",
            aigc_adapter=adapter,
            trading_style="短线",
            trigger_time="09:35",
            开盘分钟数=5,
            跌幅=3.2,
            均线类型=5,
            均线价格=10.30,
            成交额放大比例=35.5,
            板块名称="银行",
            板块涨跌幅=-1.2,
            大盘涨跌幅=-0.8
        )

        print(f"\n{result1}\n")

        # 等待一下避免限流
        await asyncio.sleep(2)

        # 测试案例2：破位下跌
        print("\n【案例2】平安银行 - 破位下跌分析")
        print("-"*70)

        result2 = await quick_analysis(
            stock_code="000001",
            pattern_type="破位下跌",
            aigc_adapter=adapter,
            trading_style="波段",
            trigger_time="10:30",
            支撑位价格=12.30,
            破位后未回弹分钟数=5,
            成交额放大比例=25.0,
            板块名称="银行",
            板块涨跌幅=-1.5,
            大盘涨跌幅=-0.8
        )

        print(f"\n{result2}\n")

        print("\n" + "="*70)
        print("✅ 测试成功！智谱AI已正常工作")
        print("="*70)

        print("\n💡 下一步:")
        print("   1. 查看完整示例: python examples/zhipu_example.py")
        print("   2. 使用交互式启动: python quick_start.py")
        print("   3. 阅读文档: docs/ZHIPU_AI_GUIDE.md")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n已退出")
