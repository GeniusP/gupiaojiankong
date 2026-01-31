#!/usr/bin/env python3
"""
股票AIGC监控系统 - 快速启动脚本
无需编码，直接运行即可体验系统功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """打印横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        股票AIGC监控系统 v1.0                              ║
║                                                           ║
║        支持图形: 开盘跳水 | 破位下跌 | 冲板回落            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_menu():
    """打印菜单"""
    menu = """
请选择功能:

1. 查看Prompt模板（输入股票数据生成Prompt）
2. 运行示例分析（使用Mock数据演示）
3. 配置检查
4. 查看帮助
0. 退出
"""
    print(menu)


def option_1_generate_prompt():
    """选项1：生成Prompt模板"""
    print("\n" + "="*60)
    print("功能1: 生成Prompt模板")
    print("="*60)

    from src.templates.prompt_templates import generate_prompt, TemplateType

    # 获取用户输入
    print("\n请输入股票信息（直接回车使用默认值）:")
    stock_code = input("股票代码 [600000]: ").strip() or "600000"
    stock_name = input("股票名称 [浦发银行]: ").strip() or "浦发银行"
    trigger_time = input("触发时间 [09:35]: ").strip() or "09:35"

    print("\n选择图形类型:")
    print("1. 开盘跳水")
    print("2. 破位下跌")
    print("3. 冲板回落")
    chart_choice = input("请选择 [1-3]: ").strip() or "1"

    chart_types = {"1": "开盘跳水", "2": "破位下跌", "3": "冲板回落"}
    chart_type = chart_types.get(chart_choice, "开盘跳水")

    print("\n选择模板类型:")
    print("1. 完整版（150字，深度分析）")
    print("2. 简化版（50字，快速响应）")
    template_choice = input("请选择 [1-2]: ").strip() or "2"

    template_type = TemplateType.FULL if template_choice == "1" else TemplateType.SIMPLIFIED

    trading_style = input("交易风格 [短线]: ").strip() or "短线"

    # 构建数据
    stock_data = {
        "股票代码": stock_code,
        "股票名称": stock_name,
        "触发时间": trigger_time,
        "开盘价": 10.50,
        "实时价": 10.17,
        "最高价": 10.50,
        "成交额放大比例": 35.5,
        "板块名称": "银行",
        "板块涨跌幅": -1.2,
        "大盘涨跌幅": -0.8,
        "最新消息": "无"
    }

    # 添加图形特定字段
    if chart_type == "开盘跳水":
        stock_data.update({
            "开盘分钟数": 5,
            "跌幅": 3.2,
            "均线类型": 5,
            "均线价格": 10.30
        })
    elif chart_type == "破位下跌":
        stock_data.update({
            "支撑位价格": 10.00,
            "破位后未回弹分钟数": 5
        })
    elif chart_type == "冲板回落":
        stock_data.update({
            "涨幅": 9.8,
            "回落幅度": 5.2,
            "封板挂单量": 15000
        })

    # 生成Prompt
    prompt = generate_prompt(
        chart_type=chart_type,
        stock_data=stock_data,
        trading_style=trading_style,
        template_type=template_type
    )

    print("\n" + "="*60)
    print("生成的Prompt:")
    print("="*60)
    print(prompt)
    print("="*60)

    input("\n按回车键继续...")


async def option_2_run_example():
    """选项2：运行示例分析"""
    print("\n" + "="*60)
    print("功能2: 运行示例分析（使用Mock AIGC）")
    print("="*60)

    from src.aigc.model_adapter import MockAIGCAdapter, AIGCService
    from src.monitors.stock_monitor import quick_analysis

    print("\n正在运行示例分析...")
    print("-" * 60)

    # 示例1：开盘跳水
    print("\n[示例1] 开盘跳水分析:")
    result1 = await quick_analysis(
        stock_code="600000",
        pattern_type="开盘跳水",
        aigc_adapter=MockAIGCAdapter(),
        trading_style="短线",
        trigger_time="09:35",
        开盘分钟数=5,
        跌幅=3.2
    )
    print(result1)

    print("\n" + "-" * 60)

    # 示例2：破位下跌
    print("\n[示例2] 破位下跌分析:")
    result2 = await quick_analysis(
        stock_code="000001",
        pattern_type="破位下跌",
        aigc_adapter=MockAIGCAdapter(),
        trading_style="波段",
        trigger_time="10:30",
        支撑位价格=12.30,
        破位后未回弹分钟数=5
    )
    print(result2)

    print("\n" + "-" * 60)

    # 示例3：冲板回落
    print("\n[示例3] 冲板回落分析:")
    result3 = await quick_analysis(
        stock_code="600036",
        pattern_type="冲板回落",
        aigc_adapter=MockAIGCAdapter(),
        trading_style="短线",
        trigger_time="10:15",
        涨幅=9.8,
        回落幅度=5.2
    )
    print(result3)

    print("\n" + "="*60)
    input("\n按回车键继续...")


def option_3_check_config():
    """选项3：检查配置"""
    print("\n" + "="*60)
    print("功能3: 配置检查")
    print("="*60)

    from src.utils.config import Config, print_config_summary

    print_config_summary()

    print("\n检查各模型配置:")
    print("-" * 60)

    # 检查GPT
    if Config.OPENAI_API_KEY:
        print("✓ GPT配置: 已配置")
        print(f"  API Key: {Config.OPENAI_API_KEY[:10]}...")
        print(f"  Model: {Config.OPENAI_MODEL}")
    else:
        print("✗ GPT配置: 未配置（OPENAI_API_KEY为空）")

    print()

    # 检查讯飞星火
    if Config.SPARK_APP_ID and Config.SPARK_API_KEY:
        print("✓ 讯飞星火配置: 已配置")
        print(f"  App ID: {Config.SPARK_APP_ID}")
        print(f"  Domain: {Config.SPARK_DOMAIN}")
    else:
        print("✗ 讯飞星火配置: 未完整配置")

    print()

    # 检查千帆
    if Config.QIANFAN_ACCESS_KEY:
        print("✓ 千帆配置: 已配置")
        print(f"  Model: {Config.QIANFAN_MODEL}")
    else:
        print("✗ 千帆配置: 未配置（QIANFAN_ACCESS_KEY为空）")

    print("\n" + "="*60)
    print("\n提示: 使用Mock AIGC可以无需配置即可测试系统功能")
    print("实际使用时请在.env文件中配置对应的API密钥")

    input("\n按回车键继续...")


def option_4_help():
    """选项4：帮助"""
    print("\n" + "="*60)
    print("功能4: 帮助文档")
    print("="*60)

    help_text = """
【系统介绍】
本系统是基于大语言模型的股票图形监控和分析工具，支持：

1. 开盘跳水 - 开盘后快速下跌的图形识别与分析
2. 破位下跌 - 跌破关键支撑位的图形识别与分析
3. 冲板回落 - 冲高后回落的图形识别与分析

【使用流程】
1. 配置AIGC模型（讯飞星火/GPT/文心一言）
2. 采集股票实时数据（行情、成交量、市场环境）
3. 系统自动识别图形并生成结构化Prompt
4. 调用AIGC模型进行分析
5. 输出判断结果、风险等级、操作建议

【快速开始】
1. 复制.env.example为.env
2. 填入API密钥
3. 运行: python quick_start.py
4. 或查看示例: python examples/basic_usage.py

【代码示例】
# 方式1: 仅使用Prompt模板
from src.templates.prompt_templates import generate_prompt

prompt = generate_prompt(
    chart_type="开盘跳水",
    stock_data={...},
    trading_style="短线"
)

# 方式2: 完整监控流程
from src.monitors.stock_monitor import quick_analysis

result = await quick_analysis(
    stock_code="600000",
    pattern_type="开盘跳水",
    aigc_adapter=your_adapter,
    trading_style="短线"
)

【获取帮助】
- 查看README.md了解更多
- 运行examples/basic_usage.py查看完整示例
- 访问项目仓库提交Issue

【免责声明】
本系统仅提供技术分析辅助，不构成任何投资建议。
股市有风险，投资需谨慎。
"""

    print(help_text)
    print("="*60)

    input("\n按回车键继续...")


async def main():
    """主函数"""
    print_banner()

    while True:
        print_menu()
        choice = input("请选择 [0-4]: ").strip()

        if choice == "0":
            print("\n感谢使用！再见！")
            break
        elif choice == "1":
            option_1_generate_prompt()
        elif choice == "2":
            await option_2_run_example()
        elif choice == "3":
            option_3_check_config()
        elif choice == "4":
            option_4_help()
        else:
            print("\n无效选择，请重新输入！")
            input("按回车键继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
