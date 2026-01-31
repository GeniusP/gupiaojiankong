"""
AIGC模型适配器
支持GPT、讯飞星火、文心一言、智谱AI等多种大语言模型
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
from enum import Enum


class ModelProvider(Enum):
    """模型提供商枚举"""
    GPT = "gpt"
    SPARK = "spark"  # 讯飞星火
    QIANFAN = "qianfan"  # 百度千帆（文心一言）
    ZHIPU = "zhipu"  # 智谱AI（ChatGLM）


class AIGCModelAdapter(ABC):
    """AIGC模型适配器抽象基类"""

    def __init__(self, api_key: str, **kwargs):
        """
        初始化模型适配器

        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def chat(self, prompt: str, **kwargs) -> str:
        """
        发送聊天请求

        Args:
            prompt: 用户提示词
            **kwargs: 其他参数（如temperature、max_tokens等）

        Returns:
            模型响应文本
        """
        pass

    @abstractmethod
    def async_chat(self, prompt: str, **kwargs) -> str:
        """
        异步发送聊天请求

        Args:
            prompt: 用户提示词
            **kwargs: 其他参数

        Returns:
            模型响应文本
        """
        pass


class GPTAdapter(AIGCModelAdapter):
    """GPT模型适配器（使用OpenAI API）"""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4-turbo-preview"):
        """
        初始化GPT适配器

        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL
            model: 模型名称
        """
        super().__init__(api_key)
        self.base_url = base_url
        self.model = model
        self._client = None

    def _get_client(self):
        """获取OpenAI客户端（延迟导入）"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError("使用GPT适配器需要安装openai包：pip install openai")
        return self._client

    def chat(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs) -> str:
        """发送GPT聊天请求"""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的股票分析助手，擅长技术分析和风险识别。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"GPT API调用失败: {str(e)}")

    async def async_chat(self, prompt: str, **kwargs) -> str:
        """异步发送GPT聊天请求"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.chat(prompt, **kwargs))


class SparkAdapter(AIGCModelAdapter):
    """
    讯飞星火模型适配器

    注意：讯飞星火使用WebSocket连接，这里提供基础实现
    实际使用时可能需要根据讯飞最新API文档调整
    """

    def __init__(self, app_id: str, api_key: str, api_secret: str, domain: str = "generalv3"):
        """
        初始化讯飞星火适配器

        Args:
            app_id: 应用ID
            api_key: API密钥
            api_secret: API密钥
            domain: 模型域名
        """
        super().__init__(api_key)
        self.app_id = app_id
        self.api_secret = api_secret
        self.domain = domain
        self._client = None

    def _get_client(self):
        """获取讯飞星火客户端"""
        if self._client is None:
            try:
                # 讯飞星火官方SDK
                from sparkai.core.spark_ai import SparkAI
                self._client = SparkAI(
                    app_id=self.app_id,
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    domain=self.domain
                )
            except ImportError:
                raise ImportError("使用讯飞星火适配器需要安装spark-ai包：pip install spark-ai")
        return self._client

    def chat(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs) -> str:
        """发送讯飞星火聊天请求"""
        try:
            client = self._get_client()
            response = client.generate([
                {"role": "user", "content": prompt}
            ])
            return response
        except Exception as e:
            raise Exception(f"讯飞星火API调用失败: {str(e)}")

    async def async_chat(self, prompt: str, **kwargs) -> str:
        """异步发送讯飞星火聊天请求"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.chat(prompt, **kwargs))


class QianfanAdapter(AIGCModelAdapter):
    """
    百度千帆模型适配器（文心一言）
    """

    def __init__(self, access_key: str, secret_key: str, model: str = "ERNIE-Bot-4"):
        """
        初始化千帆适配器

        Args:
            access_key: 访问密钥
            secret_key: 秘密密钥
            model: 模型名称
        """
        super().__init__(access_key)
        self.secret_key = secret_key
        self.model = model
        self._client = None

    def _get_client(self):
        """获取千帆客户端"""
        if self._client is None:
            try:
                from qianfan import ChatCompletion
                self._client = ChatCompletion()
            except ImportError:
                raise ImportError("使用千帆适配器需要安装qianfan包：pip install qianfan")
        return self._client

    def chat(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs) -> str:
        """发送千帆聊天请求"""
        try:
            client = self._get_client()
            response = client.do(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=0.8,
                max_output_tokens=max_tokens
            )
            return response['result']
        except Exception as e:
            raise Exception(f"千帆API调用失败: {str(e)}")

    async def async_chat(self, prompt: str, **kwargs) -> str:
        """异步发送千帆聊天请求"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.chat(prompt, **kwargs))


class ZhipuAdapter(AIGCModelAdapter):
    """
    智谱AI模型适配器（ChatGLM系列）

    支持模型：
    - glm-4-plus: 最新最强模型
    - glm-4-air: 性价比模型
    - glm-4-flash: 快速响应模型
    - glm-3-turbo: 上一代模型
    """

    def __init__(self, api_key: str, model: str = "glm-4-flash"):
        """
        初始化智谱AI适配器

        Args:
            api_key: 智谱AI API密钥（格式：id.secret）
            model: 模型名称
        """
        super().__init__(api_key)
        self.model = model
        self._client = None

    def _get_client(self):
        """获取智谱AI客户端（延迟导入）"""
        if self._client is None:
            try:
                from zhipuai import ZhipuAI
                self._client = ZhipuAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("使用智谱AI适配器需要安装zhipuai包：pip install zhipuai")
        return self._client

    def chat(self, prompt: str, temperature: float = 0.3, max_tokens: int = 500, **kwargs) -> str:
        """发送智谱AI聊天请求"""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的股票分析助手，擅长技术分析和风险识别。输出要简洁明确，避免冗余。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")

    async def async_chat(self, prompt: str, **kwargs) -> str:
        """异步发送智谱AI聊天请求"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.chat(prompt, **kwargs))


class AIGCService:
    """
    AIGC服务统一接口
    支持多种模型的切换和调用
    """

    def __init__(self, adapter: AIGCModelAdapter):
        """
        初始化AIGC服务

        Args:
            adapter: 模型适配器实例
        """
        self.adapter = adapter

    def analyze_stock_pattern(self, prompt: str) -> str:
        """
        分析股票图形

        Args:
            prompt: Prompt模板

        Returns:
            AIGC分析结果
        """
        return self.adapter.chat(
            prompt,
            temperature=0.3,  # 使用较低的温度以获得更确定性的输出
            max_tokens=500
        )

    async def async_analyze_stock_pattern(self, prompt: str) -> str:
        """异步分析股票图形"""
        return await self.adapter.async_chat(
            prompt,
            temperature=0.3,
            max_tokens=500
        )


def create_adapter(
    provider: ModelProvider,
    **config
) -> AIGCModelAdapter:
    """
    创建模型适配器的工厂函数

    Args:
        provider: 模型提供商
        **config: 配置参数

    Returns:
        模型适配器实例

    Example:
        >>> adapter = create_adapter(
        ...     ModelProvider.GPT,
        ...     api_key="sk-xxx",
        ...     model="gpt-4"
        ... )
    """
    if provider == ModelProvider.GPT:
        return GPTAdapter(
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.openai.com/v1"),
            model=config.get("model", "gpt-4-turbo-preview")
        )
    elif provider == ModelProvider.SPARK:
        return SparkAdapter(
            app_id=config.get("app_id"),
            api_key=config.get("api_key"),
            api_secret=config.get("api_secret"),
            domain=config.get("domain", "generalv3")
        )
    elif provider == ModelProvider.QIANFAN:
        return QianfanAdapter(
            access_key=config.get("access_key"),
            secret_key=config.get("secret_key"),
            model=config.get("model", "ERNIE-Bot-4")
        )
    elif provider == ModelProvider.ZHIPU:
        return ZhipuAdapter(
            api_key=config.get("api_key"),
            model=config.get("model", "glm-4-flash")
        )
    else:
        raise ValueError(f"不支持的模型提供商: {provider}")


# 简化的Mock适配器（用于测试）
class MockAIGCAdapter(AIGCModelAdapter):
    """Mock AIGC适配器，用于测试和演示"""

    def __init__(self):
        super().__init__("mock_key")

    def chat(self, prompt: str, **kwargs) -> str:
        """返回模拟响应"""
        if "开盘跳水" in prompt:
            return """判断结果：假跳水
判断依据：与大盘同步下跌，板块跌幅-1.2%与大盘-0.5%基本同步，无主动砸盘迹象
风险等级：中（理由：技术面破位但资金面未恐慌）
操作建议：持有观望（参考价位：支撑位10.00元）"""

        elif "破位下跌" in prompt:
            return """破位判断：假破位（依据：成交量温和放大20%，未出现恐慌性抛售）
核心原因：板块轮动调整，技术面回踩20日均线
短期预判：1-2个交易日内在10.00-10.30区间横盘整理后反弹
操作建议：波段持仓者可持有，短线不建议追空"""

        elif "冲板回落" in prompt:
            return """核心原因：板块资金分流导致抛压过大（抛压强度：中）
走势影响：中性偏空（理由：封板失败但未恐慌，回落幅度可控）
操作建议：已持仓短线交易者建议减仓50%，未持仓观望待企稳"""

        else:
            return """模拟AIGC响应：请提供具体的股票分析需求"""

    async def async_chat(self, prompt: str, **kwargs) -> str:
        """异步聊天"""
        return self.chat(prompt, **kwargs)
