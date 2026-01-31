#!/usr/bin/env python3
"""
智谱AI配置测试脚本
验证API密钥和模型配置是否正确
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_zhipu_connection():
    """测试智谱AI连接"""
    print("\n" + "="*70)
    print(" " * 20 + "智谱AI配置测试")
    print("="*70)

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    # 读取配置
    api_key = os.getenv("ZHIPU_API_KEY")
    model = os.getenv("ZHIPU_MODEL", "glm-4-plus")

    print(f"\n📋 配置信息:")
    print(f"   API密钥: {api_key[:15]}...{api_key[-10:] if api_key else 'None'}")
    print(f"   模型: {model}")

    if not api_key:
        print("\n❌ 错误：未配置ZHIPU_API_KEY")
        return False

    print("\n🔌 正在连接智谱AI...")

    try:
        # 导入智谱AI SDK
        from zhipuai import ZhipuAI

        # 创建客户端
        client = ZhipuAI(api_key=api_key)

        print("✓ 客户端创建成功")

        # 测试调用
        print("\n🤖 发送测试请求...")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的股票分析助手。"
                },
                {
                    "role": "user",
                    "content": "股票600000开盘5分钟跌3%，板块跌1%，是真跳水还是假跳水？请用一句话回答。"
                }
            ],
            temperature=0.3,
            max_tokens=100
        )

        result = response.choices[0].message.content

        print("\n✓ API调用成功！")
        print(f"\n📊 模型回复:")
        print("-" * 70)
        print(result)
        print("-" * 70)

        # 显示token使用情况
        if hasattr(response, 'usage') and response.usage:
            print(f"\n📈 Token使用:")
            print(f"   输入: {response.usage.prompt_tokens} tokens")
            print(f"   输出: {response.usage.completion_tokens} tokens")
            print(f"   总计: {response.usage.total_tokens} tokens")

        print("\n" + "="*70)
        print("✓ 配置测试成功！智谱AI已正常工作。")
        print("="*70)

        return True

    except ImportError as e:
        print(f"\n❌ 错误：未安装zhipuai包")
        print(f"   请运行: pip install zhipuai")
        print(f"   详细错误: {e}")
        return False

    except Exception as e:
        print(f"\n❌ API调用失败")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")

        # 提供常见错误的解决建议
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg:
            print("\n💡 建议：API密钥可能无效，请检查:")
            print("   1. 密钥是否正确复制")
            print("   2. 密钥是否已过期")
            print("   3. 访问 https://open.bigmodel.cn/usercenter/apikeys 重新获取")
        elif "timeout" in error_msg:
            print("\n💡 建议：网络连接超时")
            print("   1. 检查网络连接")
            print("   2. 尝试使用代理")
        elif "rate limit" in error_msg:
            print("\n💡 建议：请求过于频繁")
            print("   1. 稍后重试")
            print("   2. 检查账户余额")

        return False


async def test_stock_analysis():
    """测试完整的股票分析流程"""
    print("\n" + "="*70)
    print(" " * 18 + "完整股票分析测试")
    print("="*70)

    try:
        from src.aigc.model_adapter import ZhipuAdapter, AIGCService
        from src.templates.prompt_templates import generate_prompt, TemplateType

        # 创建适配器
        adapter = ZhipuAdapter(
            api_key=os.getenv("ZHIPU_API_KEY"),
            model=os.getenv("ZHIPU_MODEL", "glm-4-plus")
        )

        # 创建服务
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
                "当日成交额放大比例": 20.3,
                "板块名称": "银行",
                "板块涨跌幅": -1.2,
                "大盘名称": "上证指数",
                "大盘涨跌幅": -0.8,
                "最新消息": "无",
                "额外特征": "开盘5分钟快速下跌"
            },
            trading_style="短线",
            template_type=TemplateType.SIMPLIFIED
        )

        print("\n📝 生成的Prompt:")
        print("-" * 70)
        print(prompt)
        print("-" * 70)

        print("\n🤖 正在分析...")
        result = await service.async_analyze_stock_pattern(prompt)

        print("\n✓ 分析完成！")
        print(f"\n📊 分析结果:")
        print("-" * 70)
        print(result)
        print("-" * 70)

        print("\n" + "="*70)
        print("✓ 完整测试成功！系统可以正常进行股票分析。")
        print("="*70)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("\n🎯 开始测试智谱AI配置...")

    # 测试1: 基础连接测试
    success1 = await test_zhipu_connection()

    if not success1:
        print("\n⚠️  基础连接测试失败，跳过完整测试")
        return

    # 等待用户确认
    print("\n是否继续进行完整的股票分析测试？")
    choice = input("输入 y 继续，其他键退出: ").strip().lower()

    if choice == 'y':
        # 测试2: 完整分析流程
        await test_stock_analysis()
    else:
        print("\n✓ 基础测试完成，可以开始使用了！")
        print("\n💡 快速开始:")
        print("   1. 运行示例: python examples/zhipu_example.py")
        print("   2. 快速启动: python quick_start.py")
        print("   3. 查看文档: docs/ZHIPU_AI_GUIDE.md")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
