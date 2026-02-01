#!/usr/bin/env python3
"""
股票指数收集器
获取主要股票指数的实时行情
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class IndexCollector:
    """股票指数收集器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        # 主要指数配置
        self.indices = {
            'sh000001': {'name': '上证指数', 'code': '000001'},
            'sz399001': {'name': '深证成指', 'code': '399001'},
            'sz399006': {'name': '创业板指', 'code': '399006'},
            'sh000688': {'name': '科创50', 'code': '000688'},
            'sh000300': {'name': '沪深300', 'code': '000300'},
            'sh000852': {'name': '中证1000', 'code': '000852'}
        }

    def get_index_data(self, index_symbol: str) -> Optional[Dict]:
        """
        获取单个指数数据

        Args:
            index_symbol: 指数代码（如 sh000001）

        Returns:
            {
                'name': 指数名称,
                'code': 指数代码,
                'current': 当前点位,
                'change': 涨跌点数,
                'change_percent': 涨跌幅(%),
                'open': 开盘,
                'high': 最高,
                'low': 最低,
                'volume': 成交量(手),
                'amount': 成交额(万元)
            }
        """
        try:
            url = f"https://qt.gtimg.cn/q={index_symbol}"
            response = self.session.get(url, timeout=5)
            response.encoding = 'gbk'

            if response.status_code != 200:
                return None

            data = response.text
            if '"' not in data or '~' not in data:
                return None

            # 解析数据
            data_part = data.split('"')[1]
            fields = data_part.split('~')

            if len(fields) < 50:
                return None

            # 提取字段
            name = fields[1]
            current = float(fields[3]) if fields[3] else 0
            close_prev = float(fields[4]) if fields[4] else 0
            open_price = float(fields[5]) if fields[5] else 0
            high = float(fields[33]) if fields[33] else 0
            low = float(fields[34]) if fields[34] else 0
            volume = int(float(fields[36])) if fields[36] else 0
            amount = float(fields[37]) if fields[37] else 0

            # 计算涨跌
            change = current - close_prev
            change_percent = (change / close_prev * 100) if close_prev > 0 else 0

            return {
                'name': name,
                'code': index_symbol,
                'current': round(current, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'volume': volume,
                'amount': round(amount / 10000, 2)  # 转换为万元
            }

        except Exception as e:
            print(f"获取指数 {index_symbol} 数据失败: {e}")
            return None

    def get_all_indices(self) -> Dict:
        """
        获取所有主要指数数据

        Returns:
            {
                'indices': [指数数据列表],
                'update_time': 更新时间
            }
        """
        indices_list = []

        for symbol, config in self.indices.items():
            try:
                data = self.get_index_data(symbol)
                if data:
                    indices_list.append(data)
            except Exception as e:
                print(f"获取 {config['name']} 失败: {e}")
                # 添加空数据占位
                indices_list.append({
                    'name': config['name'],
                    'code': config['code'],
                    'current': None,
                    'change': None,
                    'change_percent': None,
                    'error': True
                })

        return {
            'indices': indices_list,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


if __name__ == "__main__":
    # 测试
    collector = IndexCollector()
    result = collector.get_all_indices()

    print("\n" + "="*80)
    print("📊 主要股票指数实时行情")
    print("="*80)

    for index in result['indices']:
        if index.get('error'):
            print(f"\n❌ {index['name']}: 数据获取失败")
        else:
            change_sign = '+' if index['change_percent'] >= 0 else ''
            change_color = '📈' if index['change_percent'] >= 0 else '📉'
            print(f"\n{change_color} {index['name']}")
            print(f"   当前点位: {index['current']}")
            print(f"   涨跌: {change_sign}{index['change']} ({change_sign}{index['change_percent']}%)")
            print(f"   今开: {index['open']}  最高: {index['high']}  最低: {index['low']}")

    print(f"\n⏰ 更新时间: {result['update_time']}")
    print("="*80)
