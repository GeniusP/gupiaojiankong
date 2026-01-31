"""
配置管理模块
从环境变量和配置文件中加载配置
"""

import os
from typing import Optional
from dotenv import load_dotenv
from enum import Enum

# 加载.env文件
load_dotenv()


class ModelProvider(Enum):
    """模型提供商"""
    GPT = "gpt"
    SPARK = "spark"
    QIANFAN = "qianfan"
    ZHIPU = "zhipu"  # 智谱AI


class Config:
    """配置管理类"""

    # AIGC模型配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    SPARK_APP_ID: str = os.getenv("SPARK_APP_ID", "")
    SPARK_API_KEY: str = os.getenv("SPARK_API_KEY", "")
    SPARK_API_SECRET: str = os.getenv("SPARK_API_SECRET", "")
    SPARK_DOMAIN: str = os.getenv("SPARK_DOMAIN", "generalv3")

    QIANFAN_ACCESS_KEY: str = os.getenv("QIANFAN_ACCESS_KEY", "")
    QIANFAN_SECRET_KEY: str = os.getenv("QIANFAN_SECRET_KEY", "")
    QIANFAN_MODEL: str = os.getenv("QIANFAN_MODEL", "ERNIE-Bot-4")

    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4-flash")

    DEFAULT_AIGC_MODEL: str = os.getenv("DEFAULT_AIGC_MODEL", "gpt")

    # 数据源配置
    STOCK_API_BASE_URL: str = os.getenv("STOCK_API_BASE_URL", "")
    STOCK_API_KEY: str = os.getenv("STOCK_API_KEY", "")

    # 监控配置
    MONITOR_INTERVAL_SECONDS: int = int(os.getenv("MONITOR_INTERVAL_SECONDS", "60"))
    TRADING_STYLE: str = os.getenv("TRADING_STYLE", "short")

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/monitor.log")

    @classmethod
    def get_model_config(cls, provider: ModelProvider) -> dict:
        """
        获取指定模型的配置

        Args:
            provider: 模型提供商

        Returns:
            配置字典
        """
        if provider == ModelProvider.GPT:
            return {
                "api_key": cls.OPENAI_API_KEY,
                "base_url": cls.OPENAI_BASE_URL,
                "model": cls.OPENAI_MODEL
            }
        elif provider == ModelProvider.SPARK:
            return {
                "app_id": cls.SPARK_APP_ID,
                "api_key": cls.SPARK_API_KEY,
                "api_secret": cls.SPARK_API_SECRET,
                "domain": cls.SPARK_DOMAIN
            }
        elif provider == ModelProvider.QIANFAN:
            return {
                "access_key": cls.QIANFAN_ACCESS_KEY,
                "secret_key": cls.QIANFAN_SECRET_KEY,
                "model": cls.QIANFAN_MODEL
            }
        elif provider == ModelProvider.ZHIPU:
            return {
                "api_key": cls.ZHIPU_API_KEY,
                "model": cls.ZHIPU_MODEL
            }
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")

    @classmethod
    def validate(cls) -> bool:
        """
        验证配置是否有效

        Returns:
            是否有效
        """
        errors = []

        # 验证默认模型的配置
        default_provider = ModelProvider(cls.DEFAULT_AIGC_MODEL)
        config = cls.get_model_config(default_provider)

        if default_provider == ModelProvider.GPT:
            if not config["api_key"]:
                errors.append("未配置OPENAI_API_KEY")
        elif default_provider == ModelProvider.SPARK:
            if not config["app_id"] or not config["api_key"] or not config["api_secret"]:
                errors.append("未配置完整的讯飞星火认证信息（APP_ID/API_KEY/API_SECRET）")
        elif default_provider == ModelProvider.QIANFAN:
            if not config["access_key"] or not config["secret_key"]:
                errors.append("未配置完整的千帆认证信息（ACCESS_KEY/SECRET_KEY）")
        elif default_provider == ModelProvider.ZHIPU:
            if not config["api_key"]:
                errors.append("未配置智谱AI API密钥（ZHIPU_API_KEY）")

        if errors:
            print("⚠️  配置验证失败:")
            for error in errors:
                print(f"   - {error}")
            return False

        return True


def print_config_summary():
    """打印配置摘要"""
    print("=" * 60)
    print("股票AIGC监控系统 - 配置摘要")
    print("=" * 60)
    print(f"默认AIGC模型: {Config.DEFAULT_AIGC_MODEL}")
    print(f"交易风格: {Config.TRADING_STYLE}")
    print(f"监控间隔: {Config.MONITOR_INTERVAL_SECONDS}秒")
    print(f"日志级别: {Config.LOG_LEVEL}")
    print("=" * 60)


if __name__ == "__main__":
    print_config_summary()
    print(f"\n配置验证: {'✓ 通过' if Config.validate() else '✗ 失败'}")
