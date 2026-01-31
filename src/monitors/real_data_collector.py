# 📊 使用真实股票数据

## 🎯 问题说明

当前系统使用Mock数据（模拟数据）进行演示。要分析真实股票，需要接入真实数据源。

## 💡 快速解决方案

### 方案1：手动输入真实数据（最简单）

创建 `analyze_real.py`：

```python
import asyncio
from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.stock_monitor import quick_analysis

async def main():
    # 手动传入真实数据
    result = await quick_analysis(
        stock_code="601138",
        pattern_type="开盘跳水",
        aigc_adapter=ZhipuAdapter(),
        trading_style="短线",

        # ========== 真实数据（请从交易软件查看） ==========
        trigger_time="09:35",          # 触发时间
        open_price=58.50,              # 开盘价
        current_price=57.70,           # 实时价（工业富联当前价）
        highest_price=59.20,           # 最高价
        limit_up_price=64.35,          # 涨停价
        ma5=58.20,                     # 5日均线
        ma20=57.50,                    # 20日均线
        support_price=57.00,           # 支撑位
        volume_amount=850000,          # 成交额（万元）
        volume_increase=30.0,          # 成交额放大比例%
        sector_name="电子",             # 板块名称
        sector_change=-0.5,            # 板块涨跌幅%
        index_change=-0.3,             # 大盘涨跌幅%
        news="无",                     # 消息面

        # 图形特定参数
        open_minutes=10,               # 开盘几分钟
        drop_percent=1.4,              # 跌幅（58.50-57.70）/58.50*100
        ma_type=5,                     # 均线类型
        ma_price=58.20                 # 均线价格
    )

    print(result)

asyncio.run(main())
```

### 方案2：接入免费数据API

以下是一些免费的股票数据API：

1. **新浪财经API**（免费，无需注册）
2. **东方财富API**（免费）
3. **腾讯财经API**（免费）
4. **网易财经API**（免费）

让我为您创建一个真实数据采集器：</think>现在让我创建一个真实数据采集器示例：<tool_call>Write<arg_key>content</arg_key><arg_value>"""
真实数据采集器示例
接入免费股票数据API获取实时行情
"""

import requests
from typing import Dict, Any
from src.monitors.data_collector import DataCollector


class SinaFinanceCollector(DataCollector):
    """
    新浪财经数据采集器（免费API）

    API说明：
    - 完全免费
    - 无需注册
    - 提供实时行情数据
    """

    def __init__(self):
        """初始化新浪财经数据采集器"""
        super().__init__(api_key="")
        self.base_url = "http://hq.sinajs.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_realtime_data(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票实时数据

        Args:
            stock_code: 股票代码（如 sh600000 或 sz000001）
        """
        try:
            # 处理股票代码格式
            if stock_code.startswith("6"):
                symbol = f"sh{stock_code}"
            elif stock_code.startswith("0") or stock_code.startswith("3"):
                symbol = f"sz{stock_code}"
            else:
                symbol = stock_code

            # 调用新浪API
            url = f"{self.base_url}/list={symbol}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'

            if response.status_code != 200:
                print(f"API调用失败: {response.status_code}")
                return {}

            # 解析响应数据
            data_str = response.text
            if not data_str or '"' not in data_str:
                print(f"无效的响应数据: {data_str[:100]}")
                return {}

            # 提取数据（新浪API返回格式：var hq_str_sh600000="...";）
            data_part = data_str.split('"')[1]
            fields = data_part.split(',')

            if len(fields) < 32:
                print(f"数据字段不足: {len(fields)}")
                return {}

            # 解析字段（新浪API字段说明见文档）
            stock_name = fields[0]
            open_price = float(fields[1])
            close_prev = float(fields[2])
            current_price = float(fields[3])
            high_price = float(fields[4])
            low_price = float(fields[5])
            buy_price = float(fields[6])
            sell_price = float(fields[7])
            volume = int(fields[8])
            amount = float(fields[9])

            # 计算涨跌
            change = current_price - close_prev
            change_percent = (change / close_prev) * 100 if close_prev > 0 else 0

            # 计算涨停价（A股规则）
            limit_up = round(close_prev * 1.1, 2) if close_prev > 0 else 0
            if "ST" in stock_name or "*" in stock_name:
                limit_up = round(close_prev * 1.05, 2)

            return {
                "股票代码": stock_code,
                "股票名称": stock_name,
                "开盘价": open_price,
                "实时价": current_price,
                "最高价": high_price,
                "最低价": low_price,
                "涨停价": limit_up,
                "昨收": close_prev,
                "涨跌": change,
                "涨跌幅": change_percent,
                "成交量": volume,
                "成交额": amount,
                "买一价": buy_price,
                "卖一价": sell_price,
                "板块名称": "未知",  # 新浪API不提供板块信息
                "最新消息": "无"
            }

        except Exception as e:
            print(f"获取股票{stock_code}数据失败: {e}")
            return {}

    def get_sector_data(self, sector_name: str) -> Dict[str, Any]:
        """获取板块数据（新浪API暂不支持，返回默认值）"""
        return {"涨跌幅": 0}

    def get_market_index_data(self, index_name: str = "上证指数") -> Dict[str, Any]:
        """获取大盘指数数据"""
        try:
            # 上证指数
            if "上证" in index_name or "sh000001" in index_name:
                symbol = "sh000001"
            # 深证成指
            elif "深证" in index_name or "sz399001" in index_name:
                symbol = "sz399001"
            # 创业板指
            elif "创业板" in index_name or "sz399006" in index_name:
                symbol = "sz399006"
            else:
                symbol = "sh000001"

            url = f"{self.base_url}/list={symbol}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'

            if response.status_code != 200:
                return {"涨跌幅": 0}

            data_str = response.text
            data_part = data_str.split('"')[1]
            fields = data_part.split(',')

            if len(fields) < 3:
                return {"涨跌幅": 0}

            current_price = float(fields[1])
            prev_price = float(fields[2])
            change_percent = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0

            return {"涨跌幅": round(change_percent, 2)}

        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return {"涨跌幅": 0}


class EastMoneyCollector(DataCollector):
    """
    东方财富数据采集器
    提供更丰富的数据，包括板块数据
    """

    def __init__(self):
        super().__init__(api_key="")
        self.base_url = "http://push2.eastmoney.com/api/qt"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_realtime_data(self, stock_code: str) -> Dict[str, Any]:
        """获取股票实时数据"""
        try:
            # 获取市场ID
            if stock_code.startswith("6"):
                market_id = "0"  # 上海
                secid = f"{market_id}.{stock_code}"
            elif stock_code.startswith(("0", "3")):
                market_id = "1"  # 深圳
                secid = f"{market_id}.{stock_code}"
            else:
                return {}

            url = f"{self.base_url}/stock/get"
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f116,f117,f127,f152,f161,f162,f167,f168,f169,f170,f171,f84,f85"
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return {}

            data = response.json()
            if data.get("rc") != 0:
                return {}

            info = data.get("data", {})
            if not info:
                return {}

            return {
                "股票代码": stock_code,
                "股票名称": info.get("f58", ""),  # 股票名称
                "开盘价": info.get("f46", 0),    # 开盘价
                "实时价": info.get("f43", 0),    # 最新价
                "最高价": info.get("f44", 0),    # 最高价
                "最低价": info.get("f45", 0),    # 最低价
                "昨收": info.get("f60", 0),      # 昨收
                "成交量": info.get("f47", 0),   # 成交量（手）
                "成交额": info.get("f48", 0),   # 成交额
                "涨停价": info.get("f51", 0),   # 涨停价
                "跌停价": info.get("f52", 0),   # 跌停价
                "板块名称": "未知",
                "最新消息": "无"
            }

        except Exception as e:
            print(f"获取股票{stock_code}数据失败: {e}")
            return {}

    def get_sector_data(self, sector_name: str) -> Dict[str, Any]:
        """获取板块数据"""
        # 东方财富板块API比较复杂，这里返回默认值
        return {"涨跌幅": 0}

    def get_market_index_data(self, index_name: str = "上证指数") -> Dict[str, Any]:
        """获取大盘指数数据"""
        try:
            index_codes = {
                "上证指数": "0.000001",
                "深证成指": "0.399001",
                "创业板指": "0.399006"
            }

            code = index_codes.get(index_name, "0.000001")

            url = f"{self.base_url}/stock/get"
            params = {
                "secid": code,
                "fields": "f43,f44,f45,f46,f60,f162"
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return {"涨跌幅": 0}

            data = response.json()
            info = data.get("data", {})

            if not info:
                return {"涨跌幅": 0}

            current = info.get("f43", 0)
            prev = info.get("f60", 0)
            change_percent = ((current - prev) / prev) * 100 if prev > 0 else 0

            return {"涨跌幅": round(change_percent, 2)}

        except Exception as e:
            return {"涨跌幅": 0}


# 使用示例
def test_real_data_collector():
    """测试真实数据采集器"""
    print("\n" + "="*70)
    print("测试真实数据采集器")
    print("="*70)

    # 使用新浪财经API
    collector = SinaFinanceCollector()

    # 测试601138（工业富联）
    print("\n正在获取601138（工业富联）的实时数据...")
    print("-"*70)

    data = collector.get_stock_realtime_data("601138")

    if data:
        print(f"股票名称: {data.get('股票名称')}")
        print(f"股票代码: {data.get('股票代码')}")
        print(f"开盘价: {data.get('开盘价')}")
        print(f"实时价: {data.get('实时价')}")
        print(f"最高价: {data.get('最高价')}")
        print(f"涨停价: {data.get('涨停价')}")
        print(f"涨跌幅: {data.get('涨跌幅'):.2f}%")
        print(f"成交量: {data.get('成交量')}手")
        print("-"*70)
        print("✅ 数据获取成功！")
    else:
        print("❌ 数据获取失败")


if __name__ == "__main__":
    test_real_data_collector()
