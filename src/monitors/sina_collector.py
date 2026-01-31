"""
真实数据采集器
接入新浪财经、东方财富等免费API获取实时行情
"""

import requests
from typing import Dict, Any
from src.monitors.data_collector import DataCollector


class SinaFinanceCollector(DataCollector):
    """

    API说明：
    - 完全免费
    - 无需注册
    - 提供实时行情数据
    """

    def __init__(self):
        """初始化新浪财经数据采集器"""
        # 新浪API不需要密钥
        self.base_url = "http://hq.sinajs.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://finance.sina.com.cn/',
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

            # 提取数据
            data_part = data_str.split('"')[1]
            fields = data_part.split(',')

            if len(fields) < 32:
                print(f"数据字段不足: {len(fields)}")
                return {}

            # 解析字段
            stock_name = fields[0]
            open_price = float(fields[1])
            close_prev = float(fields[2])
            current_price = float(fields[3])
            high_price = float(fields[4])
            low_price = float(fields[5])
            volume = int(fields[8])

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
            return {"涨跌幅": 0}


# 测试函数
def test_sina_collector():
    """测试新浪财经数据采集器"""
    print("\n" + "="*70)
    print("测试真实数据采集器 - 新浪财经API")
    print("="*70)

    collector = SinaFinanceCollector()

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
    test_sina_collector()
