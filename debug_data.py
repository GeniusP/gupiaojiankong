#!/usr/bin/env python3
"""
调试数据传递
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    from src.monitors.data_collector import MockDataCollector, StockDataAggregator

    collector = MockDataCollector()
    aggregator = StockDataAggregator(collector)

    # 测试采集601138的数据
    data = aggregator.collect_monitoring_data(
        stock_code="601138",
        chart_type="开盘跳水",
        trigger_time="09:35",
        开盘分钟数=10,
        跌幅=2.5,
        均线类型=5,
        均线价格=10.10,
        成交额放大比例=30.0
    )

    print("\n采集到的数据:")
    print(f"开盘价: {data['开盘价']}")
    print(f"实时价: {data['实时价']}")
    print(f"开盘分钟数: {data['开盘分钟数']}")
    print(f"跌幅: {data['跌幅']}")
    print(f"5日均线: {data['5日均线']}")

    # 计算实际跌幅
    if data['开盘价'] and data['实时价']:
        actual_drop = (data['开盘价'] - data['实时价']) / data['开盘价'] * 100
        print(f"\n实际跌幅: {actual_drop}%")

    # 测试规则
    from src.monitors.stock_monitor import StockPatternMonitor, PatternType
    from src.aigc.model_adapter import MockAIGCAdapter, AIGCService

    monitor = StockPatternMonitor(
        aggregator,
        AIGCService(MockAIGCAdapter())
    )

    print("\n测试规则检查...")
    result = monitor._check_opening_dive(data, minutes=10, drop_percent=2)
    print(f"规则检查结果: {result}")


if __name__ == "__main__":
    asyncio.run(main())
