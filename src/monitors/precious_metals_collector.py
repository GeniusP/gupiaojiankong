#!/usr/bin/env python3
"""
贵金属价格收集器
获取黄金、白银的实时价格（美元和人民币）
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class PreciousMetalsCollector:
    """贵金属价格收集器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_metals_prices(self) -> Optional[Dict]:
        """
        获取贵金属实时价格（黄金、白银、铂金、钯金）

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
            # 使用腾讯财经API获取贵金属价格
            # 黄金现货: HF_XAU
            # 白银现货: HF_XAG
            # 铂金现货: HF_XPT
            # 钯金现货: HF_XPD

            urls = {
                'gold': "https://qt.gtimg.cn/q=hf_XAU",
                'silver': "https://qt.gtimg.cn/q=hf_XAG",
                'platinum': "https://qt.gtimg.cn/q=hf_XPT",
                'palladium': "https://qt.gtimg.cn/q=hf_XPD"
            }

            prices_usd = {}

            # 获取各种金属的美元价格
            for metal, url in urls.items():
                try:
                    response = self.session.get(url, timeout=5)
                    data = response.text
                    if '"' in data:
                        content = data.split('"')[1]
                        parts = content.split(',')
                        prices_usd[metal] = float(parts[0]) if parts[0] else None
                except Exception as e:
                    print(f"获取{metal}价格失败: {e}")
                    prices_usd[metal] = None

            # 汇率换算（1美元兑人民币）
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
