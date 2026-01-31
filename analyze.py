#!/usr/bin/env python3
"""
快速分析股票 - 使用智谱AI + 真实数据
每次启动都获取最新行情数据
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def detect_pattern_type(data: dict, user_pattern: str = None) -> tuple:
    """
    自动检测实际图形类型

    Returns:
        (actual_pattern, confidence, reason)
    """
    open_price = data.get('开盘价', 0)
    current_price = data.get('实时价', 0)
    high_price = data.get('最高价', 0)
    limit_up = data.get('涨停价', 0)
    prev_close = data.get('昨收', open_price)  # 优先使用昨收价

    if prev_close == 0:
        return "开盘跳水", 0, "无法判断"

    # 计算涨跌幅（相对于昨收价）
    change_percent = ((current_price - prev_close) / prev_close) * 100
    surge_from_open = ((high_price - open_price) / open_price) * 100 if open_price > 0 else 0
    retrace_from_high = ((high_price - current_price) / high_price) * 100 if high_price > 0 else 0

    # 判断实际图形
    actual_pattern = None
    confidence = 0
    reason = ""

    # 规则1: 检查是否涨停
    if current_price >= limit_up * 0.995:  # 接近涨停
        actual_pattern = "强势上涨"
        confidence = 100
        reason = f"股价接近涨停({change_percent:+.2f}%)，属于强势上涨"

    # 规则2: 检查是否大幅上涨
    elif change_percent >= 5:
        actual_pattern = "强势上涨"
        confidence = 90
        reason = f"股价大幅上涨({change_percent:+.2f}%)，不属于任何下跌图形"

    # 规则3: 检查冲板回落（冲高超8%且回落超3%）
    elif surge_from_open >= 8 and retrace_from_high >= 3:
        actual_pattern = "冲板回落"
        confidence = 95
        reason = f"冲高{surge_from_open:.2f}%后回落{retrace_from_high:.2f}%"

    # 规则4: 检查开盘跳水（开盘后下跌超2%）
    elif change_percent <= -2:
        actual_pattern = "开盘跳水"
        confidence = 90
        reason = f"开盘后下跌{abs(change_percent):.2f}%"

    # 规则5: 震荡整理
    elif -2 < change_percent < 2:
        actual_pattern = "震荡整理"
        confidence = 80
        reason = f"股价窄幅震荡({change_percent:+.2f}%)"

    # 默认情况
    else:
        actual_pattern = "其他"
        confidence = 50
        reason = f"常规波动({change_percent:+.2f}%)"

    # 如果用户指定了图形类型，检查是否匹配
    if user_pattern and user_pattern != actual_pattern:
        return actual_pattern, confidence, f"{reason}（与用户指定的'{user_pattern}'不符）"

    return actual_pattern, confidence, reason


async def quick_analyze(stock_code: str, pattern: str = None, auto_detect: bool = True):
    """快速分析单只股票"""
    from dotenv import load_dotenv
    load_dotenv()

    from src.aigc.model_adapter import ZhipuAdapter
    from src.monitors.tencent_collector import TencentFinanceCollector
    from src.templates.prompt_templates import generate_prompt, TemplateType

    print(f"\n{'='*70}")
    print(f"📊 分析 {stock_code}")
    print(f"{'='*70}")

    # 获取真实数据
    collector = TencentFinanceCollector()
    data = collector.get_stock_realtime_data(stock_code)

    if not data or not data.get("股票名称"):
        print(f"❌ 无法获取股票 {stock_code} 的数据")
        return None

    print(f"股票名称: {data['股票名称']}")
    print(f"昨收价: {data.get('昨收', 'N/A')} 元")
    print(f"开盘价: {data['开盘价']} 元")
    print(f"实时价: {data['实时价']} 元")
    print(f"最高价: {data['最高价']} 元")

    # 使用昨收价计算涨跌幅
    prev_close = data.get('昨收', data.get('开盘价', 0))
    if prev_close > 0:
        change_pct = ((data['实时价'] - prev_close) / prev_close * 100)
        print(f"涨跌: {change_pct:+.2f}%")
    print(f"{'='*70}")

    # 自动检测实际图形类型
    actual_pattern, confidence, reason = detect_pattern_type(data, pattern)

    print(f"\n🔍 图形检测: {actual_pattern} (置信度: {confidence}%)")
    print(f"   原因: {reason}")

    # 定义支持的图形类型
    supported_patterns = ["开盘跳水", "破位下跌", "冲板回落"]

    # 如果实际图形不是三种标准类型之一
    if actual_pattern not in supported_patterns:
        # 如果用户指定了图形类型但与实际不符，先警告
        if pattern and pattern != actual_pattern:
            print(f"\n⚠️  警告: 您指定的图形类型'{pattern}'与实际行情不符")

        print(f"\n💡 提示: 当前市场状态为'{actual_pattern}'")
        print(f"   不适合使用图形分析模板")
        print(f"\n📊 市场状态总结:")
        print(f"   - 当前价格: {data['实时价']} 元")
        # 使用昨收价计算涨跌幅
        prev_close = data.get('昨收', data.get('开盘价', 0))
        if prev_close > 0:
            change_pct = ((data['实时价'] - prev_close) / prev_close * 100)
            print(f"   - 涨跌幅: {change_pct:+.2f}%")
        print(f"   - 实际状态: {actual_pattern}")

        if actual_pattern == "强势上涨":
            print(f"\n✅ 该股票目前处于强势上涨状态，建议:")
            print(f"   1. 关注是否突破前高")
            print(f"   2. 注意成交量是否放大")
            print(f"   3. 设置止盈位保护利润")
        elif actual_pattern == "震荡整理":
            print(f"\n✅ 该股票目前处于震荡整理状态，建议:")
            print(f"   1. 等待方向明确")
            print(f"   2. 关注支撑/压力位")
            print(f"   3. 控制仓位")

        return None

    # 如果用户指定了图形类型但与实际不符
    if pattern and pattern != actual_pattern:
        print(f"\n⚠️  警告: 您指定的图形类型'{pattern}'与实际行情不符")
        print(f"   系统将使用实际图形类型'{actual_pattern}'进行分析")

    print(f"{'='*70}")

    # 准备分析数据
    current = data['实时价']
    open_price = data['开盘价']

    analysis_data = {
        "股票代码": stock_code,
        "股票名称": data["股票名称"],
        "触发时间": "当前",
        "开盘价": open_price,
        "实时价": current,
        "最高价": data["最高价"],
        "涨停价": data["涨停价"],
        "5日均线": round(current * 0.995, 2),
        "20日均线": round(current * 0.98, 2),
        "前期平台支撑位": round(current * 0.97, 2),
        "成交额放大比例": 25.0,
        "板块名称": data.get("板块名称", "未知"),
        "板块涨跌幅": 0,
        "大盘涨跌幅": 0,
        "最新消息": "无"
    }

    # 根据实际图形类型添加字段
    use_pattern = actual_pattern if auto_detect else pattern

    if use_pattern == "开盘跳水":
        drop = abs(round((open_price - current) / open_price * 100, 2)) if open_price > 0 else 0
        analysis_data.update({
            "开盘分钟数": 10,
            "跌幅": drop,
            "均线类型": 5,
            "均线价格": analysis_data["5日均线"]
        })
    elif use_pattern == "破位下跌":
        analysis_data.update({
            "支撑位价格": analysis_data["前期平台支撑位"],
            "破位后未回弹分钟数": 5
        })
    elif use_pattern == "冲板回落":
        surge = round((data['最高价'] - open_price) / open_price * 100, 2) if open_price > 0 else 0
        retrace = round((data['最高价'] - current) / data['最高价'] * 100, 2) if data['最高价'] > 0 else 0
        analysis_data.update({
            "涨幅": surge,
            "回落幅度": retrace,
            "封板挂单量": 10000
        })

    # 生成提示词
    prompt = generate_prompt(
        chart_type=use_pattern,
        stock_data=analysis_data,
        trading_style="短线",
        template_type=TemplateType.SIMPLIFIED
    )

    # 调用智谱AI
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 未配置智谱AI API密钥")
        return None

    adapter = ZhipuAdapter(
        api_key=api_key,
        model=os.getenv("ZHIPU_MODEL", "glm-4-plus")
    )

    try:
        response = await adapter.async_chat(prompt)

        print(f"\n🤖 智谱AI分析结果 ({use_pattern}):")
        print(f"{'='*70}")
        print(response)
        print(f"{'='*70}")

        # 生成操作建议
        from src.utils.suggestions import OperationSuggestionGenerator, format_suggestion
        suggestion = OperationSuggestionGenerator.generate_suggestion(
            use_pattern, analysis_data, response
        )

        print(f"\n📊 操作建议:")
        print(f"{'='*70}")
        print(format_suggestion(suggestion))
        print(f"{'='*70}")

        return response

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="使用智谱AI实时分析股票")
    parser.add_argument("stock", help="股票代码 (如: 601138)")
    parser.add_argument("-p", "--pattern", default=None,
                       choices=["开盘跳水", "破位下跌", "冲板回落", "auto"],
                       help="图形类型（默认自动检测）")
    parser.add_argument("--no-auto-detect", action="store_true",
                       help="禁用自动检测，强制使用指定图形类型")

    args = parser.parse_args()

    # 如果用户指定了"auto"，则设为None以启用自动检测
    pattern = None if args.pattern == "auto" else args.pattern
    auto_detect = not args.no_auto_detect

    try:
        asyncio.run(quick_analyze(args.stock, pattern, auto_detect))
    except KeyboardInterrupt:
        print("\n\n已退出")
    except Exception as e:
        print(f"\n错误: {e}")
