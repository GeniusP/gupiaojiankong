#!/usr/bin/env python3
"""
股票分析Web应用
使用Flask提供Web界面，每次刷新都重新获取真实数据
"""

from flask import Flask, render_template, request, jsonify
import asyncio
import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.tencent_collector import TencentFinanceCollector
from src.monitors.precious_metals_collector import PreciousMetalsCollector
from src.monitors.sector_scanner import SectorScanner
from analyze import detect_pattern_type

app = Flask(__name__)

# 获取配置
API_KEY = os.getenv("ZHIPU_API_KEY")
MODEL = os.getenv("ZHIPU_MODEL", "glm-4-plus")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/batch-quick')
def batch_quick():
    """批量快速分析页面"""
    return render_template('batch_quick.html')


@app.route('/sector-scan')
def sector_scan():
    """板块扫描页面"""
    return render_template('sector_scan.html')


@app.route('/api/sector-scan', methods=['POST'])
def sector_scan_api():
    """板块扫描API - 扫描热门板块并筛选图形"""
    try:
        from src.monitors.tencent_collector import TencentFinanceCollector

        # 获取参数
        sector_count = request.json.get('sector_count', 5)
        stocks_per_sector = request.json.get('stocks_per_sector', 5)

        # 扫描板块和股票
        scanner = SectorScanner()
        scan_result = scanner.scan_hot_sectors_stocks(
            sector_count=sector_count,
            stocks_per_sector=stocks_per_sector
        )

        # 获取股票实时数据并检测图形
        collector = TencentFinanceCollector()
        stocks_with_patterns = []

        for stock in scan_result['stocks']:
            stock_code = stock['stock_code']
            real_data = collector.get_stock_realtime_data(stock_code)

            if real_data and real_data.get('股票名称'):
                # 检测图形类型
                pattern_type, confidence, reason = detect_pattern_type(real_data)

                # 计算涨跌幅
                prev_close = real_data.get('昨收', real_data.get('开盘价', 0))
                change_percent = ((real_data['实时价'] - prev_close) / prev_close * 100) if prev_close > 0 else 0

                stock_info = {
                    'stock_code': real_data.get('股票代码'),  # 使用标准化后的代码
                    'stock_name': stock['stock_name'],
                    'sector_name': stock['sector_name'],
                    'sector_change': stock['sector_change'],
                    'current_price': real_data.get('实时价'),
                    'open_price': real_data.get('开盘价'),
                    'high_price': real_data.get('最高价'),
                    'low_price': real_data.get('最低价'),
                    'prev_close': prev_close,
                    'change_percent': round(change_percent, 2),
                    'volume': real_data.get('成交量'),
                    'limit_up': real_data.get('涨停价'),
                    'pattern_type': pattern_type,
                    'pattern_confidence': confidence,
                    'pattern_reason': reason
                }

                stocks_with_patterns.append(stock_info)

        # 筛选符合条件的图形
        target_patterns = ['开盘跳水', '冲板回落', '破位下跌']
        filtered_stocks = [s for s in stocks_with_patterns if s['pattern_type'] in target_patterns]

        return jsonify({
            'success': True,
            'sectors': scan_result['sectors'],
            'all_stocks': stocks_with_patterns,
            'filtered_stocks': filtered_stocks,
            'scan_time': scan_result['scan_time'],
            'total_count': len(stocks_with_patterns),
            'filtered_count': len(filtered_stocks)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/stock-detail/<stock_code>', methods=['GET'])
def stock_detail_api(stock_code):
    """股票详情API"""
    try:
        from src.monitors.tencent_collector import TencentFinanceCollector

        collector = TencentFinanceCollector()
        real_data = collector.get_stock_realtime_data(stock_code)

        if not real_data or not real_data.get('股票名称'):
            # 标准化股票代码用于错误提示
            display_code = stock_code.upper() if any(c.isalpha() for c in stock_code) else stock_code
            return jsonify({
                'success': False,
                'error': f'无法获取股票 {display_code} 的数据'
            })

        # 检测图形类型
        pattern_type, confidence, reason = detect_pattern_type(real_data)

        # 计算涨跌幅
        prev_close = real_data.get('昨收', real_data.get('开盘价', 0))
        change_percent = ((real_data['实时价'] - prev_close) / prev_close * 100) if prev_close > 0 else 0

        # 准备详细数据
        detail = {
            'stock_code': real_data.get('股票代码'),  # 使用标准化后的代码
            'stock_name': real_data.get('股票名称'),
            'current_price': real_data.get('实时价'),
            'open_price': real_data.get('开盘价'),
            'high_price': real_data.get('最高价'),
            'low_price': real_data.get('最低价'),
            'prev_close': prev_close,
            'change_percent': round(change_percent, 2),
            'volume': real_data.get('成交量'),
            'amount': real_data.get('成交额'),
            'limit_up': real_data.get('涨停价'),
            'limit_down': real_data.get('跌停价'),
            'pattern_type': pattern_type,
            'pattern_confidence': confidence,
            'pattern_reason': reason,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 如果是支持的图形，进行AI分析
        supported_patterns = ['开盘跳水', '冲板回落', '破位下跌']

        if pattern_type in supported_patterns and API_KEY:
            analysis_data = {
                "股票代码": stock_code,
                "股票名称": real_data["股票名称"],
                "触发时间": datetime.now().strftime("%H:%M"),
                "开盘价": real_data['开盘价'],
                "实时价": real_data['实时价'],
                "最高价": real_data["最高价"],
                "涨停价": real_data["涨停价"],
                "5日均线": round(real_data['实时价'] * 0.995, 2),
                "20日均线": round(real_data['实时价'] * 0.98, 2),
                "前期平台支撑位": round(real_data['实时价'] * 0.97, 2),
                "成交额放大比例": 25.0,
                "板块名称": real_data.get("板块名称", "未知"),
                "板块涨跌幅": 0,
                "大盘涨跌幅": 0,
                "最新消息": "无"
            }

            # 添加图形特定字段
            if pattern_type == "开盘跳水":
                drop = abs(round((real_data['开盘价'] - real_data['实时价']) / real_data['开盘价'] * 100, 2))
                analysis_data.update({
                    "开盘分钟数": 10,
                    "跌幅": drop,
                    "均线类型": 5,
                    "均线价格": analysis_data["5日均线"]
                })
            elif pattern_type == "破位下跌":
                analysis_data.update({
                    "支撑位价格": analysis_data["前期平台支撑位"],
                    "破位后未回弹分钟数": 5
                })
            elif pattern_type == "冲板回落":
                surge = round((real_data['最高价'] - real_data['开盘价']) / real_data['开盘价'] * 100, 2)
                retrace = round((real_data['最高价'] - real_data['实时价']) / real_data['最高价'] * 100, 2)
                analysis_data.update({
                    "涨幅": surge,
                    "回落幅度": retrace,
                    "封板挂单量": 10000
                })

            # 生成提示词
            from src.templates.prompt_templates import generate_prompt, TemplateType
            prompt = generate_prompt(
                chart_type=pattern_type,
                stock_data=analysis_data,
                trading_style="短线",
                template_type=TemplateType.SIMPLIFIED
            )

            # 调用智谱AI
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                adapter = ZhipuAdapter(api_key=API_KEY, model=MODEL)
                ai_response = loop.run_until_complete(adapter.async_chat(prompt))

                detail['ai_analysis'] = ai_response

                # 生成操作建议
                from src.utils.suggestions import OperationSuggestionGenerator
                suggestion = OperationSuggestionGenerator.generate_suggestion(
                    pattern_type, analysis_data, ai_response
                )

                detail['operation_suggestion'] = {
                    'action': suggestion.action,
                    'confidence': suggestion.confidence,
                    'reasoning': suggestion.reasoning,
                    'price_levels': suggestion.price_level,
                    'risk_warning': suggestion.risk_warning
                }
            finally:
                loop.close()

        return jsonify({
            'success': True,
            'detail': detail
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/batch-quick-analyze', methods=['POST'])
def batch_quick_analyze_api():
    """批量快速分析API - 同时分析多只股票"""
    try:
        data = request.json

        # 从请求中获取股票列表，如果没有则使用默认列表
        # 支持 codes 和 stock_codes 两种字段名
        stock_codes = data.get('codes') or data.get('stock_codes', ['601869', '518880', '603993', '601138'])

        # 异步批量分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async def batch_analyze():
                results = []
                for stock_code in stock_codes:
                    result = await analyze_stock_async(stock_code)
                    results.append(result)
                return results

            results = loop.run_until_complete(batch_analyze())

            return jsonify({
                'success': True,
                'results': results,
                'total': len(stock_codes),
                'stock_codes': stock_codes,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        finally:
            loop.close()

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/metals-prices', methods=['GET'])
def metals_prices_api():
    """获取贵金属实时价格API"""
    try:
        collector = PreciousMetalsCollector()
        prices = collector.get_metals_prices()

        if prices:
            return jsonify({
                'success': True,
                'data': prices
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取贵金属价格'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/stock-search', methods=['GET'])
def stock_search_api():
    """股票搜索API - 通过名称或代码搜索股票"""
    try:
        keyword = request.args.get('keyword', '').strip()

        if not keyword:
            return jsonify({
                'success': False,
                'error': '请提供搜索关键词'
            })

        # 如果关键词本身是有效的股票代码，直接返回
        # 支持：6位数字(A股)、5位数字(港股)、纯字母(美股)
        is_valid_code = (
            re.match(r'^\d{6}$', keyword) or      # A股
            re.match(r'^\d{5}$', keyword) or      # 港股
            re.match(r'^[a-zA-Z]+$', keyword)     # 美股
        )

        if is_valid_code:
            # 标准化股票代码
            if re.match(r'^[a-zA-Z]+$', keyword):
                keyword = keyword.upper()
            return jsonify({
                'success': True,
                'results': [{
                    'code': keyword,
                    'name': keyword,
                    'market': 'unknown'
                }]
            })

        # 使用腾讯财经API搜索
        collector = TencentFinanceCollector()
        results = collector.search_stock_by_name(keyword)

        if results:
            return jsonify({
                'success': True,
                'results': results
            })
        else:
            return jsonify({
                'success': False,
                'error': '未找到匹配的股票'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/stock-kline', methods=['GET'])
def stock_kline_api():
    """K线数据API - 获取股票历史K线数据"""
    try:
        stock_code = request.args.get('stock_code', '').strip()
        count = int(request.args.get('count', 100))  # 默认100条数据

        if not stock_code:
            return jsonify({
                'success': False,
                'error': '请提供股票代码'
            })

        collector = TencentFinanceCollector()
        result = collector.get_stock_kline_data(stock_code, count=count)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/analyze', methods=['POST'])
def analyze_api():
    """
    分析API接口
    每次调用都重新获取真实数据
    """
    try:
        data = request.json
        stock_code = data.get('stock_code', '').strip()

        if not stock_code:
            return jsonify({
                'success': False,
                'error': '请提供股票代码'
            })

        # 异步执行分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                analyze_stock_async(stock_code)
            )

            if result.get('success'):
                return jsonify(result)
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', '分析失败')
                })
        finally:
            loop.close()

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


async def analyze_stock_async(stock_code: str):
    """
    异步分析股票
    使用真实数据和AI分析
    """
    try:
        # 1. 获取真实数据
        collector = TencentFinanceCollector()
        real_data = collector.get_stock_realtime_data(stock_code)

        if not real_data or not real_data.get("股票名称"):
            # 标准化股票代码用于错误提示
            display_code = stock_code.upper() if any(c.isalpha() for c in stock_code) else stock_code
            return {
                'success': False,
                'error': f'无法获取股票 {display_code} 的数据'
            }

        # 2. 检测图形类型
        pattern_type, confidence, reason = detect_pattern_type(real_data)

        # 计算涨跌幅（使用昨收价）
        prev_close = real_data.get('昨收', real_data.get('开盘价', 0))
        current = real_data.get('实时价', 0)
        high = real_data.get('最高价', current)
        low = real_data.get('最低价', current)
        change_percent = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0

        # 计算关键价位
        key_price_levels = {
            # 当前价格区间
            '当前价格': current,
            '今开': real_data.get('开盘价', current),
            '昨收': prev_close,

            # 今日压力位（基于当前价格上方）
            '第一压力位': round(current * 1.02, 2),
            '第二压力位': round(current * 1.05, 2),
            '第三压力位': round(current * 1.08, 2),

            # 今日支撑位（基于当前价格下方）
            '第一支撑位': round(current * 0.98, 2),
            '第二支撑位': round(current * 0.95, 2),
            '第三支撑位': round(current * 0.92, 2),

            # 今日实际价位
            '今日最高': high,
            '今日最低': low,
            '涨停价': real_data.get('涨停价', round(prev_close * 1.1, 2) if prev_close > 0 else 0),
            '跌停价': real_data.get('跌停价', round(prev_close * 0.9, 2) if prev_close > 0 else 0),

            # 均线估算（基于当前价格）
            '5日均线': round(current * 0.995, 2),
            '10日均线': round(current * 0.99, 2),
            '20日均线': round(current * 0.98, 2),
        }

        # 准备响应数据
        response = {
            'success': True,
            'data': {
                'stock_code': real_data.get('股票代码'),  # 使用标准化后的股票代码
                'stock_name': real_data.get('股票名称'),
                'open_price': real_data.get('开盘价'),
                'current_price': real_data.get('实时价'),
                'high_price': real_data.get('最高价'),
                'low_price': real_data.get('最低价'),
                'limit_up': real_data.get('涨停价'),
                'change_percent': round(change_percent, 2),
                'volume': real_data.get('成交量'),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'pattern_detection': {
                'type': pattern_type,
                'confidence': confidence,
                'reason': reason
            },
            'key_price_levels': key_price_levels
        }

        # 3. 如果是支持的图形类型，进行AI分析
        supported_patterns = ["开盘跳水", "破位下跌", "冲板回落"]

        if pattern_type in supported_patterns and API_KEY:
            # 准备分析数据
            current = real_data['实时价']
            open_price = real_data['开盘价']

            analysis_data = {
                "股票代码": stock_code,
                "股票名称": real_data["股票名称"],
                "触发时间": datetime.now().strftime("%H:%M"),
                "开盘价": open_price,
                "实时价": current,
                "最高价": real_data["最高价"],
                "涨停价": real_data["涨停价"],
                "5日均线": round(current * 0.995, 2),
                "20日均线": round(current * 0.98, 2),
                "前期平台支撑位": round(current * 0.97, 2),
                "成交额放大比例": 25.0,
                "板块名称": real_data.get("板块名称", "未知"),
                "板块涨跌幅": 0,
                "大盘涨跌幅": 0,
                "最新消息": "无"
            }

            # 添加图形特定字段
            if pattern_type == "开盘跳水":
                drop = abs(round((open_price - current) / open_price * 100, 2)) if open_price > 0 else 0
                analysis_data.update({
                    "开盘分钟数": 10,
                    "跌幅": drop,
                    "均线类型": 5,
                    "均线价格": analysis_data["5日均线"]
                })
            elif pattern_type == "破位下跌":
                analysis_data.update({
                    "支撑位价格": analysis_data["前期平台支撑位"],
                    "破位后未回弹分钟数": 5
                })
            elif pattern_type == "冲板回落":
                surge = round((real_data['最高价'] - open_price) / open_price * 100, 2) if open_price > 0 else 0
                retrace = round((real_data['最高价'] - current) / real_data['最高价'] * 100, 2) if real_data['最高价'] > 0 else 0
                analysis_data.update({
                    "涨幅": surge,
                    "回落幅度": retrace,
                    "封板挂单量": 10000
                })

            # 生成提示词
            from src.templates.prompt_templates import generate_prompt, TemplateType
            prompt = generate_prompt(
                chart_type=pattern_type,
                stock_data=analysis_data,
                trading_style="短线",
                template_type=TemplateType.SIMPLIFIED
            )

            # 调用智谱AI
            adapter = ZhipuAdapter(api_key=API_KEY, model=MODEL)
            ai_response = await adapter.async_chat(prompt)

            response['ai_analysis'] = {
                'pattern_type': pattern_type,
                'analysis': ai_response,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 生成操作建议
            from src.utils.suggestions import OperationSuggestionGenerator, format_suggestion
            suggestion = OperationSuggestionGenerator.generate_suggestion(
                pattern_type, analysis_data, ai_response
            )

            response['operation_suggestion'] = {
                'action': suggestion.action,
                'confidence': suggestion.confidence,
                'reasoning': suggestion.reasoning,
                'price_levels': suggestion.price_level,
                'risk_warning': suggestion.risk_warning
            }
        else:
            # 不适合分析的状态
            if pattern_type not in supported_patterns:
                response['message'] = f'当前市场状态为"{pattern_type}"，不适合图形分析'

                if pattern_type == "强势上涨":
                    response['suggestions'] = [
                        "关注是否突破前高",
                        "注意成交量是否放大",
                        "设置止盈位保护利润"
                    ]
                elif pattern_type == "震荡整理":
                    response['suggestions'] = [
                        "等待方向明确",
                        "关注支撑/压力位",
                        "控制仓位"
                    ]
            else:
                response['message'] = '未配置智谱AI密钥，无法进行AI分析'

        return response

    except Exception as e:
        return {
            'success': False,
            'error': f'分析失败: {str(e)}'
        }


@app.route('/api/batch_analyze', methods=['POST'])
def batch_analyze_api():
    """批量分析API"""
    try:
        data = request.json
        stock_codes = data.get('stock_codes', [])

        if not stock_codes:
            return jsonify({
                'success': False,
                'error': '请提供股票代码列表'
            })

        # 异步批量分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async def batch_analyze():
                results = []
                for stock_code in stock_codes:
                    result = await analyze_stock_async(stock_code)
                    results.append(result)
                return results

            results = loop.run_until_complete(batch_analyze())

            return jsonify({
                'success': True,
                'results': results,
                'total': len(stock_codes),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        finally:
            loop.close()

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" " * 20 + "🌐 股票分析Web服务")
    print("="*70)
    print("\n✅ 使用腾讯财经API获取实时数据")
    print("✅ 使用智谱GLM-4-Plus模型分析")
    print("✅ 每次刷新都重新获取最新数据")
    print("="*70)

    if not API_KEY:
        print("\n⚠️  警告: 未配置智谱AI API密钥")
        print("   将无法进行AI分析，仅显示行情数据")
        print("   请在.env文件中设置: ZHIPU_API_KEY=your_api_key")
        print("="*70)

    print("\n🚀 启动Web服务...")
    print("📱 访问地址: http://127.0.0.1:5001")
    print("⏹️  按 Ctrl+C 停止服务")
    print("="*70)
    print()

    # 禁用自动重载，避免文件变化导致服务器频繁重启
    # use_reloader=False: 禁用文件监控和自动重载
    # debug=True: 保留调试错误信息功能
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
