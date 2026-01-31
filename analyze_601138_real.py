#!/usr/bin/env python3
"""
使用真实数据分析601138工业富联
展示如何手动传入真实股票数据
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def analyze_with_real_data():
    """
    使用真实数据分析601138
    """
    print("\n" + "="*70)
    print("601138 工业富联 - 真实数据分析")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    from src.aigc.model_adapter import ZhipuAdapter
    from src.monitors.stock_monitor import StockPatternMonitor, PatternType
    from src.monitors.data_collector import StockDataAggregator, MockDataCollector

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置智谱AI API密钥")
        return

    # 创建适配器
    adapter = ZhipuAdapter(api_key=api_key, model=os.getenv("ZHIPU_MODEL", "glm-4-plus"))

    # 创建监控器（使用Mock数据采集器，但手动传入真实数据）
    aggregator = StockDataAggregator(MockDataCollector())

    # 手动传入真实数据（2025-01-27 工业富联数据）
    # 您可以从交易软件或财经网站获取实时数据
    real_data = aggregator.collect_monitoring_data(
        stock_code="601138",
        chart_type="开盘跳水",
        trigger_time="09:35",
        开盘价=58.50,
        实时价=57.70,
        最高价=59.20,
        涨停价=64.35,
        ma5=58.20,
        ma20=57.50,
        前期平台支撑位=57.00,
        触发成交额=850000,
        成交额放大比例=35.0,
        板块名称="电子",
        板块涨跌幅=-0.5,
        大盘涨跌幅=-0.3,
        最新消息="无",
        额外特征="",
        开盘分钟数=10,
        跌幅=1.4,
        均线类型=5,
        均线价格=58.20
    )

    print("\n真实数据:")
    print("-"*70)
    print(f"股票: 601138 工业富联")
    print(f"开盘价: {real_data['开盘价']} 元")
    print(f"实时价: {real_data['实时价']} 元")
    print(f"最高价: {real_data['最高价']} 元")
    print(f"跌幅: {real_data['跌幅']}%")
    print(f"成交量: {real_data['触发成交额']} 万元")
    print(f"板块: {real_data['板块名称']} ({real_data['板块涨跌幅']}%)")
    print("-"*70)

    # 创建监控器并分析
    from src.aigc.model_adapter import AIGCService
    aigc_service = AIGCService(adapter)
    monitor = StockPatternMonitor(aggregator, aigc_service)

    print("\n正在分析...")
    print("-"*70)

    try:
        result = await monitor.analyze_pattern(
            stock_code="601138",
            pattern_type=PatternType.OPENING_DIVE,
            position_status="已持仓",
            **real_data
        )

        if result:
            print("\n✅ 分析完成！")
            print(f"\n{result.AIGC分析结果.原始回复}")
        else:
            print("\n⚠️  未触发识别规则")

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")


async def analyze_with_user_input():
    """
    让用户输入真实数据
    """
    print("\n" + "="*70)
    print("手动输入真实数据分析")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置智谱AI API密钥")
        return

    print("\n请输入股票数据（按回车使用默认值）：")
    print("-"*70)

    stock_code = input("股票代码 [601138]: ").strip() or "601138"
    stock_name = input("股票名称 [工业富联]: ").strip() or "工业富联"
    open_price = float(input("开盘价 [58.50]: ").strip() or "58.50")
    current_price = float(input("实时价 [57.70]: ").strip() or "57.70")
    high_price = float(input("最高价 [59.20]: ").strip() or "59.20")

    # 计算其他数据
    change_percent = ((open_price - current_price) / open_price) * 100
    limit_up = round(open_price * 1.1, 2)  # 简单计算涨停价

    print(f"\n自动计算:")
    print(f"  跌幅: {change_percent:.2f}%")
    print(f"  涨停价: {limit_up}")

    # 分析
    from src.aigc.model_adapter import ZhipuAdapter, AIGCService
    from src.monitors.stock_monitor import quick_analysis

    adapter = ZhipuAdapter(api_key=api_key)

    result = await quick_analysis(
        stock_code=stock_code,
        pattern_type="开盘跳水",
        aigc_adapter=adapter,
        trading_style="短线",
        trigger_time="09:35",
        开盘分钟数=10,
        跌幅=round(change_percent, 2),
        均线类型=5,
        均线_price=round(open_price * 0.995, 2),  # 简单估算5日均线
        成交额放大比例=30.0,
        板块名称="电子",
        板块涨跌幅=-0.5,
        大盘涨跌幅=-0.3
    )

    if result:
        print(f"\n分析结果:\n{result}")


async def main():
    """主函数"""
    print("\n请选择模式:")
    print("1. 使用预设的真实数据分析601138")
    print("2. 手动输入真实数据")

    choice = input("\n请选择 [1-2]: ").strip()

    if choice == "1":
        await analyze_with_real_data()
    elif choice == "2":
        await analyze_with_user_input()
    else:
        print("\n无效选择")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n已退出")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
