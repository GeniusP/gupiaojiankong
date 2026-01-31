#!/usr/bin/env python3
"""
快速演示：使用真实数据和AI分析
自动运行，无需交互
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def demo():
    """演示真实数据+AI分析"""
    print("\n" + "="*80)
    print(" " * 20 + "🚀 智谱AI股票分析演示")
    print("="*80)
    print("\n✓ 使用腾讯财经API获取实时数据")
    print("✓ 使用智谱GLM-4-Plus模型分析")
    print("✓ 自动检测图形类型")
    print("="*80)

    from dotenv import load_dotenv
    load_dotenv()

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n❌ 未配置智谱AI API密钥")
        print("请在.env文件中设置: ZHIPU_API_KEY=your_api_key")
        return

    print("\n✅ 智谱AI API密钥已配置")

    # 测试股票列表
    test_stocks = ["601138", "600519", "002594"]

    try:
        import analyze
        from src.monitors.tencent_collector import TencentFinanceCollector

        # 首先显示所有股票的实时数据
        print("\n" + "="*80)
        print("📊 获取实时行情数据")
        print("="*80)

        collector = TencentFinanceCollector()

        for code in test_stocks:
            data = collector.get_stock_realtime_data(code)
            if data and data.get("股票名称"):
                # 使用昨收价计算涨跌幅
                prev_close = data.get('昨收', data.get('开盘价', 0))
                change = ((data['实时价'] - prev_close) / prev_close * 100) if prev_close > 0 else 0
                print(f"{data['股票名称']}({code}): {data['实时价']}元 ({change:+.2f}%)")

        # 分析每只股票
        print("\n" + "="*80)
        print("🤖 AI智能分析")
        print("="*80)

        for i, stock_code in enumerate(test_stocks, 1):
            print(f"\n[{i}/{len(test_stocks)}] 分析 {stock_code}")
            print("-"*80)

            result = await analyze.quick_analyze(stock_code, None, auto_detect=True)

            if result:
                print("✅ 分析完成")
            else:
                print("⚠️  市场状态不适合图形分析")

            # 延迟
            if i < len(test_stocks):
                print("\n⏳ 等待3秒...")
                await asyncio.sleep(3)

        print("\n" + "="*80)
        print("✅ 演示完成！")
        print("="*80)

        print("\n💡 使用提示:")
        print("   1. 运行 'python3 analyze.py <股票代码>' 分析单只股票")
        print("   2. 运行 'python3 real_time_analysis.py' 启动交互式分析")
        print("   3. 运行 'python3 start.py' 启动主菜单")
        print("   4. 查看 '使用说明.md' 了解详细用法")

    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
