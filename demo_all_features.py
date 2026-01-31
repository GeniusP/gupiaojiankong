#!/usr/bin/env python3
"""
自动演示所有功能
无需交互，自动展示系统所有功能
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def demo_prompt_template():
    """演示Prompt模板生成"""
    print("\n" + "="*70)
    print("【功能1】Prompt模板生成")
    print("="*70)

    from src.templates.prompt_templates import generate_prompt, TemplateType

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
            "大盘涨跌幅": -0.8
        },
        trading_style="短线",
        template_type=TemplateType.SIMPLIFIED
    )

    print("\n生成的简化版Prompt:")
    print("-"*70)
    print(prompt)
    print("-"*70)


async def demo_mock_analysis():
    """演示Mock AIGC分析"""
    print("\n" + "="*70)
    print("【功能2】Mock AIGC分析（无需API）")
    print("="*70)

    from src.aigc.model_adapter import MockAIGCAdapter, AIGCService
    from src.templates.prompt_templates import generate_prompt

    adapter = MockAIGCAdapter()
    service = AIGCService(adapter)

    prompt = "股票600000开盘5分钟跌3.2%，板块跌1.2%，大盘跌0.8%。判断是真/假跳水？风险高/中/低？短线该规避/持有/止损？给出关键价位，50字内。"

    print("\n发送到Mock AIGC的Prompt:")
    print("-"*70)
    print(prompt)
    print("-"*70)

    result = await service.async_analyze_stock_pattern(prompt)

    print("\nMock AIGC分析结果:")
    print("-"*70)
    print(result)
    print("-"*70)


async def demo_config_check():
    """演示配置检查"""
    print("\n" + "="*70)
    print("【功能3】配置检查")
    print("="*70)

    from src.utils.config import Config, print_config_summary

    print_config_summary()

    print("\n各模型配置状态:")
    print("-"*70)

    # 检查GPT
    if Config.OPENAI_API_KEY:
        print("✓ GPT配置: 已配置")
    else:
        print("✗ GPT配置: 未配置")

    # 检查讯飞星火
    if Config.SPARK_APP_ID:
        print("✓ 讯飞星火配置: 已配置")
    else:
        print("✗ 讯飞星火配置: 未配置")

    # 检查千帆
    if Config.QIANFAN_ACCESS_KEY:
        print("✓ 千帆配置: 已配置")
    else:
        print("✗ 千帆配置: 未配置")

    # 检查智谱AI
    if Config.ZHIPU_API_KEY:
        print(f"✓ 智谱AI配置: 已配置 ({Config.ZHIPU_MODEL})")
    else:
        print("✗ 智谱AI配置: 未配置")

    print("-"*70)

    # 验证默认模型
    print(f"\n默认模型: {Config.DEFAULT_AIGC_MODEL}")
    print(f"配置验证: {'✓ 通过' if Config.validate() else '✗ 失败（部分模型未配置）'}")


async def demo_real_analysis():
    """演示真实AIGC分析（如果配置了智谱AI）"""
    print("\n" + "="*70)
    print("【功能4】真实AIGC分析（智谱AI）")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")

    if not api_key:
        print("\n未配置智谱AI API密钥")
        print("如需使用真实AIGC，请在.env文件中配置:")
        print("  ZHIPU_API_KEY=your_api_key_here")
        return

    try:
        from src.aigc.model_adapter import ZhipuAdapter, AIGCService
        from src.monitors.stock_monitor import quick_analysis

        adapter = ZhipuAdapter(api_key=api_key, model=os.getenv("ZHIPU_MODEL", "glm-4-plus"))

        print("\n正在分析股票...")
        print("-"*70)

        # 分析案例1
        result = await quick_analysis(
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

        if result:
            print(result)

        print("-"*70)
        print("\n✓ 真实AIGC分析成功！")

    except Exception as e:
        print(f"\n✗ 分析失败: {e}")


async def demo_help():
    """演示帮助信息"""
    print("\n" + "="*70)
    print("【功能5】使用帮助")
    print("="*70)

    help_text = """
【系统功能】

1. Prompt模板生成
   - 支持开盘跳水、破位下跌、冲板回落三种图形
   - 完整版（150字）和简化版（50字）两种模板
   - 自动生成结构化Prompt

2. AIGC分析
   - 支持多种模型：智谱AI、GPT、讯飞星火、文心一言
   - 自动识别图形并触发分析
   - 输出判断、风险、操作建议

3. 配置管理
   - 支持.env文件配置
   - 多模型API密钥管理
   - 自动配置验证

【使用方式】

方式1：仅使用Prompt模板
  from src.templates.prompt_templates import generate_prompt

  prompt = generate_prompt(
      chart_type="开盘跳水",
      stock_data={...},
      trading_style="短线"
  )

方式2：快速分析函数
  from src.monitors.stock_monitor import quick_analysis
  from src.aigc.model_adapter import ZhipuAdapter

  result = await quick_analysis(
      stock_code="600000",
      pattern_type="开盘跳水",
      aigc_adapter=ZhipuAdapter(),
      trading_style="短线"
  )

方式3：完整监控流程
  from src.monitors.stock_monitor import StockPatternMonitor

  monitor = StockPatternMonitor(data_aggregator, aigc_service)
  result = await monitor.analyze_pattern(
      stock_code="600000",
      pattern_type=PatternType.OPENING_DIVE
  )

【支持的图形类型】

- 开盘跳水：开盘后快速下跌分析
- 破位下跌：跌破关键支撑位分析
- 冲板回落：冲高后回落分析

【支持的AIGC模型】

- 智谱AI（推荐）：glm-4-plus, glm-4-air, glm-4-flash
- GPT：gpt-4-turbo-preview, gpt-4
- 讯飞星火：generalv3
- 文心一言：ERNIE-Bot-4

【文档】

- README.md - 完整使用文档
- QUICKSTART_ZHIPU.md - 智谱AI快速开始
- docs/ZHIPU_AI_GUIDE.md - 智谱AI详细指南
- examples/ - 代码示例

【免责声明】
本系统仅提供技术分析辅助，不构成任何投资建议。
股市有风险，投资需谨慎。
"""

    print(help_text)
    print("="*70)


async def main():
    """主函数"""
    print("\n" + "="*70)
    print(" " * 20 + "股票AIGC监控系统 - 功能演示")
    print("="*70)

    print("\n将自动演示所有功能...")

    # 演示所有功能
    await demo_prompt_template()
    await asyncio.sleep(1)

    await demo_mock_analysis()
    await asyncio.sleep(1)

    await demo_config_check()
    await asyncio.sleep(1)

    await demo_real_analysis()
    await asyncio.sleep(1)

    await demo_help()

    print("\n" + "="*70)
    print("✅ 所有功能演示完成！")
    print("="*70)

    print("\n💡 快速开始:")
    print("   1. 使用真实AIGC: python quick_start_zhipu.py")
    print("   2. 查看更多示例: python examples/zhipu_example.py")
    print("   3. 阅读文档: docs/ZHIPU_AI_GUIDE.md")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n演示已中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
