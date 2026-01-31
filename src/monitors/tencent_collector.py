"""
腾讯财经数据采集器
备用真实数据源
"""

import requests
from typing import Dict, Any
from .data_collector import DataCollector


class TencentFinanceCollector(DataCollector):
    """
    腾讯财经数据采集器

    API说明：
    - 完全免费
    - 无需注册
    - 提供实时行情数据
    """

    def __init__(self):
        """初始化腾讯财经数据采集器"""
        self.base_url = "http://qt.gtimg.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://stockapp.finance.qq.com/',
            'Connection': 'keep-alive'
        })

    def get_stock_realtime_data(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票实时数据

        Args:
            stock_code: 股票代码（如 sh600000 或 sz000001）
        """
        try:
            # 处理股票代码格式
            if stock_code.startswith("6") or stock_code.startswith("5"):
                # 6开头是上交所股票，5开头是上交所ETF基金
                symbol = f"sh{stock_code}"
            elif stock_code.startswith("0") or stock_code.startswith("3") or stock_code.startswith("1"):
                # 0/3开头是深交所股票，1开头是深交所ETF基金
                symbol = f"sz{stock_code}"
            elif stock_code.startswith("4") or stock_code.startswith("8"):
                # 4/8开头是北交所股票
                symbol = f"bj{stock_code}"
            else:
                symbol = stock_code

            # 调用腾讯API
            url = f"{self.base_url}/q={symbol}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'

            if response.status_code != 200:
                print(f"API调用失败: {response.status_code}")
                return {}

            # 解析响应数据
            data_str = response.text
            if not data_str or '"' not in data_str or '~' not in data_str:
                print(f"无效的响应数据: {data_str[:100]}")
                return {}

            # 提取数据部分
            data_part = data_str.split('"')[1]
            fields = data_part.split('~')

            if len(fields) < 30:
                print(f"数据字段不足: {len(fields)}")
                return {}

            # 解析字段（腾讯API字段索引）
            stock_name = fields[1]
            open_price = float(fields[5]) if fields[5] else 0
            close_prev = float(fields[4]) if fields[4] else 0
            current_price = float(fields[3]) if fields[3] else 0
            high_price = float(fields[33]) if fields[33] else 0
            low_price = float(fields[34]) if fields[34] else 0
            volume = int(fields[36]) if fields[36] else 0

            # 计算涨停价
            limit_up = round(close_prev * 1.1, 2) if close_prev > 0 else 0

            return {
                "股票代码": stock_code,
                "股票名称": stock_name,
                "开盘价": open_price,
                "实时价": current_price,
                "最高价": high_price,
                "最低价": low_price,
                "涨停价": limit_up,
                "昨收": close_prev,
                "成交量": volume,
                "成交额": 0,
                "板块名称": "未知",
                "最新消息": "无"
            }

        except Exception as e:
            print(f"获取股票{stock_code}数据失败: {e}")
            return {}

    def get_sector_data(self, sector_name: str) -> Dict[str, Any]:
        """获取板块数据"""
        return {"涨跌幅": 0}

    def get_market_index_data(self, index_name: str = "上证指数") -> Dict[str, Any]:
        """获取大盘指数数据"""
        try:
            if "上证" in index_name:
                symbol = "sh000001"
            elif "深证" in index_name:
                symbol = "sz399001"
            else:
                symbol = "sh000001"

            url = f"{self.base_url}/q={symbol}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'

            if response.status_code != 200:
                return {"涨跌幅": 0}

            data_str = response.text
            if '"' not in data_str or '~' not in data_str:
                return {"涨跌幅": 0}

            data_part = data_str.split('"')[1]
            fields = data_part.split('~')

            if len(fields) < 4:
                return {"涨跌幅": 0}

            current_price = float(fields[3]) if fields[3] else 0
            prev_price = float(fields[4]) if fields[4] else 0
            change_percent = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0

            return {"涨跌幅": round(change_percent, 2)}

        except Exception as e:
            return {"涨跌幅": 0}


class UnifiedRealDataCollector(DataCollector):
    """
    统一真实数据采集器
    自动尝试多个数据源，提高数据获取成功率
    """

    def __init__(self):
        """初始化统一数据采集器"""
        self.collectors = [
            TencentFinanceCollector(),  # 优先使用腾讯
            # SinaFinanceCollector(),  # 新浪API可能被限流
        ]
        self.current_collector = None

    def _try_collectors(self, stock_code: str, method_name: str, *args, **kwargs):
        """尝试所有采集器，直到成功"""
        for collector in self.collectors:
            try:
                result = getattr(collector, method_name)(*args, **kwargs)
                if result and (result.get("股票名称") or result.get("涨跌幅", 0) != 0 or len(result) > 2):
                    self.current_collector = collector
                    return result
            except Exception as e:
                continue

        return {}

    def get_stock_realtime_data(self, stock_code: str) -> Dict[str, Any]:
        """获取股票实时数据"""
        result = self._try_collectors(stock_code, "get_stock_realtime_data", stock_code)
        if not result or not result.get("股票名称"):
            print(f"⚠️  所有真实数据源均失败，将使用Mock数据作为备用")
        return result

    def get_sector_data(self, sector_name: str) -> Dict[str, Any]:
        """获取板块数据"""
        return self._try_collectors(sector_name, "get_sector_data", sector_name) or {"涨跌幅": 0}

    def get_market_index_data(self, index_name: str = "上证指数") -> Dict[str, Any]:
        """获取大盘指数数据"""
        return self._try_collectors(index_name, "get_market_index_data", index_name) or {"涨跌幅": 0}


# 测试函数
def test_tencent_collector():
    """测试腾讯财经数据采集器"""
    print("\n" + "="*70)
    print("测试真实数据采集器 - 腾讯财经API")
    print("="*70)

    collector = TencentFinanceCollector()

    print("\n正在获取601138（工业富联）的实时数据...")
    print("-"*70)

    data = collector.get_stock_realtime_data("601138")

    if data and data.get("股票名称"):
        print(f"股票名称: {data.get('股票名称')}")
        print(f"股票代码: {data.get('股票代码')}")
        print(f"开盘价: {data.get('开盘价')}")
        print(f"实时价: {data.get('实时价')}")
        print(f"最高价: {data.get('最高价')}")
        print(f"涨停价: {data.get('涨停价')}")
        print("-"*70)
        print("✅ 数据获取成功！")
        return data
    else:
        print("❌ 数据获取失败")
        return None


def test_unified_collector():
    """测试统一数据采集器"""
    print("\n" + "="*70)
    print("测试统一真实数据采集器")
    print("="*70)

    collector = UnifiedRealDataCollector()

    print("\n正在获取601138（工业富联）的实时数据...")
    print("-"*70)

    data = collector.get_stock_realtime_data("601138")

    if data and data.get("股票名称"):
        print(f"股票名称: {data.get('股票名称')}")
        print(f"股票代码: {data.get('股票代码')}")
        print(f"开盘价: {data.get('开盘价')}")
        print(f"实时价: {data.get('实时价')}")
        print(f"最高价: {data.get('最高价')}")
        print(f"涨停价: {data.get('涨停价')}")
        print("-"*70)
        print("✅ 数据获取成功！")
        return data
    else:
        print("❌ 数据获取失败")
        return None


if __name__ == "__main__":
    test_tencent_collector()
    print("\n")
    test_unified_collector()
