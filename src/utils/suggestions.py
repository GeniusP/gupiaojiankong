#!/usr/bin/env python3
"""
操作建议生成器
针对不同图形类型和市场状态，提供具体的操作建议
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class OperationSuggestion:
    """操作建议"""
    action: str  # 买入/卖出/观望/加仓/减仓/止损
    confidence: str  # 高/中/低
    reasoning: str  # 建议理由
    price_level: Dict[str, float]  # 关键价位
    risk_warning: str  # 风险提示


class OperationSuggestionGenerator:
    """操作建议生成器"""

    @staticmethod
    def generate_suggestion(
        pattern_type: str,
        stock_data: Dict,
        ai_analysis: str
    ) -> OperationSuggestion:
        """
        根据图形类型和AI分析生成操作建议

        Args:
            pattern_type: 图形类型（开盘跳水、冲板回落、破位下跌）
            stock_data: 股票数据
            ai_analysis: AI分析结果

        Returns:
            OperationSuggestion: 操作建议
        """

        stock_name = stock_data.get("股票名称")
        current_price = stock_data.get("实时价", 0)
        open_price = stock_data.get("开盘价", 0)

        if pattern_type == "开盘跳水":
            return OperationSuggestionGenerator._suggest_opening_dive(
                stock_data, ai_analysis
            )
        elif pattern_type == "冲板回落":
            return OperationSuggestionGenerator._suggest_surge_retrace(
                stock_data, ai_analysis
            )
        elif pattern_type == "破位下跌":
            return OperationSuggestionGenerator._suggest_breakdown(
                stock_data, ai_analysis
            )
        else:
            # 默认建议
            return OperationSuggestion(
                action="观望",
                confidence="低",
                reasoning=f"当前市场状态为'{pattern_type}'，建议保持观望，等待明确信号",
                price_level={},
                risk_warning="市场状态不明确，建议谨慎操作"
            )

    @staticmethod
    def _suggest_opening_dive(stock_data: Dict, ai_analysis: str) -> OperationSuggestion:
        """
        开盘跳水操作建议

        判断依据：
        - 是否真跳水（资金主动出逃 vs 假跳水）
        - 跌幅大小
        - 是否跌破关键支撑位
        - 成交量放大情况
        """

        stock_name = stock_data.get("股票名称")
        current_price = stock_data.get("实时价", 0)
        open_price = stock_data.get("开盘价", 0)
        drop_pct = ((open_price - current_price) / open_price * 100) if open_price > 0 else 0
        volume = stock_data.get("成交量", 0)

        # 支撑位和压力位
        support_5ma = current_price * 0.98
        support_20ma = current_price * 0.96
        resistance = open_price

        # 根据跌幅分级建议
        if drop_pct >= 5:
            # 重跳水（跌幅≥5%）
            return OperationSuggestion(
                action="观望",
                confidence="高",
                reasoning=f"{stock_name}开盘重跳水{drop_pct:.2f}%，资金主动出逃迹象明显。"
                          f"建议等待企稳信号，可在反弹至{resistance:.2f}元附近轻仓试探，"
                          f"或等待跌破{support_5ma:.2f}元后确认再考虑。",
                price_level={
                    "支撑位1": round(support_5ma, 2),
                    "支撑位2": round(support_20ma, 2),
                    "压力位": round(resistance, 2),
                    "当前价": round(current_price, 2)
                },
                risk_warning=f"重跳水风险极高，严禁抄底。如必须操作，仓位控制在10%以内，止损设在{support_20ma:.2f}元"
            )
        elif drop_pct >= 3:
            # 中等跳水
            return OperationSuggestion(
                action="观望或轻仓试探",
                confidence="中",
                reasoning=f"{stock_name}开盘跳水{drop_pct:.2f}%，需要观察是否有资金承接。"
                          f"如果出现快速反弹并站稳{open_price:.2f}元上方，可考虑轻仓跟进。"
                          f"若继续下探，建议等待企稳。",
                price_level={
                    "观察位": round(open_price, 2),
                    "支撑位": round(support_5ma, 2),
                    "止损位": round(current_price * 0.97, 2)
                },
                risk_warning=f"中等风险，建议分批操作。首次试探仓位不超过20%，严格止损{support_5ma:.2f}元"
            )
        else:
            # 轻微跳水
            return OperationSuggestion(
                action="谨慎观望",
                confidence="低",
                reasoning=f"{stock_name}小幅跳水{drop_pct:.2f}%，可能是正常波动。"
                          f"建议观察成交量和MACD等指标，若出现明显背离且放量反弹，可考虑轻仓参与。",
                price_level={
                    "支撑位": round(support_5ma, 2),
                    "观察位": round(open_price, 2)
                },
                risk_warning="跳水幅度较小，可能只是洗盘，不建议追涨杀跌"
            )

    @staticmethod
    def _suggest_surge_retrace(stock_data: Dict, ai_analysis: str) -> OperationSuggestion:
        """
        冲板回落操作建议

        判断依据：
        - 冲高幅度
        - 回落幅度
        - 是否守住均线
        - 封板量变化
        """

        stock_name = stock_data.get("股票名称")
        current_price = stock_data.get("实时价", 0)
        open_price = stock_data.get("开盘价", 0)
        high_price = stock_data.get("最高价", 0)

        surge = ((high_price - open_price) / open_price * 100) if open_price > 0 else 0
        retrace = ((high_price - current_price) / high_price * 100) if high_price > 0 else 0

        # 支撑位和压力位
        support_open = open_price * 1.01
        support_5ma = current_price * 0.99
        resistance = high_price

        # 根据回落幅度分级
        if surge >= 9 and retrace <= 3:
            # 冲高回落较少，强势
            return OperationSuggestion(
                action="回调买入或持有",
                confidence="中高",
                reasoning=f"{stock_name}冲高{surge:.2f}%后仅回落{retrace:.2f}%，显示多头力量较强。"
                          f"若回落至{support_open:.2f}元（开盘价附近）并企稳，是较好买点。"
                          f"已持有的建议继续持有，目标前高{high_price:.2f}元。",
                price_level={
                    "买点": round(support_open, 2),
                    "目标价": round(high_price, 2),
                    "止损位": round(support_5ma, 2)
                },
                risk_warning=f"注意观察是否二次上攻。回调买入仓位控制在30%以内，止损{support_5ma:.2f}元"
            )
        elif surge >= 9 and retrace > 3:
            # 冲高回落较多
            return OperationSuggestion(
                action="观望或等待企稳",
                confidence="中",
                reasoning=f"{stock_name}冲高{surge:.2f}%后回落{retrace:.2f}%，抛压较大。"
                          f"建议等待股价企稳并出现反弹信号再考虑介入。"
                          f"支撑位在{support_open:.2f}元，跌破则观望。",
                price_level={
                    "支撑位": round(support_open, 2),
                    "观察位": round(current_price * 0.98, 2)
                },
                risk_warning=f"冲板回落风险较大，不确定性强。建议观望或等待二次上攻确认"
            )
        else:
            # 冲高幅度不大
            return OperationSuggestion(
                action="谨慎参与",
                confidence="低",
                reasoning=f"{stock_name}冲高{surge:.2f}%后回落{retrace:.2f}%，上方压力明显。"
                          f"建议等待放量突破{resistance:.2f}元后再考虑追涨。",
                price_level={
                    "突破位": round(resistance * 1.01, 2),
                    "支撑位": round(support_5ma, 2)
                },
                risk_warning="冲高力度不足，回落风险存在，不建议追高"
            )

    @staticmethod
    def _suggest_breakdown(stock_data: Dict, ai_analysis: str) -> OperationSuggestion:
        """
        破位下跌操作建议

        判断依据：
        - 是否有效跌破（成交量、跌幅）
        - 是否有回抽确认
        - 跌破后的位置
        - 技术形态
        """

        stock_name = stock_data.get("股票名称")
        current_price = stock_data.get("实时价", 0)
        support_price = stock_data.get("前期平台支撑位", current_price * 0.97)

        # 支撑位和压力位
        next_support = support_price * 0.97
        resistance = current_price * 1.05

        # 根据破位后的位置分级
        decline_from_support = ((support_price - current_price) / support_price * 100)

        if decline_from_support >= 3:
            # 破位后持续下跌
            return OperationSuggestion(
                action="观望",
                confidence="高",
                reasoning=f"{stock_name}跌破支撑位{support_price:.2f}元后已下跌{decline_from_support:.2f}%，"
                          f"说明抛压沉重，未见企稳迹象。建议等待股价在{next_support:.2f}元附近企稳，"
                          f"或出现明显反弹信号后再考虑介入。",
                price_level={
                    "观察位": round(next_support, 2),
                    "止损位": round(current_price * 1.03, 2),
                    "支撑位": round(next_support, 2)
                },
                risk_warning=f"破位下跌趋势中，风险极高。严禁抄底，等待右侧信号。股价需站稳{next_support:.2f}元以上"
            )
        else:
            # 刚破位或破位后震荡
            return OperationSuggestion(
                action="谨慎观望",
                confidence="中",
                reasoning=f"{stock_name}跌破支撑位{support_price:.2f}元，需要观察是否有回抽确认。"
                          f"若回抽至{support_price:.2f}元附近受阻回落，确认破位有效，建议继续观望。"
                          f"若放量收回支撑位上方，可能是假破。",
                price_level={
                    "确认位": round(support_price * 1.02, 2),
                    "止损位": round(support_price * 0.98, 2),
                    "观察位": round(current_price, 2)
                },
                risk_warning="破位后走势不确定，建议等待确认。不排除假破可能，但安全第一"
            )


def format_suggestion(suggestion: OperationSuggestion) -> str:
    """格式化建议输出"""
    lines = [
        f"📊 操作建议: {suggestion.action} (置信度: {suggestion.confidence})",
        "",
        f"💡 建议理由:",
        f"   {suggestion.reasoning}",
        "",
        f"📍 关键价位:"
    ]

    if suggestion.price_level:
        for key, value in suggestion.price_level.items():
            lines.append(f"   • {key}: {value} 元")

    lines.append("")
    lines.append(f"⚠️  风险提示:")
    lines.append(f"   {suggestion.risk_warning}")

    return "\n".join(lines)


# 快速生成建议（供外部调用）
def get_quick_suggestion(pattern_type: str, stock_data: Dict) -> str:
    """快速获取操作建议（不包含AI分析）"""
    suggestion = OperationSuggestionGenerator.generate_suggestion(
        pattern_type, stock_data, ""
    )
    return format_suggestion(suggestion)
