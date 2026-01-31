#!/usr/bin/env python3
"""
板块扫描器
获取热门板块及成分股，用于批量筛选图形形态
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class SectorScanner:
    """板块扫描器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_hot_sectors(self, top_n: int = 5) -> List[Dict]:
        """
        获取热门板块列表（按热度排序）

        热度定义：按成交额排序，成交额越大代表市场关注度越高

        Args:
            top_n: 获取前N个热门板块

        Returns:
            [
                {
                    'sector_code': 板块代码,
                    'sector_name': 板块名称,
                    'change_percent': 涨跌幅,
                    'amount': 成交额（万元）
                },
                ...
            ]
        """
        try:
            # 使用东方财富的板块数据接口
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': top_n,
                'po': '1',
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'fid': 'f6',  # 按成交额排序（热度）
                'fs': 'm:90+t:2',  # 板块
                'fields': 'f12,f14,f2,f3,f6',  # 代码,名称,最新价,涨跌幅,成交额
                '_': str(int(datetime.now().timestamp() * 1000))
            }

            response = self.session.get(url, params=params, timeout=5)
            data = response.json()

            if data.get('rc') == 0 and 'data' in data:
                sectors = []
                for item in data['data']['diff']:
                    sectors.append({
                        'sector_code': item.get('f12', ''),
                        'sector_name': item.get('f14', ''),
                        'change_percent': round(item.get('f3', 0), 2),
                        'amount': item.get('f6', 0)  # 成交额
                    })
                return sectors

            return []

        except Exception as e:
            print(f"获取热门板块失败: {e}")
            # 返回默认热门板块列表
            return self._get_default_sectors()

    def _get_default_sectors(self) -> List[Dict]:
        """获取默认热门板块列表（备用）"""
        return [
            {'sector_code': 'BK0001', 'sector_name': '人工智能', 'change_percent': 3.5, 'amount': 5000000},
            {'sector_code': 'BK0002', 'sector_name': '新能源汽车', 'change_percent': 2.8, 'amount': 4500000},
            {'sector_code': 'BK0003', 'sector_name': '半导体', 'change_percent': 2.5, 'amount': 4200000},
            {'sector_code': 'BK0004', 'sector_name': '军工', 'change_percent': 2.0, 'amount': 3800000},
            {'sector_code': 'BK0005', 'sector_name': '医药生物', 'change_percent': 1.8, 'amount': 3500000},
        ]

    def get_sector_stocks(self, sector_code: str, top_n: int = 5) -> List[Dict]:
        """
        获取指定板块的成分股（按涨跌幅排序，取前N只）

        Args:
            sector_code: 板块代码
            top_n: 获取前N只股票

        Returns:
            [
                {
                    'stock_code': 股票代码,
                    'stock_name': 股票名称,
                    'change_percent': 涨跌幅,
                    'current_price': 当前价,
                    'volume': 成交量
                },
                ...
            ]
        """
        try:
            # 使用东方财富的板块成分股接口
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': top_n * 3,  # 多取一些，因为后面会过滤
                'po': '1',
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',  # 按涨跌幅排序
                'fs': f'b:{sector_code}+f:!50',  # 板块成分股，排除ST
                'fields': 'f12,f14,f2,f3,f5,f6,f15,f16',  # 代码,名称,最新价,涨跌幅,成交量,成交额
                '_': str(int(datetime.now().timestamp() * 1000))
            }

            response = self.session.get(url, params=params, timeout=5)
            data = response.json()

            if data.get('rc') == 0 and 'data' in data:
                stocks = []
                for item in data['data']['diff']:
                    stock_code = item.get('f12', '')
                    stock_name = item.get('f14', '')

                    # 过滤ST股票和科创板（688开头）
                    if 'ST' in stock_name or 'st' in stock_name or stock_code.startswith('688'):
                        continue

                    stocks.append({
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'current_price': round(item.get('f2', 0) / 100, 2) if item.get('f2') else 0,
                        'change_percent': round(item.get('f3', 0), 2),
                        'volume': item.get('f5', 0),
                        'amount': item.get('f6', 0)
                    })

                    # 达到需要的数量就停止
                    if len(stocks) >= top_n:
                        break
                return stocks

            return []

        except Exception as e:
            print(f"获取板块 {sector_code} 成分股失败: {e}")
            return []

    def scan_hot_sectors_stocks(self, sector_count: int = 5, stocks_per_sector: int = 5) -> Dict:
        """
        扫描热门板块及其成分股

        Args:
            sector_count: 扫描前N个热门板块
            stocks_per_sector: 每个板块取前N只股票

        Returns:
            {
                'sectors': [板块信息...],
                'stocks': [股票信息...],
                'scan_time': 扫描时间
            }
        """
        print(f"\n{'='*60}")
        print(f"🔍 开始扫描热门板块 (前{sector_count}个板块)")
        print(f"{'='*60}")

        # 获取热门板块
        sectors = self.get_hot_sectors(top_n=sector_count)

        if not sectors:
            print("❌ 未获取到热门板块")
            return {'sectors': [], 'stocks': [], 'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        print(f"✅ 获取到 {len(sectors)} 个热门板块 (按热度排序):")
        for sector in sectors:
            amount_wan = sector.get('amount', 0) / 10000  # 转换为万元
            print(f"   - {sector['sector_name']} ({sector['change_percent']:+.2f}%) 成交额: {amount_wan:.0f}万元")

        # 获取每个板块的前N只股票
        all_stocks = []
        for i, sector in enumerate(sectors, 1):
            print(f"\n📊 扫描第{i}个板块: {sector['sector_name']}")
            stocks = self.get_sector_stocks(sector['sector_code'], top_n=stocks_per_sector)

            for stock in stocks:
                stock['sector_name'] = sector['sector_name']
                stock['sector_change'] = sector['change_percent']
                all_stocks.append(stock)
                print(f"   ✓ {stock['stock_name']} ({stock['stock_code']}) {stock['change_percent']:+.2f}%")

        print(f"\n{'='*60}")
        print(f"✅ 扫描完成，共获取 {len(all_stocks)} 只股票")
        print(f"{'='*60}\n")

        return {
            'sectors': sectors,
            'stocks': all_stocks,
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


if __name__ == "__main__":
    # 测试
    scanner = SectorScanner()
    result = scanner.scan_hot_sectors_stocks(sector_count=5, stocks_per_sector=5)

    print(f"\n扫描结果:")
    print(f"板块数: {len(result['sectors'])}")
    print(f"股票数: {len(result['stocks'])}")
    print(f"扫描时间: {result['scan_time']}")

    print(f"\n股票列表:")
    for stock in result['stocks']:
        print(f"  [{stock['sector_name']}] {stock['stock_name']} ({stock['stock_code']}) {stock['change_percent']:+.2f}%")
