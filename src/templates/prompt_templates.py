"""
股票AIGC监控Prompt模板管理器
支持开盘跳水、破位下跌、冲板回落三类图形的完整版和简化版模板
"""

from typing import Dict, Any, Optional
from enum import Enum


class ChartType(Enum):
    """图形类型枚举"""
    OPENING_DIVE = "开盘跳水"
    BREAKDOWN_FALL = "破位下跌"
    SURGE_RETRACE = "冲板回落"


class TemplateType(Enum):
    """模板类型枚举"""
    FULL = "完整版"
    SIMPLIFIED = "简化版"


class PromptTemplateManager:
    """Prompt模板管理器"""

    @staticmethod
    def _build_supplementary_data(stock_data: Dict[str, Any]) -> str:
        """
        构建通用补充维度数据

        Args:
            stock_data: 股票数据字典，包含以下字段：
                - 股票代码, 股票名称, 触发时间, 图形类型
                - 开盘价, 实时价, 最高价, 涨停价
                - 5日均线, 20日均线, 前期平台支撑位
                - 触发成交额, 成交额放大比例, 当日成交额放大比例, 分钟成交额放大比例
                - 板块名称, 板块涨跌幅
                - 大盘名称, 大盘涨跌幅
                - 最新消息
                - 额外特征

        Returns:
            格式化的补充维度数据字符串
        """
        return (
            f"{stock_data.get('股票代码', '')} {stock_data.get('股票名称', '')}，"
            f"今日{stock_data.get('触发时间', '')}触发{stock_data.get('图形类型', '')}规则，"
            f"补充数据如下：\n"
            f"1. 行情数据：{stock_data.get('开盘价', '')}、实时价{stock_data.get('实时价', '')}、"
            f"最高价{stock_data.get('最高价', '')}、涨停价{stock_data.get('涨停价', '')}、"
            f"5日均线{stock_data.get('5日均线', '')}、20日均线{stock_data.get('20日均线', '')}、"
            f"前期平台支撑位{stock_data.get('前期平台支撑位', '')}；\n"
            f"2. 成交量数据：触发时成交额{stock_data.get('触发成交额', '')}、"
            f"较前5日均值放大{stock_data.get('成交额放大比例', '')}%、"
            f"较当日均值放大{stock_data.get('当日成交额放大比例', '')}%、"
            f"较前1分钟放大{stock_data.get('分钟成交额放大比例', '')}%；\n"
            f"3. 市场环境：所属板块{stock_data.get('板块名称', '')}"
            f"（今日板块涨跌幅{stock_data.get('板块涨跌幅', '')}%）、"
            f"大盘指数{stock_data.get('大盘名称', '')}"
            f"（今日涨跌幅{stock_data.get('大盘涨跌幅', '')}%）；\n"
            f"4. 消息面：{stock_data.get('最新消息', '无')}；\n"
            f"5. 额外特征：{stock_data.get('额外特征', '')}"
        )

    @staticmethod
    def get_opening_dive_template(
        stock_data: Dict[str, Any],
        trading_style: str = "短线",
        template_type: TemplateType = TemplateType.FULL
    ) -> str:
        """
        获取开盘跳水Prompt模板

        Args:
            stock_data: 股票数据字典
            trading_style: 交易风格（短线/波段/长线）
            template_type: 模板类型（完整版/简化版）

        Returns:
            完整的Prompt字符串
        """
        if template_type == TemplateType.SIMPLIFIED:
            # 简化版模板
            return (
                f"股票{stock_data.get('股票代码', '')} {stock_data.get('股票名称', '')}，"
                f"{stock_data.get('触发时间', '')}开盘{stock_data.get('开盘分钟数', '')}分钟"
                f"跌{stock_data.get('跌幅', '')}%，"
                f"跌破{stock_data.get('均线类型', '')}日均线{stock_data.get('均线价格', '')}，"
                f"成交额放大{stock_data.get('成交额放大比例', '')}%，"
                f"板块{stock_data.get('板块名称', '')}跌{stock_data.get('板块涨跌幅', '')}%，"
                f"大盘跌{stock_data.get('大盘涨跌幅', '')}%。"
                f"判断是真/假跳水？风险高/中/低？{trading_style}该规避/持有/止损？给出关键价位，50字内。"
            )

        # 完整版模板
        supplementary_data = PromptTemplateManager._build_supplementary_data(stock_data)

        return (
            f"{supplementary_data}\n\n"
            f"请完成3件事：\n"
            f"1. 判断该标的是【真开盘跳水（资金主动出逃）】还是【假跳水（板块/大盘联动被动下跌）】，"
            f"给出1条核心判断依据；\n"
            f"2. 基于技术面+市场环境，判定风险等级（高/中/低），说明理由；\n"
            f"3. 针对{trading_style}交易者，给出明确操作建议（规避/持有/止盈/止损），"
            f"标注关键参考价位（如支撑位/压力位）。\n\n"
            f"输出格式要求：\n"
            f"判断结果：XXX\n"
            f"判断依据：XXX\n"
            f"风险等级：XXX（理由：XXX）\n"
            f"操作建议：XXX（参考价位：XXX）\n"
            f"总字数控制在150字内，语言简洁，无冗余表述。"
        )

    @staticmethod
    def get_breakdown_fall_template(
        stock_data: Dict[str, Any],
        trading_style: str = "短线",
        template_type: TemplateType = TemplateType.FULL
    ) -> str:
        """
        获取破位下跌Prompt模板

        Args:
            stock_data: 股票数据字典
            trading_style: 交易风格（短线/波段/长线）
            template_type: 模板类型（完整版/简化版）

        Returns:
            完整的Prompt字符串
        """
        if template_type == TemplateType.SIMPLIFIED:
            # 简化版模板
            return (
                f"股票{stock_data.get('股票代码', '')} {stock_data.get('股票名称', '')}，"
                f"{stock_data.get('触发时间', '')}跌破支撑位{stock_data.get('支撑位价格', '')}，"
                f"放量{stock_data.get('成交额放大比例', '')}%，"
                f"板块{stock_data.get('板块名称', '')}跌{stock_data.get('板块涨跌幅', '')}%，"
                f"有{stock_data.get('最新消息', '无')}。"
                f"是真/假破位？短期涨/跌？{trading_style}操作建议？50字内。"
            )

        # 完整版模板
        supplementary_data = PromptTemplateManager._build_supplementary_data(stock_data)

        return (
            f"{supplementary_data}\n\n"
            f"请完成3件事：\n"
            f"1. 判断该破位是【真破位（趋势走坏）】还是【假破位（洗盘/误杀）】，"
            f"结合成交量和支撑位重要性说明依据；\n"
            f"2. 分析破位下跌的核心原因（资金面/板块/消息面/大盘，选1-2个核心因素）；\n"
            f"3. 预判短期（1-2个交易日）技术面走势（反弹/继续下跌/横盘），"
            f"给出{trading_style}对应的操作建议。\n\n"
            f"输出格式要求：\n"
            f"破位判断：XXX（依据：XXX）\n"
            f"核心原因：XXX\n"
            f"短期预判：XXX\n"
            f"操作建议：XXX\n"
            f"总字数控制在150字内，结论明确，不模糊表述。"
        )

    @staticmethod
    def get_surge_retrace_template(
        stock_data: Dict[str, Any],
        position_status: str = "已持仓",
        trading_style: str = "短线",
        template_type: TemplateType = TemplateType.FULL
    ) -> str:
        """
        获取冲板回落Prompt模板

        Args:
            stock_data: 股票数据字典
            position_status: 持仓状态（已持仓/未持仓）
            trading_style: 交易风格（短线/波段/长线）
            template_type: 模板类型（完整版/简化版）

        Returns:
            完整的Prompt字符串
        """
        if template_type == TemplateType.SIMPLIFIED:
            # 简化版模板
            return (
                f"股票{stock_data.get('股票代码', '')} {stock_data.get('股票名称', '')}，"
                f"{stock_data.get('触发时间', '')}冲至{stock_data.get('涨幅', '')}%未封板，"
                f"回落{stock_data.get('回落幅度', '')}%，"
                f"放量{stock_data.get('成交额放大比例', '')}%，"
                f"封板挂单{stock_data.get('封板挂单量', '')}手。"
                f"抛压强/弱？{trading_style}该持有/清仓/观望？50字内。"
            )

        # 完整版模板
        supplementary_data = PromptTemplateManager._build_supplementary_data(stock_data)

        return (
            f"{supplementary_data}\n\n"
            f"请完成3件事：\n"
            f"1. 分析冲板回落的核心原因（抛压过大/主力诱多/板块资金分流），判断抛压强度（强/中/弱）；\n"
            f"2. 判定该图形对短期（1-2个交易日）走势的影响（偏空/中性/偏多），说明理由；\n"
            f"3. 针对{position_status}的{trading_style}交易者，"
            f"给出具体操作建议（加仓/减仓/清仓/观望）。\n\n"
            f"输出格式要求：\n"
            f"核心原因：XXX（抛压强度：XXX）\n"
            f"走势影响：XXX（理由：XXX）\n"
            f"操作建议：XXX\n"
            f"总字数控制在150字内，聚焦实际交易决策，避免理论化表述。"
        )

    @classmethod
    def get_template(
        cls,
        chart_type: ChartType,
        stock_data: Dict[str, Any],
        trading_style: str = "短线",
        position_status: str = "已持仓",
        template_type: TemplateType = TemplateType.FULL
    ) -> str:
        """
        根据图形类型获取对应的Prompt模板

        Args:
            chart_type: 图形类型（开盘跳水/破位下跌/冲板回落）
            stock_data: 股票数据字典
            trading_style: 交易风格（短线/波段/长线）
            position_status: 持仓状态（已持仓/未持仓）
            template_type: 模板类型（完整版/简化版）

        Returns:
            完整的Prompt字符串
        """
        if chart_type == ChartType.OPENING_DIVE:
            return cls.get_opening_dive_template(stock_data, trading_style, template_type)
        elif chart_type == ChartType.BREAKDOWN_FALL:
            return cls.get_breakdown_fall_template(stock_data, trading_style, template_type)
        elif chart_type == ChartType.SURGE_RETRACE:
            return cls.get_surge_retrace_template(stock_data, position_status, trading_style, template_type)
        else:
            raise ValueError(f"不支持的图形类型: {chart_type}")


# 便捷函数：快速生成Prompt
def generate_prompt(
    chart_type: str,
    stock_data: Dict[str, Any],
    **kwargs
) -> str:
    """
    快速生成Prompt的便捷函数

    Args:
        chart_type: 图形类型字符串（"开盘跳水"/"破位下跌"/"冲板回落"）
        stock_data: 股票数据字典
        **kwargs: 其他可选参数（trading_style, position_status, template_type）

    Returns:
        完整的Prompt字符串

    Example:
        >>> stock_data = {
        ...     "股票代码": "600000",
        ...     "股票名称": "浦发银行",
        ...     "触发时间": "09:35",
        ...     "开盘价": 10.5,
        ...     "实时价": 10.2,
        ...     # ... 其他字段
        ... }
        >>> prompt = generate_prompt("开盘跳水", stock_data, trading_style="短线")
    """
    # 字符串转换为枚举
    chart_type_map = {
        "开盘跳水": ChartType.OPENING_DIVE,
        "破位下跌": ChartType.BREAKDOWN_FALL,
        "冲板回落": ChartType.SURGE_RETRACE
    }

    chart_type_enum = chart_type_map.get(chart_type)
    if not chart_type_enum:
        raise ValueError(f"不支持的图形类型: {chart_type}，请使用：开盘跳水/破位下跌/冲板回落")

    return PromptTemplateManager.get_template(
        chart_type_enum,
        stock_data,
        trading_style=kwargs.get("trading_style", "短线"),
        position_status=kwargs.get("position_status", "已持仓"),
        template_type=kwargs.get("template_type", TemplateType.FULL)
    )
