"""
基础使用示例
演示如何使用股票AIGC监控系统
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.templates.prompt_templates import PromptTemplateManager, ChartType, TemplateType, generate_prompt
from src.aigc.model_adapter import MockAIGCAdapter, AIGCService
from src.monitors.data_collector import create_mock_monitoring_data
from src.monitors.stock_monitor import StockPatternMonitor, PatternType, TradingStyle, quick_analysis
from src.utils.config import Config


# ==================== 示例1：直接使用Prompt模板 ====================
def example_1_direct_template_usage():
    """示例1：直接使用Prompt模板生成功能"""
    print("\n" + "="*60)
    print("示例1：直接使用Prompt模板")
    print("="*60)

    # 准备股票数据
    stock_data = {
        "股票代码": "600000",
        "股票名称": "浦发银行",
        "触发时间": "09:35",
        "图形类型": "开盘跳水",
        "开盘价": 10.50,
        "实时价": 10.17,
        "最高价": 10.50,
        "涨停价": 11.55,
        "5日均线": 10.30,
        "20日均线": 10.15,
        "前期平台支撑位": 10.00,
        "触发成交额": 12500,
        "成交额放大比例": 35.5,
        "当日成交额放大比例": 20.3,
        "分钟成交额放大比例": 50.0,
        "板块名称": "银行",
        "板块涨跌幅": -1.2,
        "大盘名称": "上证指数",
        "大盘涨跌幅": -0.8,
        "最新消息": "无",
        "额外特征": "开盘5分钟跌超3%，跌破5日均线",
        "开盘分钟数": 5,
        "跌幅": 3.2,
        "均线类型": 5,
        "均线价格": 10.30
    }

    # 生成开盘跳水完整版Prompt
    prompt = PromptTemplateManager.get_opening_dive_template(
        stock_data=stock_data,
        trading_style="短线",
        template_type=TemplateType.FULL
    )

    print("\n生成的Prompt（完整版）:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)

    # 生成简化版Prompt
    simple_prompt = PromptTemplateManager.get_opening_dive_template(
        stock_data=stock_data,
        trading_style="短线",
        template_type=TemplateType.SIMPLIFIED
    )

    print("\n生成的Prompt（简化版）:")
    print("-" * 60)
    print(simple_prompt)
    print("-" * 60)


# ==================== 示例2：使用便捷函数生成Prompt ====================
def example_2_convenient_function():
    """示例2：使用便捷函数快速生成Prompt"""
    print("\n" + "="*60)
    print("示例2：使用便捷函数生成Prompt")
    print("="*60)

    # 使用便捷函数
    prompt = generate_prompt(
        chart_type="开盘跳水",
        stock_data={
            "股票代码": "600000",
            "股票名称": "浦发银行",
            "触发时间": "09:35",
            "开盘分钟数": 5,
            "跌幅": 3.2,
            "均线类型": 5,
            "均线价格": 10.30,
            "成交额放大比例": 35.5,
            "板块名称": "银行",
            "板块涨跌幅": -1.2,
            "大盘涨跌幅": -0.8,
            "最新消息": "无"
        },
        trading_style="短线",
        template_type=TemplateType.SIMPLIFIED
    )

    print("\n使用便捷函数生成的简化版Prompt:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)


# ==================== 示例3：结合AIGC进行分析 ====================
async def example_3_with_aigc():
    """示例3：结合Mock AIGC模型进行分析"""
    print("\n" + "="*60)
    print("示例3：结合AIGC模型进行分析")
    print("="*60)

    # 创建Mock AIGC适配器（实际使用时替换为真实适配器）
    aigc_adapter = MockAIGCAdapter()
    aigc_service = AIGCService(aigc_adapter)

    # 准备数据
    stock_data = {
        "股票代码": "600000",
        "股票名称": "浦发银行",
        "触发时间": "09:35",
        "图形类型": "开盘跳水",
        # ... 其他数据字段（参见示例1）
        "开盘价": 10.50,
        "实时价": 10.17,
        "最高价": 10.50,
        "5日均线": 10.30,
        "20日均线": 10.15,
        "前期平台支撑位": 10.00,
        "触发成交额": 12500,
        "成交额放大比例": 35.5,
        "当日成交额放大比例": 20.3,
        "分钟成交额放大比例": 50.0,
        "板块名称": "银行",
        "板块涨跌幅": -1.2,
        "大盘名称": "上证指数",
        "大盘涨跌幅": -0.8,
        "最新消息": "无",
        "额外特征": "开盘5分钟跌超3%",
        "开盘分钟数": 5,
        "跌幅": 3.2,
        "均线类型": 5,
        "均线价格": 10.30
    }

    # 生成Prompt
    prompt = PromptTemplateManager.get_opening_dive_template(
        stock_data=stock_data,
        trading_style="短线"
    )

    print("\n调用AIGC分析...")
    print("-" * 60)

    # 调用AIGC
    result = await aigc_service.async_analyze_stock_pattern(prompt)

    print("\nAIGC分析结果:")
    print("-" * 60)
    print(result)
    print("-" * 60)


# ==================== 示例4：使用完整监控流程 ====================
async def example_4_full_monitoring():
    """示例4：使用完整的监控流程"""
    print("\n" + "="*60)
    print("示例4：完整监控流程")
    print("="*60)

    # 创建监控器（使用真实数据）
    from src.monitors.tencent_collector import UnifiedRealDataCollector
    from src.monitors.data_collector import StockDataAggregator

    try:
        data_collector = UnifiedRealDataCollector()
        print("\n使用腾讯财经API获取真实数据")
    except Exception as e:
        print(f"\n⚠️  无法使用真实数据: {e}")
        from src.monitors.data_collector import MockDataCollector
        data_collector = MockDataCollector()
        print("   使用模拟数据")

    data_aggregator = StockDataAggregator(data_collector)

    aigc_adapter = MockAIGCAdapter()
    aigc_service = AIGCService(aigc_adapter)

    monitor = StockPatternMonitor(
        data_aggregator=data_aggregator,
        aigc_service=aigc_service,
        trading_style=TradingStyle.SHORT,
        template_type=TemplateType.FULL
    )

    # 模拟检测开盘跳水
    print("\n检测股票 600000 的开盘跳水图形...")
    print("-" * 60)

    trigger_event = await monitor.analyze_pattern(
        stock_code="600000",
        pattern_type=PatternType.OPENING_DIVE,
        position_status="已持仓",
        trigger_time="09:35",
        开盘分钟数=5,
        跌幅=3.2,
        均线类型=5,
        均线价格=10.30,
        成交额放大比例=35.5,
        当日成交额放大比例=20.3,
        分钟成交额放大比例=50.0
    )

    if trigger_event:
        print(f"\n✓ 监控触发事件ID: {trigger_event.事件ID}")
        print(f"✓ 股票: {trigger_event.股票代码} {trigger_event.股票名称}")
        print(f"✓ 图形类型: {trigger_event.图形类型}")
    else:
        print("\n✗ 未触发监控规则")


# ==================== 示例5：快速分析函数 ====================
async def example_5_quick_analysis():
    """示例5：使用快速分析函数"""
    print("\n" + "="*60)
    print("示例5：快速分析函数")
    print("="*60)

    # 使用快速分析函数
    result = await quick_analysis(
        stock_code="600000",
        pattern_type="破位下跌",
        aigc_adapter=MockAIGCAdapter(),
        trading_style="波段",
        trigger_time="10:30",
        支撑位价格=10.00,
        破位后未回弹分钟数=5,
        成交额放大比例=25.0,
        板块名称="银行",
        板块涨跌幅=-1.5,
        大盘涨跌幅=-0.8,
        最新消息="无"
    )

    if result:
        print("\n快速分析结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)


# ==================== 示例6：批量检测 ====================
def example_6_batch_detection():
    """示例6：批量检测多个股票"""
    print("\n" + "="*60)
    print("示例6：批量检测多个股票")
    print("="*60)

    from src.monitors.tencent_collector import UnifiedRealDataCollector
    from src.monitors.data_collector import StockDataAggregator
    from src.aigc.model_adapter import MockAIGCAdapter, AIGCService

    # 创建监控器（使用真实数据）
    try:
        data_collector = UnifiedRealDataCollector()
        print("\n使用腾讯财经API获取真实数据")
    except Exception as e:
        print(f"\n⚠️  无法使用真实数据: {e}")
        from src.monitors.data_collector import MockDataCollector
        data_collector = MockDataCollector()

    data_aggregator = StockDataAggregator(data_collector)
    aigc_service = AIGCService(MockAIGCAdapter())
    monitor = StockPatternMonitor(data_aggregator, aigc_service)

    # 批量检测
    stock_codes = ["600000", "000001"]
    pattern_types = [PatternType.OPENING_DIVE, PatternType.BREAKDOWN_FALL]

    print(f"\n批量检测 {len(stock_codes)} 只股票的 {len(pattern_types)} 种图形...")
    print("-" * 60)

    detected = monitor.batch_detect(stock_codes, pattern_types)

    print(f"\n检测结果: 发现 {len(detected)} 个触发事件")
    for event in detected:
        print(f"  - {event['股票代码']}: {event['图形类型']}")


# ==================== 主函数 ====================
async def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print(" " * 15 + "股票AIGC监控系统 - 使用示例")
    print("="*70)

    # 示例1：直接使用Prompt模板
    example_1_direct_template_usage()

    # 示例2：使用便捷函数
    example_2_convenient_function()

    # 示例3：结合AIGC
    await example_3_with_aigc()

    # 示例4：完整监控流程
    await example_4_full_monitoring()

    # 示例5：快速分析
    await example_5_quick_analysis()

    # 示例6：批量检测
    example_6_batch_detection()

    print("\n" + "="*70)
    print("所有示例运行完成！")
    print("="*70)


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
