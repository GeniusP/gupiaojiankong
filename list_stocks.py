#!/usr/bin/env python3
"""
列出系统中的所有默认股票
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_stocks():
    """打印所有默认股票"""
    from src.monitors.data_collector import MockDataCollector

    collector = MockDataCollector()

    print("\n" + "="*80)
    print(" " * 25 + "📊 系统默认股票列表")
    print("="*80)

    # 按板块分组
    sectors = {}
    for stock_code, stock_data in collector.mock_stocks.items():
        sector = stock_data.get("板块名称", "其他")
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock_data)

    # 按板块打印
    for sector, stocks in sorted(sectors.items()):
        print(f"\n【{sector}】")
        print("-"*80)
        print(f"{'股票代码':<10} {'股票名称':<12} {'开盘价':<8} {'实时价':<8} {'涨跌幅':<8}")
        print("-"*80)

        for stock in stocks:
            code = stock["股票代码"]
            name = stock["股票名称"]
            open_price = stock["开盘价"]
            current_price = stock["实时价"]
            change = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0

            print(f"{code:<10} {name:<12} {open_price:<8.2f} {current_price:<8.2f} {change:>+6.2f}%")

    # 打印板块涨跌
    print("\n" + "="*80)
    print("板块涨跌幅")
    print("="*80)

    for sector_name, sector_data in sorted(collector.mock_sectors.items()):
        change = sector_data.get("涨跌幅", 0)
        print(f"{sector_name:<8} {change:>+6.2f}%")

    # 打印大盘指数
    print("\n" + "="*80)
    print("大盘指数")
    print("="*80)

    for index_name, index_data in sorted(collector.mock_indices.items()):
        change = index_data.get("涨跌幅", 0)
        print(f"{index_name:<8} {change:>+6.2f}%")

    print("\n" + "="*80)
    print(f"总计: {len(collector.mock_stocks)} 只股票，{len(collector.mock_sectors)} 个板块")
    print("="*80)


def test_real_stock(stock_code: str):
    """测试获取单个股票数据"""
    from src.monitors.data_collector import MockDataCollector

    collector = MockDataCollector()
    data = collector.get_stock_realtime_data(stock_code)

    print("\n" + "="*80)
    print(f"股票数据: {data['股票代码']} {data['股票名称']}")
    print("="*80)

    for key, value in data.items():
        if key not in ["股票代码", "股票名称"]:
            print(f"{key}: {value}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="股票数据查询工具")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有默认股票")
    parser.add_argument("--stock", "-s", type=str, help="查询指定股票代码")

    args = parser.parse_args()

    if args.list:
        print_stocks()
    elif args.stock:
        test_real_stock(args.stock)
    else:
        print_stocks()
