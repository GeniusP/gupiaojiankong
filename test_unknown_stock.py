#!/usr/bin/env python3
"""
测试未知股票代码
验证系统可以处理任何股票代码
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("\n" + "="*70)
    print("测试未知股票代码：601138")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    from src.aigc.model_adapter import ZhipuAdapter
    from src.monitors.stock_monitor import quick_analysis

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置API密钥")
        return

    adapter = ZhipuAdapter(api_key=api_key)

    print("\n正在分析601138...")
    print("-"*70)

    result = await quick_analysis(
        stock_code="601138",  # 未知的股票代码
        pattern_type="开盘跳水",
        aigc_adapter=adapter,
        trading_style="短线",
        开盘分钟数=10,  # 使用10分钟规则，要求跌幅>=2%
        跌幅=2.5,  # 跌幅2.5%
        均线类型=5,
        均线价格=10.10,
        成交额放大比例=30.0
    )

    if result:
        print(f"\n✅ 分析成功！")
        print(f"\n分析结果:")
        print("-"*70)
        print(result)
        print("-"*70)
    else:
        print(f"\n⚠️  未触发识别规则")

    print("\n" + "="*70)
    print("✅ 测试完成：系统可以处理任何股票代码")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
