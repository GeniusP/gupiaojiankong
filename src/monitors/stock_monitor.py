"""
股票图形监控器
实现开盘跳水、破位下跌、冲板回落三类图形的识别和触发判断
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, time
from enum import Enum
import asyncio

from ..templates.prompt_templates import PromptTemplateManager, ChartType, TemplateType
from ..models.stock_data import StockMarketData, AIGCResponse, MonitorTrigger
from ..aigc.model_adapter import AIGCService, ModelProvider
from .data_collector import StockDataAggregator


class PatternType(Enum):
    """图形类型枚举"""
    OPENING_DIVE = "开盘跳水"
    BREAKDOWN_FALL = "破位下跌"
    SURGE_RETRACE = "冲板回落"


class TradingStyle(Enum):
    """交易风格枚举"""
    SHORT = "短线"
    MEDIUM = "波段"
    LONG = "长线"


class PatternRule:
    """图形识别规则"""

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        description: str
    ):
        """
        初始化识别规则

        Args:
            name: 规则名称
            condition: 判断函数，接受市场数据返回布尔值
            description: 规则描述
        """
        self.name = name
        self.condition = condition
        self.description = description


class StockPatternMonitor:
    """
    股票图形监控器
    """

    def __init__(
        self,
        data_aggregator: StockDataAggregator,
        aigc_service: AIGCService,
        trading_style: TradingStyle = TradingStyle.SHORT,
        template_type: TemplateType = TemplateType.FULL
    ):
        """
        初始化监控器

        Args:
            data_aggregator: 数据聚合器
            aigc_service: AIGC服务
            trading_style: 交易风格
            template_type: 模板类型
        """
        self.data_aggregator = data_aggregator
        self.aigc_service = aigc_service
        self.trading_style = trading_style
        self.template_type = template_type

        # 初始化识别规则
        self._init_rules()

    def _init_rules(self):
        """初始化图形识别规则"""

        # 开盘跳水规则
        self.opening_dive_rules = [
            PatternRule(
                name="开盘5分钟跳水",
                condition=lambda data: self._check_opening_dive(data, minutes=5, drop_percent=3),
                description="开盘5分钟内跌幅超过3%"
            ),
            PatternRule(
                name="开盘10分钟跳水",
                condition=lambda data: self._check_opening_dive(data, minutes=10, drop_percent=2),
                description="开盘10分钟内跌幅超过2%"
            )
        ]

        # 破位下跌规则
        self.breakdown_rules = [
            PatternRule(
                name="跌破5日均线",
                condition=lambda data: self._check_breakdown(data, ma_type=5),
                description="跌破5日均线且放量"
            ),
            PatternRule(
                name="跌破20日均线",
                condition=lambda data: self._check_breakdown(data, ma_type=20),
                description="跌破20日均线且放量"
            ),
            PatternRule(
                name="跌破平台支撑位",
                condition=lambda data: self._check_support_breakdown(data),
                description="跌破前期平台支撑位且3分钟未回弹"
            )
        ]

        # 冲板回落规则
        self.surge_retrace_rules = [
            PatternRule(
                name="冲板回落超5%",
                condition=lambda data: self._check_surge_retrace(data, retrace_percent=5),
                description="冲至涨停板后回落超过5%"
            ),
            PatternRule(
                name="冲高回落超3%",
                condition=lambda data: self._check_surge_retrace(data, surge_percent=8, retrace_percent=3),
                description="冲高超8%后回落超过3%"
            )
        ]

    def _check_opening_dive(self, data: Dict[str, Any], minutes: int, drop_percent: float) -> bool:
        """检查开盘跳水"""
        current_price = data.get("实时价") or 0
        open_price = data.get("开盘价") or 0
        open_minutes = data.get("开盘分钟数") or 0

        if open_price == 0 or current_price == 0:
            return False

        drop_ratio = round((open_price - current_price) / open_price * 100, 2)  # 四舍五入到2位小数
        return open_minutes <= minutes and drop_ratio >= drop_percent

    def _check_breakdown(self, data: Dict[str, Any], ma_type: int) -> bool:
        """检查破位下跌"""
        current_price = data.get("实时价") or 0
        ma_price = data.get(f"{ma_type}日均线") or 0
        volume_increase = data.get("成交额放大比例") or 0

        return (
            current_price < ma_price and
            volume_increase > 20  # 成交额放大超过20%
        )

    def _check_support_breakdown(self, data: Dict[str, Any]) -> bool:
        """检查支撑位破位"""
        current_price = data.get("实时价") or 0
        support_price = data.get("前期平台支撑位") or 0
        minutes_no_rebound = data.get("破位后未回弹分钟数") or 0
        volume_increase = data.get("成交额放大比例") or 0

        return (
            current_price < support_price and
            minutes_no_rebound >= 3 and
            volume_increase > 15
        )

    def _check_surge_retrace(
        self,
        data: Dict[str, Any],
        surge_percent: float = 9.9,
        retrace_percent: float = 5
    ) -> bool:
        """检查冲板回落"""
        current_price = data.get("实时价") or 0
        high_price = data.get("最高价") or 0
        open_price = data.get("开盘价") or 0
        limit_up_price = data.get("涨停价") or 0

        if open_price == 0 or high_price == 0:
            return False

        # 计算涨幅
        surge = round((high_price - open_price) / open_price * 100, 2)  # 四舍五入到2位小数
        # 计算回落幅度
        retrace = round((high_price - current_price) / high_price * 100, 2)  # 四舍五入到2位小数

        return surge >= surge_percent and retrace >= retrace_percent

    def detect_pattern(
        self,
        stock_code: str,
        pattern_type: PatternType,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        检测指定图形是否触发

        Args:
            stock_code: 股票代码
            pattern_type: 图形类型
            **kwargs: 额外参数

        Returns:
            如果触发，返回完整的市场数据；否则返回None
        """
        # 采集数据
        trigger_time = kwargs.pop("trigger_time", datetime.now().strftime("%H:%M"))
        market_data = self.data_aggregator.collect_monitoring_data(
            stock_code=stock_code,
            chart_type=pattern_type.value,
            trigger_time=trigger_time,
            **kwargs
        )

        # 根据图形类型选择规则
        if pattern_type == PatternType.OPENING_DIVE:
            rules = self.opening_dive_rules
        elif pattern_type == PatternType.BREAKDOWN_FALL:
            rules = self.breakdown_rules
        elif pattern_type == PatternType.SURGE_RETRACE:
            rules = self.surge_retrace_rules
        else:
            return None

        # 检查是否满足任一规则
        for rule in rules:
            if rule.condition(market_data):
                print(f"✓ 触发规则: {rule.name} - {rule.description}")
                return market_data

        return None

    async def analyze_pattern(
        self,
        stock_code: str,
        pattern_type: PatternType,
        position_status: str = "已持仓",
        **kwargs
    ) -> Optional[MonitorTrigger]:
        """
        检测并分析图形

        Args:
            stock_code: 股票代码
            pattern_type: 图形类型
            position_status: 持仓状态
            **kwargs: 其他参数

        Returns:
            监控触发事件对象，如果未触发则返回None
        """
        # 1. 检测图形
        market_data = self.detect_pattern(stock_code, pattern_type, **kwargs)
        if not market_data:
            return None

        # 2. 生成Prompt
        prompt = PromptTemplateManager.get_template(
            chart_type=ChartType(pattern_type.value),
            stock_data=market_data,
            trading_style=self.trading_style.value,
            position_status=position_status,
            template_type=self.template_type
        )

        print(f"\n{'='*60}")
        print(f"检测到 {pattern_type.value}: {market_data['股票代码']} {market_data['股票名称']}")
        print(f"{'='*60}")
        print(f"生成Prompt:\n{prompt}\n")

        # 3. 调用AIGC分析
        try:
            aigc_response = await self.aigc_service.async_analyze_stock_pattern(prompt)
            print(f"AIGC分析结果:\n{aigc_response}\n")

            # 4. 创建触发事件
            trigger_event = MonitorTrigger(
                事件ID=f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stock_code}",
                股票代码=stock_code,
                股票名称=market_data["股票名称"],
                图形类型=pattern_type.value,
                触发时间=datetime.now(),
                市场数据=StockMarketData(**market_data),
                已处理=True,
                AIGC分析结果=AIGCResponse(原始回复=aigc_response)
            )

            return trigger_event

        except Exception as e:
            print(f"❌ AIGC分析失败: {str(e)}")
            return None

    def batch_detect(
        self,
        stock_codes: List[str],
        pattern_types: List[PatternType]
    ) -> List[Dict[str, Any]]:
        """
        批量检测多个股票的多种图形

        Args:
            stock_codes: 股票代码列表
            pattern_types: 图形类型列表

        Returns:
            触发的事件列表
        """
        detected = []

        for stock_code in stock_codes:
            for pattern_type in pattern_types:
                result = self.detect_pattern(stock_code, pattern_type)
                if result:
                    detected.append({
                        "股票代码": stock_code,
                        "图形类型": pattern_type.value,
                        "市场数据": result
                    })

        return detected


# 便捷函数
async def quick_analysis(
    stock_code: str,
    pattern_type: str,
    aigc_adapter,
    trading_style: str = "短线",
    **data_kwargs
) -> Optional[str]:
    """
    快速分析函数（简化版，适合快速调用）

    Args:
        stock_code: 股票代码
        pattern_type: 图形类型（"开盘跳水"/"破位下跌"/"冲板回落"）
        aigc_adapter: AIGC适配器
        trading_style: 交易风格
        **data_kwargs: 数据参数

    Returns:
        AIGC分析结果文本

    Example:
        >>> from src.aigc.model_adapter import MockAIGCAdapter
        >>> result = await quick_analysis(
        ...     "600000",
        ...     "开盘跳水",
        ...     MockAIGCAdapter(),
        ...     开盘分钟数=5,
        ...     跌幅=3.2
        ... )
    """
    # 使用真实数据采集器（优先使用腾讯财经API）
    try:
        from .tencent_collector import UnifiedRealDataCollector
        collector = UnifiedRealDataCollector()
    except Exception as e:
        print(f"⚠️  警告: 无法使用真实数据采集器: {e}")
        print("   请确保已安装 requests 库: pip install requests")
        from .data_collector import MockDataCollector
        collector = MockDataCollector()

    # 创建监控器
    aggregator = StockDataAggregator(collector)
    aigc_service = AIGCService(aigc_adapter)
    monitor = StockPatternMonitor(
        aggregator,
        aigc_service,
        TradingStyle(trading_style),
        TemplateType.SIMPLIFIED if "简化" in str(data_kwargs.get("template_type", "")) else TemplateType.FULL
    )

    # 执行分析
    trigger_event = await monitor.analyze_pattern(
        stock_code=stock_code,
        pattern_type=PatternType(pattern_type),
        **data_kwargs
    )

    return trigger_event.AIGC分析结果.原始回复 if trigger_event else None
