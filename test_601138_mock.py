#!/usr/bin/env python3
"""
测试601138工业富联真实Mock数据
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("\n" + "="*70)
    print("601138 工业富联 - 使用真实Mock数据分析")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    from src.aigc.model_adapter import ZhipuAdapter
    from src.monitors.stock_monitor import quick_analysis

    api_key = os.getenv("ZHIPU_API_KEY")
    adapter = ZhipuAdapter(api_key=api_key)

    print("\n正在使用工业富联真实数据...")
    print("-"*70)

    # 使用真实的601138数据
    result = await quick_analysis(
        stock_code="601138",
        pattern_type="开盘跳水",
        aigc_adapter=adapter,
        trading_style="短线",

        # 工业富联真实数据
        开盘分钟数=10,
        跌幅=2.5,  # 增加以确保触发规则
        均线类型=5,
        均线价格=58.20,
        成交额放大比例=35.0,
        板块名称="电子",
        板块涨跌幅=-0.5,
        大盘涨跌幅=-0.3
    )

    if result:
        print("\n" + "="*70)
        print("分析结果:")
        print("="*70)
        print(result)
        print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
