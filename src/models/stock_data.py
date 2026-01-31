"""
股票数据模型定义
使用Pydantic进行数据验证和序列化
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class StockMarketData(BaseModel):
    """股票行情数据模型"""

    # 基础信息
    股票代码: str = Field(..., description="股票代码，如600000")
    股票名称: str = Field(..., description="股票名称，如浦发银行")
    触发时间: str = Field(..., description="触发时间，格式HH:MM，如09:35")
    图形类型: str = Field(..., description="图形类型：开盘跳水/破位下跌/冲板回落")

    # 行情数据
    开盘价: Optional[float] = Field(None, description="开盘价")
    实时价: Optional[float] = Field(None, description="当前实时价")
    最高价: Optional[float] = Field(None, description="当日最高价")
    涨停价: Optional[float] = Field(None, description="涨停价")
    ma5: Optional[float] = Field(None, description="5日均线价格", alias="5日均线")
    ma20: Optional[float] = Field(None, description="20日均线价格", alias="20日均线")
    前期平台支撑位: Optional[float] = Field(None, description="前期平台支撑位价格")

    # 成交量数据
    触发成交额: Optional[float] = Field(None, description="触发时刻的成交额（万元）")
    成交额放大比例: Optional[float] = Field(None, description="较前5日均值的放大比例（%）")
    当日成交额放大比例: Optional[float] = Field(None, description="较当日均值的放大比例（%）")
    分钟成交额放大比例: Optional[float] = Field(None, description="较前1分钟的放大比例（%）")

    # 市场环境
    板块名称: Optional[str] = Field(None, description="所属板块名称")
    板块涨跌幅: Optional[float] = Field(None, description="板块当日涨跌幅（%）")
    大盘名称: Optional[str] = Field("上证指数", description="大盘指数名称")
    大盘涨跌幅: Optional[float] = Field(None, description="大盘当日涨跌幅（%）")

    # 消息面
    最新消息: Optional[str] = Field("无", description="最新公告或利好利空消息")

    # 额外特征（根据不同图形类型会有不同字段）
    额外特征: Optional[str] = Field("", description="图形专属特征")

    # 开盘跳水专属
    开盘分钟数: Optional[int] = Field(None, description="开盘后几分钟触发")
    跌幅: Optional[float] = Field(None, description="跌幅百分比")
    均线类型: Optional[int] = Field(None, description="跌破的均线类型（5/20）")
    均线价格: Optional[float] = Field(None, description="跌破的均线价格")

    # 破位下跌专属
    支撑位价格: Optional[float] = Field(None, description="跌破的支撑位价格")
    破位后未回弹分钟数: Optional[int] = Field(None, description="破位后几分钟未回弹")

    # 冲板回落专属
    涨幅: Optional[float] = Field(None, description="冲板时的涨幅百分比")
    回落幅度: Optional[float] = Field(None, description="回落幅度百分比")
    封板挂单量: Optional[int] = Field(None, description="封板时的买一挂单量（手）")

    @validator('触发时间')
    def validate_time_format(cls, v):
        """验证时间格式"""
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError('触发时间格式错误，应为HH:MM，如09:35')
        return v

    @validator('图形类型')
    def validate_chart_type(cls, v):
        """验证图形类型"""
        valid_types = ['开盘跳水', '破位下跌', '冲板回落']
        if v not in valid_types:
            raise ValueError(f'图形类型错误，应为：{"/".join(valid_types)}')
        return v

    def to_dict(self) -> dict:
        """转换为字典格式，用于模板替换"""
        return self.dict()

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "股票代码": "600000",
                "股票名称": "浦发银行",
                "触发时间": "09:35",
                "图形类型": "开盘跳水",
                "开盘价": 10.5,
                "实时价": 10.2,
                "最高价": 10.5,
                "涨停价": 11.55,
                "5日均线": 10.3,
                "20日均线": 10.15,
                "前期平台支撑位": 10.0,
                "触发成交额": 12500,
                "成交额放大比例": 35.5,
                "当日成交额放大比例": 20.3,
                "分钟成交额放大比例": 50.0,
                "板块名称": "银行",
                "板块涨跌幅": -1.2,
                "大盘名称": "上证指数",
                "大盘涨跌幅": -0.8,
                "最新消息": "无",
                "额外特征": "开盘5分钟跌超3%，跌破5日均线",
                "开盘分钟数": 5,
                "跌幅": 3.2,
                "均线类型": 5,
                "均线价格": 10.3
            }
        }


class AIGCResponse(BaseModel):
    """AIGC模型响应数据模型"""

    判断结果: Optional[str] = Field(None, description="判断结果（真/假）")
    判断依据: Optional[str] = Field(None, description="判断依据")
    破位判断: Optional[str] = Field(None, description="破位判断（真破位/假破位）")
    核心原因: Optional[str] = Field(None, description="核心原因")
    风险等级: Optional[str] = Field(None, description="风险等级（高/中/低）")
    风险理由: Optional[str] = Field(None, description="风险理由")
    短期预判: Optional[str] = Field(None, description="短期走势预判")
    走势影响: Optional[str] = Field(None, description="走势影响（偏空/中性/偏多）")
    操作建议: Optional[str] = Field(None, description="操作建议")
    参考价位: Optional[float] = Field(None, description="关键参考价位")
    抛压强度: Optional[str] = Field(None, description="抛压强度（强/中/弱）")
    原始回复: str = Field(..., description="AIGC模型的原始回复")

    def to_display_format(self) -> str:
        """格式化输出用于显示"""
        lines = []
        if self.判断结果:
            lines.append(f"判断结果: {self.判断结果}")
        if self.判断依据:
            lines.append(f"判断依据: {self.判断依据}")
        if self.破位判断:
            lines.append(f"破位判断: {self.破位判断}")
        if self.核心原因:
            lines.append(f"核心原因: {self.核心原因}")
        if self.风险等级:
            reason = f"（理由：{self.风险理由}）" if self.风险理由 else ""
            lines.append(f"风险等级: {self.风险等级}{reason}")
        if self.短期预判:
            lines.append(f"短期预判: {self.短期预判}")
        if self.走势影响:
            reason = f"（理由：{self.判断依据}）" if self.判断依据 else ""
            lines.append(f"走势影响: {self.走势影响}{reason}")
        if self.操作建议:
            if self.参考价位:
                lines.append(f"操作建议: {self.操作建议}（参考价位: {self.参考价位}）")
            else:
                lines.append(f"操作建议: {self.操作建议}")
        if self.抛压强度:
            lines.append(f"抛压强度: {self.抛压强度}")

        return "\n".join(lines) if lines else self.原始回复


class MonitorTrigger(BaseModel):
    """监控触发事件模型"""

    事件ID: str = Field(..., description="唯一事件ID")
    股票代码: str = Field(..., description="股票代码")
    股票名称: str = Field(..., description="股票名称")
    图形类型: str = Field(..., description="图形类型")
    触发时间: datetime = Field(default_factory=datetime.now, description="触发时间")
    市场数据: StockMarketData = Field(..., description="市场数据")
    已处理: bool = Field(False, description="是否已处理")
    AIGC分析结果: Optional[AIGCResponse] = Field(None, description="AIGC分析结果")

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "事件ID": "evt_20250127_093500_600000",
                "股票代码": "600000",
                "股票名称": "浦发银行",
                "图形类型": "开盘跳水",
                "已处理": False
            }
        }
