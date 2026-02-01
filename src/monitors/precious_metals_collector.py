#!/usr/bin/env python3
"""
贵金属价格收集器
获取黄金、白银的实时价格（美元和人民币）
使用 iTick API: https://docs.itick.org/
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class PreciousMetalsCollector:
    """贵金属价格收集器 - 使用 iTick API"""

    # iTick API 配置
    API_BASE_URL = "https://api.itick.org"
   

    # 贵金属代码映射
    METALS_CODES = {
        'gold': 'XAUUSD',      # 黄金
        'silver': 'XAGUSD',    # 白银
        'platinum': 'XPTUSD',  # 铂金
        'palladium': 'XPDUSD'  # 钯金
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'token': self.API_TOKEN,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_metals_prices(self) -> Optional[Dict]:
        """
        使用 iTick API 获取贵金属实时价格（黄金、白银、铂金、钯金）

        Returns:
            {
                'gold_usd': 黄金美元价格(美元/盎司),
                'gold_cny': 黄金人民币价格(元/克),
                'silver_usd': 白银美元价格(美元/盎司),
                'silver_cny': 白银人民币价格(元/克),
                'platinum_usd': 铂金美元价格(美元/盎司),
                'platinum_cny': 铂金人民币价格(元/克),
                'palladium_usd': 钯金美元价格(美元/盎司),
                'palladium_cny': 钯金人民币价格(元/克),
                'update_time': 更新时间
            }
        """
        try:
            prices_usd = {}

            # 使用 iTick API 获取各种贵金属的实时报价
            for metal_name, metal_code in self.METALS_CODES.items():
                try:
                    url = f"{self.API_BASE_URL}/forex/tick"
                    params = {'region': 'gb', 'code': metal_code}

                    response = self.session.get(url, params=params, timeout=10)

                    if response.status_code == 200:
                        data = response.json()

                        # iTick API 返回格式: {"code": 0, "data": {"s": "XAUUSD", "ld": 2730.55, "t": 1234567890}}
                        if data and data.get('code') == 0 and 'data' in data:
                            # ld 字段是最新价格 (last deal price)
                            price = float(data['data'].get('ld', 0))
                            prices_usd[metal_name] = price if price > 0 else None
                        else:
                            print(f"获取{metal_name}价格: API返回数据格式异常")
                            prices_usd[metal_name] = None
                    else:
                        print(f"获取{metal_name}价格失败: HTTP {response.status_code}")
                        prices_usd[metal_name] = None

                except Exception as e:
                    print(f"获取{metal_name}价格失败: {e}")
                    prices_usd[metal_name] = None

            # 汇率换算（1美元兑人民币，可后续通过API获取实时汇率）
            usd_to_cny = 7.24

            # 换算人民币价格（1盎司 = 31.1035克）
            result = {
                'gold_usd': round(prices_usd.get('gold'), 2) if prices_usd.get('gold') else None,
                'gold_cny': round(prices_usd.get('gold') * usd_to_cny / 31.1035, 2) if prices_usd.get('gold') else None,
                'silver_usd': round(prices_usd.get('silver'), 2) if prices_usd.get('silver') else None,
                'silver_cny': round(prices_usd.get('silver') * usd_to_cny / 31.1035, 2) if prices_usd.get('silver') else None,
                'platinum_usd': round(prices_usd.get('platinum'), 2) if prices_usd.get('platinum') else None,
                'platinum_cny': round(prices_usd.get('platinum') * usd_to_cny / 31.1035, 2) if prices_usd.get('platinum') else None,
                'palladium_usd': round(prices_usd.get('palladium'), 2) if prices_usd.get('palladium') else None,
                'palladium_cny': round(prices_usd.get('palladium') * usd_to_cny / 31.1035, 2) if prices_usd.get('palladium') else None,
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return result

        except Exception as e:
            print(f"获取贵金属价格失败: {e}")
            return None

    def get_alternative_prices(self) -> Optional[Dict]:
        """
        使用备用方法获取贵金属价格
        从英为财情或其他数据源
        """
        try:
            # 使用腾讯财经API
            urls = {
                'gold_usd': 'https://qt.gtimg.cn/q=hf_XAU',
                'silver_usd': 'https://qt.gtimg.cn/q=hf_XAG',
            }

            result = {}

            for key, url in urls.items():
                try:
                    response = self.session.get(url, timeout=5)
                    data = response.text
                    if '~' in data:
                        price = data.split('~')[1]
                        result[key] = round(float(price), 2) if price else None
                except:
                    result[key] = None

            # 汇率换算
            usd_to_cny = 7.2

            if result.get('gold_usd'):
                result['gold_cny'] = round(result['gold_usd'] * usd_to_cny / 31.1035, 2)

            if result.get('silver_usd'):
                result['silver_cny'] = round(result['silver_usd'] * usd_to_cny / 31.1035 * 1000, 2)

            result['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return result if any(result.values()) else None

        except Exception as e:
            print(f"获取备用贵金属价格失败: {e}")
            return None

    def get_metal_kline(self, metal_type: str, days: int = 60) -> Optional[list]:
        """
        使用 iTick API 获取贵金属K线数据

        Args:
            metal_type: 贵金属类型 (gold/silver/platinum/palladium)
            days: 获取天数

        Returns:
            [[日期, 开盘, 最高, 最低, 收盘], ...]
        """
        try:
            # 获取贵金属代码
            metal_code = self.METALS_CODES.get(metal_type)
            if not metal_code:
                print(f"不支持的贵金属类型: {metal_type}")
                return None

            print(f"正在从 iTick API 获取 {metal_type} 的K线数据...")

            # iTick API K线接口
            # kType: 1=1分钟, 8=日K线, 7=1小时
            url = f"{self.API_BASE_URL}/forex/kline"
            params = {
                'region': 'gb',
                'code': metal_code,
                'kType': '8',  # 日K线
                'limit': days
            }

            try:
                response = self.session.get(url, params=params, timeout=15)

                if response.status_code != 200:
                    print(f"iTick API 请求失败: HTTP {response.status_code}")
                    return None

                # 解析JSON响应
                result = response.json()

                if not result or 'data' not in result:
                    print(f"iTick API 返回错误: {result}")
                    return None

                # 提取K线数据
                kline_list = result['data']

                if not kline_list:
                    print("iTick API 返回数据为空")
                    return None

                # 转换数据格式
                kline_data = []
                usd_to_cny = 7.24
                ounce_to_gram = 31.1035

                from datetime import datetime as dt

                for bar in kline_list:
                    try:
                        # iTick 返回格式: {"tu": ..., "c": 收盘, "t": 时间戳, "v": 成交量, "h": 最高, "l": 最低, "o": 开盘}
                        timestamp = bar.get('t', 0)
                        open_price = float(bar.get('o', 0))
                        high_price = float(bar.get('h', 0))
                        low_price = float(bar.get('l', 0))
                        close_price = float(bar.get('c', 0))

                        # 转换时间戳为日期字符串
                        date_str = dt.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')

                        # 转换为人民币/克
                        open_cny = open_price * usd_to_cny / ounce_to_gram
                        high_cny = high_price * usd_to_cny / ounce_to_gram
                        low_cny = low_price * usd_to_cny / ounce_to_gram
                        close_cny = close_price * usd_to_cny / ounce_to_gram

                        kline_data.append([
                            date_str,
                            round(open_cny, 2),
                            round(high_cny, 2),
                            round(low_cny, 2),
                            round(close_cny, 2)
                        ])

                    except Exception as e:
                        print(f"解析K线数据项失败: {e}")
                        continue

                if kline_data:
                    # 按日期排序（从早到晚）
                    kline_data.sort(key=lambda x: x[0])
                    print(f"✓ 成功从 iTick API 获取 {metal_type} 的 {len(kline_data)} 天K线数据")
                    return kline_data
                else:
                    print("未能解析出任何K线数据")
                    return None

            except Exception as e:
                print(f"从 iTick API 获取数据失败: {e}")
                import traceback
                traceback.print_exc()
                return None

        except Exception as e:
            print(f"获取贵金属K线数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    # 测试
    collector = PreciousMetalsCollector()
    prices = collector.get_metals_prices()

    if prices:
        print("\n" + "="*60)
        print("🥇 贵金属实时价格")
        print("="*60)
        print(f"💰 黄金价格:")
        print(f"   国际: ${prices['gold_usd']}/盎司" if prices['gold_usd'] else "   国际: 暂无数据")
        print(f"   国内: ¥{prices['gold_cny']}/克" if prices['gold_cny'] else "   国内: 暂无数据")

        print(f"\n💎 白银价格:")
        print(f"   国际: ${prices['silver_usd']}/盎司" if prices['silver_usd'] else "   国际: 暂无数据")
        print(f"   国内: ¥{prices['silver_cny']}/克" if prices['silver_cny'] else "   国内: 暂无数据")

        print(f"\n⏰ 更新时间: {prices['update_time']}")
        print("="*60)
    else:
        print("❌ 获取失败")
