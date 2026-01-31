"""
股票AIGC监控系统
基于大语言模型的股票图形监控和分析系统
"""

__version__ = "1.0.0"
__author__ = "Stock AI Monitor Team"

from .templates.prompt_templates import (
    PromptTemplateManager,
    ChartType,
    TemplateType,
    generate_prompt
)

from .models.stock_data import (
    StockMarketData,
    AIGCResponse,
    MonitorTrigger
)

from .monitors.data_collector import (
    DataCollector,
    StockDataAggregator,
    create_monitoring_data
)

from .monitors.stock_monitor import (
    StockPatternMonitor,
    PatternType,
    TradingStyle,
    quick_analysis
)

from .aigc.model_adapter import (
    AIGCModelAdapter,
    AIGCService,
    ModelProvider,
    create_adapter,
    MockAIGCAdapter
)

__all__ = [
    # Templates
    "PromptTemplateManager",
    "ChartType",
    "TemplateType",
    "generate_prompt",

    # Models
    "StockMarketData",
    "AIGCResponse",
    "MonitorTrigger",

    # Data Collection
    "DataCollector",
    "StockDataAggregator",
    "create_monitoring_data",

    # Monitor
    "StockPatternMonitor",
    "PatternType",
    "TradingStyle",
    "quick_analysis",

    # AIGC
    "AIGCModelAdapter",
    "AIGCService",
    "ModelProvider",
    "create_adapter",
    "MockAIGCAdapter",
]
