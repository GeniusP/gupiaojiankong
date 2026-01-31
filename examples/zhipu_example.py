"""
智谱AI（ChatGLM）使用示例
演示如何使用智谱AI进行股票图形分析
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aigc.model_adapter import ZhipuAdapter, AIGCService
from src.templates.prompt_templates import generate_prompt, TemplateType
from src.monitors.stock_monitor import quick_analysis


# ==================== 示例1：基础使用 ====================
async def example_1_basic_usage():
    """示例1：智谱AI基础使用"""
    print("\n" + "="*60)
    print("示例1：智谱AI基础使用")
    print("="*60)

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n⚠️  未配置ZHIPU_API_KEY环境变量")
        print("请在.env文件中设置：ZHIPU_API_KEY=your_api_key_here")
        print("获取API密钥：https://open.bigmodel.cn/usercenter/apikeys")
        return

    # 创建智谱AI适配器
    adapter = ZhipuAdapter(
        api_key=api_key,
        model="glm-4-flash"  # 使用快速响应模型
    )

    # 创建AIGC服务
    service = AIGCService(adapter)

    # 生成Prompt
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

    print("\n发送到智谱AI的Prompt:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)

    # 调用智谱AI
    print("\n正在调用智谱AI...")
    print("-" * 60)

    try:
        result = await service.async_analyze_stock_pattern(prompt)
        print("\n智谱AI分析结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)
    except Exception as e:
        print(f"\n❌ 调用失败: {e}")


# ==================== 示例2：使用快速分析函数 ====================
async def example_2_quick_analysis():
    """示例2：使用快速分析函数"""
    print("\n" + "="*60)
    print("示例2：使用快速分析函数")
    print("="*60)

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n⚠️  未配置ZHIPU_API_KEY环境变量")
        return

    # 使用快速分析函数
    result = await quick_analysis(
        stock_code="600036",
        pattern_type="冲板回落",
        aigc_adapter=ZhipuAdapter(api_key=api_key, model="glm-4-flash"),
        trading_style="短线",
        trigger_time="10:15",
        涨幅=9.8,
        回落幅度=5.2,
        封板挂单量=15000,
        成交额放大比例=80.0,
        板块名称="银行",
        板块涨跌幅=-0.5,
        大盘涨跌幅=-0.3,
        最新消息="无"
    )

    if result:
        print("\n分析结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)


# ==================== 示例3：对比不同模型 ====================
async def example_3_model_comparison():
    """示例3：对比智谱AI不同模型"""
    print("\n" + "="*60)
    print("示例3：对比智谱AI不同模型")
    print("="*60)

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n⚠️  未配置ZHIPU_API_KEY环境变量")
        return

    # 测试不同模型
    models = [
        ("glm-4-flash", "快速响应模型（推荐）"),
        ("glm-4-air", "高性价比模型"),
        ("glm-4-plus", "最强模型"),
    ]

    prompt = "股票600000开盘5分钟跌3.2%，板块跌1.2%，大盘跌0.8%。是真跳水还是假跳水？风险等级？操作建议？50字内。"

    for model_name, model_desc in models:
        print(f"\n{'='*60}")
        print(f"模型: {model_name} - {model_desc}")
        print(f"{'='*60}")

        try:
            adapter = ZhipuAdapter(api_key=api_key, model=model_name)
            service = AIGCService(adapter)

            result = await service.async_analyze_stock_pattern(prompt)

            print(f"\n分析结果:")
            print("-" * 60)
            print(result)
            print("-" * 60)
        except Exception as e:
            print(f"\n❌ 调用失败: {e}")


# ==================== 示例4：批量分析 ====================
async def example_4_batch_analysis():
    """示例4：批量分析多个股票"""
    print("\n" + "="*60)
    print("示例4：批量分析多个股票")
    print("="*60)

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n⚠️  未配置ZHIPU_API_KEY环境变量")
        return

    # 批量分析案例
    cases = [
        {
            "stock_code": "600000",
            "pattern_type": "开盘跳水",
            "description": "浦发银行开盘跳水"
        },
        {
            "stock_code": "000001",
            "pattern_type": "破位下跌",
            "description": "平安银行破位下跌"
        },
        {
            "stock_code": "600036",
            "pattern_type": "冲板回落",
            "description": "招商银行冲板回落"
        }
    ]

    adapter = ZhipuAdapter(api_key=api_key, model="glm-4-flash")

    for i, case in enumerate(cases, 1):
        print(f"\n{'='*60}")
        print(f"案例 {i}/{len(cases)}: {case['description']}")
        print(f"{'='*60}")

        try:
            result = await quick_analysis(
                stock_code=case["stock_code"],
                pattern_type=case["pattern_type"],
                aigc_adapter=adapter,
                trading_style="短线"
            )

            print(f"\n分析结果:")
            print("-" * 60)
            print(result)
            print("-" * 60)

            # 避免API限流
            if i < len(cases):
                print("\n等待2秒后处理下一个案例...")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"\n❌ 分析失败: {e}")


# ==================== 主函数 ====================
async def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print(" " * 15 + "智谱AI（ChatGLM）使用示例")
    print("="*70)

    # 检查是否配置了API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("\n⚠️  重要提示：")
        print("   未检测到ZHIPU_API_KEY环境变量")
        print("   请按照以下步骤配置：")
        print("   1. 访问 https://open.bigmodel.cn/usercenter/apikeys 获取API密钥")
        print("   2. 复制.env.example为.env")
        print("   3. 在.env文件中设置：ZHIPU_API_KEY=你的密钥")
        print("   4. 重新运行此示例")
        print("\n   示例将使用模拟模式演示...")
        print("="*70)
        return

    print(f"\n✓ 检测到API密钥配置: {api_key[:10]}...")
    print(f"✓ 智谱AI支持以下模型:")
    print(f"  - glm-4-plus: 最强模型（适合复杂分析）")
    print(f"  - glm-4-air: 高性价比模型（适合日常使用）")
    print(f"  - glm-4-flash: 快速响应模型（推荐，本示例使用）")
    print(f"  - glm-3-turbo: 上一代模型（成本低）")
    print("="*70)

    # 运行示例
    print("\n选择要运行的示例:")
    print("1. 基础使用")
    print("2. 快速分析函数")
    print("3. 对比不同模型")
    print("4. 批量分析")
    print("0. 退出")

    choice = input("\n请选择 [0-4]: ").strip()

    if choice == "1":
        await example_1_basic_usage()
    elif choice == "2":
        await example_2_quick_analysis()
    elif choice == "3":
        await example_3_model_comparison()
    elif choice == "4":
        await example_4_batch_analysis()
    elif choice == "0":
        print("\n退出示例")
    else:
        print("\n无效选择")

    print("\n" + "="*70)
    print("示例运行完成！")
    print("="*70)


if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    # 运行示例
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
