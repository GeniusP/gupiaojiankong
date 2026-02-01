#!/usr/bin/env python3
"""
股票分析Web应用
使用Flask提供Web界面，每次刷新都重新获取真实数据
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import asyncio
import sys
import os
import re
from datetime import datetime, timedelta
import base64
import hashlib
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.aigc.model_adapter import ZhipuAdapter
from src.monitors.tencent_collector import TencentFinanceCollector
from src.monitors.precious_metals_collector import PreciousMetalsCollector
from src.monitors.sector_scanner import SectorScanner
from src.monitors.index_collector import IndexCollector
from analyze import detect_pattern_type

app = Flask(__name__)
app.secret_key = 'zhipu-ai-stock-analysis-secret-key-2024'  # 用于session加密
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session有效期7天

# Mock用户数据库（内存存储）
users_db = {
    'admin': '123456'  # 默认管理员账号
}


def generate_token(username):
    """生成加密token"""
    # 使用用户名和时间戳生成token
    data = f"{username}:{datetime.now().isoformat()}"
    # 使用SHA256哈希
    hashed = hashlib.sha256(data.encode()).hexdigest()
    # Base64编码
    token = base64.b64encode(f"{username}:{hashed}".encode()).decode()
    return token


def verify_token(token):
    """验证token"""
    try:
        decoded = base64.b64decode(token.encode()).decode()
        username, _ = decoded.split(':')
        return username in users_db
    except:
        return False


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session
        if 'username' in session:
            return f(*args, **kwargs)

        # 检查header中的token
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]  # 移除 'Bearer ' 前缀
            if verify_token(token):
                return f(*args, **kwargs)

        # 未登录，返回JSON错误或重定向
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': '请先登录', 'redirect': '/login'}), 401
        else:
            return redirect(url_for('login'))
    return decorated_function


# 获取配置
API_KEY = os.getenv("ZHIPU_API_KEY")
MODEL = os.getenv("ZHIPU_MODEL", "glm-4-plus")


@app.before_request
def check_authentication():
    """在每个请求前检查登录状态"""
    # 排除登录、注册页面和静态文件
    if request.path in ['/login', '/register', '/api/login', '/api/register', '/logout']:
        return None

    # 排除静态文件
    if request.path.startswith('/static'):
        return None

    # 对于API请求，检查session或token
    if request.path.startswith('/api/'):
        if 'username' not in session:
            token = request.headers.get('Authorization', '')
            if not token or not token.startswith('Bearer ') or not verify_token(token[7:]):
                return jsonify({'success': False, 'message': '请先登录', 'redirect': '/login'}), 401
        return None

    # 对于页面请求，检查session
    if 'username' not in session:
        return redirect(url_for('login'))

    return None


@app.route('/')
@login_required
def index():
    """主页"""
    return render_template('index.html')


@app.route('/batch-quick')
@login_required
def batch_quick():
    """批量快速分析页面"""
    return render_template('batch_quick.html')


@app.route('/login')
def login():
    """登录页面"""
    # 如果已经登录，重定向到首页
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register')
def register():
    """注册页面"""
    # 如果已经登录，重定向到首页
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/login', methods=['POST'])
def api_login():
    """登录API"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # 验证输入
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            })

        # 验证用户
        if username in users_db and users_db[username] == password:
            session['username'] = username
            session.permanent = True  # 保持session
            # 生成token用于本地存储
            token = generate_token(username)
            return jsonify({
                'success': True,
                'message': '登录成功',
                'redirect': '/',
                'token': token,
                'username': username
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            })
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        })


@app.route('/api/register', methods=['POST'])
def api_register():
    """注册API"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # 验证输入
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            })

        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'success': False,
                'message': '用户名长度必须在3-20个字符之间'
            })

        # 验证密码长度
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': '密码至少需要6个字符'
            })

        # 检查用户是否已存在
        if username in users_db:
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            })

        # 注册新用户
        users_db[username] = password

        print(f"新用户注册: {username}")

        return jsonify({
            'success': True,
            'message': '注册成功'
        })
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({
            'success': False,
            'message': '注册失败，请稍后重试'
        })


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """检查登录状态"""
    if 'username' in session:
        return jsonify({
            'authenticated': True,
            'username': session['username']
        })
    else:
        return jsonify({
            'authenticated': False
        })


@app.route('/sector-scan')
@login_required
def sector_scan():
    """板块扫描页面"""
    return render_template('sector_scan.html')


def is_retail_favorite_stock(real_data: dict) -> tuple:
    """
    检测是否为散户最爱买的股票

    散户最爱买的股票特征：
    1. 低价股（<10元）- 散户觉得便宜、好买、能翻倍
    2. 小盘股（<50亿市值）- 散户觉得成长空间大
    3. ST/*ST股票 - 散户赌重组、借壳
    4. 概念股名字（科技、智能、生物、新能源等）- 散户追热点
    5. 高换手+高振幅组合 - 散户喜欢追涨杀跌
    6. 曾经大涨过（前高远高于当前价）- 散户抄底心理

    Args:
        real_data: 股票实时数据字典

    Returns:
        (is_retail_favorite: bool, reason: str, retail_score: int)
    """
    try:
        current_price = real_data.get('实时价', 0)
        stock_name = real_data.get('股票名称', '')
        open_price = real_data.get('开盘价', 0)
        high_price = real_data.get('最高价', 0)
        low_price = real_data.get('最低价', 0)
        prev_close = real_data.get('昨收', 0)
        turnover_rate = real_data.get('换手率', 0)
        market_cap = real_data.get('总市值', 0)

        if current_price <= 0 or not stock_name:
            return False, "", 0

        retail_factors = []
        retail_score = 0

        # ========== 1. 低价股判断（散户最爱）==========

        if current_price < 5:  # 超低价股
            retail_score += 30
            retail_factors.append(f"💸 超低价股({current_price:.2f}元),散户最爱")
        elif current_price < 10:  # 低价股
            retail_score += 20
            retail_factors.append(f"💸 低价股({current_price:.2f}元)")
        elif current_price < 20:  # 中低价
            retail_score += 10
            retail_factors.append(f"价格适中({current_price:.2f}元)")
        elif current_price >= 50:  # 高价股，散户不太买
            retail_score -= 15
            retail_factors.append(f"✓ 高价股({current_price:.2f}元),机构偏好")

        # ========== 2. 小盘股判断（散户觉得好炒作）==========

        if market_cap and market_cap > 0:
            market_cap_yi = market_cap / 100000000

            if market_cap_yi < 30:  # 超小盘
                retail_score += 25
                retail_factors.append(f"🎯 超小盘(市值{market_cap_yi:.0f}亿),易炒作")
            elif market_cap_yi < 50:  # 小盘
                retail_score += 15
                retail_factors.append(f"🎯 小盘股(市值{market_cap_yi:.0f}亿)")
            elif market_cap_yi < 100:  # 中盘
                retail_score += 5
            elif market_cap_yi >= 200:  # 大盘股，散户不太关注
                retail_score -= 10
                retail_factors.append(f"✓ 大盘股(市值{market_cap_yi:.0f}亿)")

        # ========== 3. ST/*ST股票判断（散户赌重组）==========

        if 'ST' in stock_name or '*ST' in stock_name or '退' in stock_name:
            retail_score += 40
            retail_factors.append(f"⚠️ 特殊处理股票({stock_name}),散户赌重组")

        # ========== 4. 概念股名字判断（散户追热点）==========

        # 散户最爱的概念关键词
        concept_keywords = {
            '科技': 15, '智能': 15, 'AI': 15, '人工智能': 15,
            '生物': 12, '医疗': 12, '医药': 12, '健康': 12,
            '新能源': 12, '锂电': 12, '光伏': 12, '储能': 12,
            '芯片': 12, '半导体': 12, '集成电路': 12,
            '软件': 10, '信息': 10, '网络': 10, '数据': 10,
            '材料': 8, '化工': 8, '环保': 8,
            '文化': 8, '传媒': 8, '教育': 8
        }

        matched_concepts = []
        for keyword, score in concept_keywords.items():
            if keyword in stock_name:
                retail_score += score
                matched_concepts.append(keyword)

        if matched_concepts:
            retail_factors.append(f"🔥 热门概念({','.join(matched_concepts)})")

        # ========== 5. 高换手+高振幅组合（散户追涨杀跌）==========

        is_high_turnover = turnover_rate and turnover_rate >= 10
        is_high_amplitude = False
        if high_price > 0 and low_price > 0 and prev_close > 0:
            amplitude = ((high_price - low_price) / low_price * 100)
            is_high_amplitude = amplitude >= 10
            if amplitude >= 15:
                retail_score += 15
                retail_factors.append(f"🎢 巨幅波动({amplitude:.2f}%)")

        # 散户最爱：高换手+高振幅
        if is_high_turnover and is_high_amplitude:
            retail_score += 20
            retail_factors.append(f"🎲 高换手+高振幅,散户追涨杀跌")

        # ========== 6. 涨停/跌停判断（散户最关注）==========

        if prev_close > 0:
            change_percent = ((current_price - prev_close) / prev_close * 100)

            if change_percent >= 9.9:  # 涨停
                retail_score += 25
                retail_factors.append(f"🚀 涨停({change_percent:+.2f}%)")
            elif change_percent <= -9.9:  # 跌停
                retail_score += 20
                retail_factors.append(f"💥 跌停({change_percent:+.2f}%),散户抄底")
            elif change_percent >= 7:  # 大涨
                retail_score += 15
                retail_factors.append(f"大涨({change_percent:+.2f}%)")
            elif change_percent <= -7:  # 大跌
                retail_score += 15
                retail_factors.append(f"大跌({change_percent:+.2f}%),散户抄底")

        # ========== 7. 成交量异常放大（散户跟风）==========

        if turnover_rate and turnover_rate > 0:
            if turnover_rate >= 20:  # 超高换手
                retail_score += 20
                retail_factors.append(f"📊 超高换手({turnover_rate:.2f}%),散户跟风")
            elif turnover_rate >= 15:  # 高换手
                retail_score += 15
                retail_factors.append(f"高换手({turnover_rate:.2f}%)")

        # ========== 8. 冲高回落（散户追高被套）==========

        if high_price > 0 and current_price > 0 and high_price > current_price:
            pullback_from_high = ((high_price - current_price) / high_price * 100)
            if pullback_from_high > 5:
                retail_score += 10
                retail_factors.append(f"⛰️ 冲高回落({pullback_from_high:.2f}%)")

        # ========== 综合判断 ==========

        # 低价 + 小盘 + 高换手 = 散户最爱组合
        is_very_cheap = current_price < 10
        is_very_small_cap = market_cap and (market_cap / 100000000) < 50
        is_very_high_turnover = turnover_rate and turnover_rate >= 10

        if is_very_cheap and is_very_small_cap and is_very_high_turnover:
            retail_score += 15
            if not any("散户最爱" in f for f in retail_factors):
                retail_factors.insert(0, "🎯 散户最爱组合(低价+小盘+高换手)")

        # 风险分数 > 40 判定为散户最爱
        is_retail_favorite = retail_score > 40

        reason = "、".join(retail_factors) if retail_factors else ""

        return is_retail_favorite, reason, max(0, retail_score)

    except Exception as e:
        print(f"检测散户最爱股票时出错: {e}")
        return False, "", 0


def is_speculative_stock(real_data: dict) -> tuple:
    """
    检测是否为游资炒作的股票（游资票）

    基于"核心3问+硬指标阈值"判断标准：

    【第一问 看资金&龙虎榜】（暂无法获取，跳过）
    【第二问 看量能&换手】（最易判断）⭐核心
    【第三问 看走势&驱动】（定性关键）

    ✅ 硬指标阈值：
    - 游资票：换手率≥15%、振幅≥8%、流通值40-200亿
    - 机构票：换手率≤5%、振幅≤5%、大中盘百亿起

    ✅ 终极速判口诀：
    1. 高换手(≥15%) + 大振幅(≥8%) + 中小盘 = 游资票
    2. 低换手(≤5%) + 小振幅(≤5%) + 大盘 = 机构票

    Args:
        real_data: 股票实时数据字典

    Returns:
        (is_speculative: bool, reason: str, risk_score: int)
    """
    try:
        current_price = real_data.get('实时价', 0)
        open_price = real_data.get('开盘价', 0)
        high_price = real_data.get('最高价', 0)
        low_price = real_data.get('最低价', 0)
        prev_close = real_data.get('昨收', 0)
        amount = real_data.get('成交额', 0)  # 成交额（元）
        turnover_rate = real_data.get('换手率', 0)  # 换手率
        market_cap = real_data.get('总市值', 0)  # 总市值

        if current_price <= 0 or prev_close <= 0:
            return False, "", 0

        risk_factors = []
        risk_score = 0

        # ========== 【第二问 看量能&换手】核心指标 ==========

        # 1. 换手率判断（最关键指标）
        if turnover_rate and turnover_rate > 0:
            if turnover_rate >= 20:  # 连板期水平
                risk_score += 40
                risk_factors.append(f"⚠️ 超高换手({turnover_rate:.2f}%),连板特征")
            elif turnover_rate >= 15:  # 游资票硬指标
                risk_score += 30
                risk_factors.append(f"⚠️ 高换手({turnover_rate:.2f}%),游资活跃")
            elif turnover_rate >= 10:
                risk_score += 15
                risk_factors.append(f"换手率偏高({turnover_rate:.2f}%)")
            elif turnover_rate <= 5:  # 机构票特征
                risk_score -= 20  # 降低风险分数
                risk_factors.append(f"✓ 低换手({turnover_rate:.2f}%),机构特征")

        # ========== 【第三问 看走势&驱动】定性判断 ==========

        # 2. 日内振幅判断（硬指标：游资票≥8%，机构票≤5%）
        if high_price > 0 and low_price > 0:
            amplitude = ((high_price - low_price) / low_price * 100)
            if amplitude >= 12:  # 暴涨暴跌
                risk_score += 30
                risk_factors.append(f"⚠️ 巨幅震荡({amplitude:.2f}%),情绪化")
            elif amplitude >= 8:  # 游资票硬指标
                risk_score += 20
                risk_factors.append(f"⚠️ 大振幅({amplitude:.2f}%),游资特征")
            elif amplitude <= 5:  # 机构票特征
                risk_score -= 15  # 降低风险分数
                risk_factors.append(f"✓ 小振幅({amplitude:.2f}%),稳健")

        # 3. 单日涨幅判断（连板/涨停特征）
        change_percent = ((current_price - prev_close) / prev_close * 100)
        if change_percent >= 9.9:  # 涨停
            risk_score += 25
            risk_factors.append(f"⚠️ 涨停({change_percent:+.2f}%)")
        elif change_percent >= 7:  # 大涨
            risk_score += 15
            risk_factors.append(f"大涨({change_percent:+.2f}%)")
        elif change_percent <= 3 and change_percent >= 0:  # 温和上涨（机构特征）
            risk_score -= 10
            risk_factors.append(f"✓ 温和上涨({change_percent:+.2f}%)")

        # ========== 市值判断（辅助指标） ==========

        if market_cap and market_cap > 0:
            market_cap_yi = market_cap / 100000000  # 转换为亿

            # 流通值40-200亿：游资票偏好区间
            if 40 <= market_cap_yi <= 200:
                if turnover_rate and turnover_rate >= 15:
                    risk_score += 15
                    risk_factors.append(f"中小盘+高换手(市值{market_cap_yi:.0f}亿)")
                elif turnover_rate and turnover_rate >= 10:
                    risk_score += 10
                    risk_factors.append(f"中小盘(市值{market_cap_yi:.0f}亿)")

            # 小于40亿：容易被控盘
            elif market_cap_yi < 40:
                if turnover_rate and turnover_rate >= 15:
                    risk_score += 20
                    risk_factors.append(f"⚠️ 小盘易控盘(市值{market_cap_yi:.0f}亿,换手{turnover_rate:.2f}%)")
                elif turnover_rate and turnover_rate >= 10:
                    risk_score += 10
                    risk_factors.append(f"小盘股(市值{market_cap_yi:.0f}亿)")

            # 大于100亿：机构票偏好
            elif market_cap_yi >= 100:
                if turnover_rate and turnover_rate <= 5:
                    risk_score -= 15
                    risk_factors.append(f"✓ 大盘低换手(市值{market_cap_yi:.0f}亿),机构偏好")

        # ========== 情绪化走势特征 ==========

        # 冲高回落（从高点回落>5%）
        if high_price > 0 and current_price > 0:
            pullback_from_high = ((high_price - current_price) / high_price * 100)
            if pullback_from_high > 5:
                risk_score += 15
                risk_factors.append(f"⚠️ 冲高回落({pullback_from_high:.2f}%)")

        # 开盘强势但回落
        if open_price > 0 and current_price > 0 and open_price > prev_close:
            open_change = ((open_price - prev_close) / prev_close * 100)
            current_change = ((current_price - prev_close) / prev_close * 100)
            if open_change > current_change and open_change > 3:
                pullback = open_change - current_change
                if pullback > 3:
                    risk_score += 10
                    risk_factors.append(f"开盘回落({pullback:.2f}%)")

        # ========== 成交额异常放大判断 ==========

        if market_cap and amount and market_cap > 0:
            amount_ratio = (amount / market_cap * 100)
            if amount_ratio > 40:
                risk_score += 10
                risk_factors.append(f"成交额异常({amount_ratio:.0f}%市值)")

        # ========== 综合判断（终极速判口诀）==========

        # 口诀1: 高换手(≥15%) + 大振幅(≥8%) + 中小盘 = 游资票
        is_high_turnover = turnover_rate and turnover_rate >= 15
        is_high_amplitude = False
        if high_price > 0 and low_price > 0:
            amplitude = ((high_price - low_price) / low_price * 100)
            is_high_amplitude = amplitude >= 8
        is_mid_small_cap = False
        if market_cap and market_cap > 0:
            market_cap_yi = market_cap / 100000000
            is_mid_small_cap = market_cap_yi <= 200

        # 满足游资票"三位一体"特征，直接判定
        if is_high_turnover and is_high_amplitude and is_mid_small_cap:
            is_speculative = True
            if not any("三位一体" in f for f in risk_factors):
                risk_factors.insert(0, "⚠️ 游资票三位一体(高换手+大振幅+中小盘)")
        else:
            # 否则按风险分数判断
            # 风险分数 > 50 判定为游资票
            is_speculative = risk_score > 50 or len([f for f in risk_factors if "⚠️" in f]) >= 2

        reason = "、".join(risk_factors) if risk_factors else ""

        return is_speculative, reason, max(0, risk_score)

    except Exception as e:
        print(f"检测游资票时出错: {e}")
        return False, "", 0


@app.route('/daily-recommend')
@login_required
def daily_recommend():
    """每日推荐页面"""
    return render_template('daily_recommend.html')


@app.route('/finance-news')
@login_required
def finance_news():
    """财经新闻页面"""
    return render_template('finance_news.html')


@app.route('/api/finance-news', methods=['GET'])
def finance_news_api():
    """财经新闻API"""
    try:
        from src.monitors.finance_news_collector import FinanceNewsCollector

        collector = FinanceNewsCollector()
        result = collector.get_all_news(limit=30)

        return jsonify({
            'success': True,
            'data': result['data'],
            'update_time': result['update_time']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


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


@app.route('/api/daily-recommend', methods=['POST'])
def daily_recommend_api():
    """每日推荐API - 基于热门板块和图形分析推荐股票"""
    try:
        from src.monitors.tencent_collector import TencentFinanceCollector

        # 获取参数
        sector_count = request.json.get('sector_count', 10)
        stocks_per_sector = request.json.get('stocks_per_sector', 5)

        # 扫描板块和股票
        scanner = SectorScanner()
        scan_result = scanner.scan_hot_sectors_stocks(
            sector_count=sector_count,
            stocks_per_sector=stocks_per_sector
        )

        # 获取股票实时数据并检测图形
        collector = TencentFinanceCollector()
        recommended_stocks = []

        for stock in scan_result['stocks']:
            stock_code = stock['stock_code']
            real_data = collector.get_stock_realtime_data(stock_code)

            if real_data and real_data.get('股票名称'):
                # 检测图形类型
                pattern_type, confidence, reason = detect_pattern_type(real_data)

                # 计算涨跌幅
                prev_close = real_data.get('昨收', real_data.get('开盘价', 0))
                change_percent = ((real_data['实时价'] - prev_close) / prev_close * 100) if prev_close > 0 else 0

                # 检测是否为游资票（标记但不过滤）
                is_speculative, speculative_reason, risk_score = is_speculative_stock(real_data)

                # 检测是否为散户最爱买的股票（标记但不过滤）
                is_retail_favorite, retail_reason, retail_score = is_retail_favorite_stock(real_data)

                stock_info = {
                    'stock_code': real_data.get('股票代码'),
                    'stock_name': stock['stock_name'],
                    'sector_name': stock['sector_name'],
                    'sector_change': stock['sector_change'],
                    'current_price': real_data.get('实时价'),
                    'open_price': real_data.get('开盘价'),
                    'high_price': real_data.get('最高价'),
                    'low_price': real_data.get('最低价'),
                    'volume': real_data.get('成交量'),
                    'amount': real_data.get('成交额'),
                    'change_percent': round(change_percent, 2),
                    'pattern_type': pattern_type,
                    'pattern_detection': {
                        'type': pattern_type,
                        'confidence': confidence,
                        'description': reason
                    },
                    # 添加标记字段
                    'is_speculative': is_speculative,
                    'speculative_reason': speculative_reason,
                    'speculative_risk_score': risk_score,
                    'is_retail_favorite': is_retail_favorite,
                    'retail_reason': retail_reason,
                    'retail_score': retail_score
                }

                recommended_stocks.append(stock_info)

        # 按图形类型排序，优先显示强势上涨的股票
        pattern_priority = {
            '强势上涨': 1,
            '震荡整理': 2,
            '冲板回落': 3,
            '开盘跳水': 4,
            '破位下跌': 5
        }

        recommended_stocks.sort(
            key=lambda x: (pattern_priority.get(x['pattern_type'], 6), -abs(x['change_percent']))
        )

        return jsonify({
            'success': True,
            'stocks': recommended_stocks,
            'sectors': scan_result['sectors'],
            'update_time': scan_result['scan_time']
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


@app.route('/api/index-data', methods=['GET'])
def index_data_api():
    """获取主要股票指数实时行情API"""
    try:
        collector = IndexCollector()
        data = collector.get_all_indices()

        if data and data['indices']:
            # 计算沪深京总成交额（上证+深证+北证）
            total_amount_wan = 0
            for index in data['indices']:
                # 计算上证指数、深证成指、北证50
                if index.get('amount') and not index.get('error'):
                    code = index.get('code', '')
                    # code 格式可能是 'sh000001' 或 '000001'
                    if code in ['sh000001', 'sz399001', 'bj899050', '000001', '399001', '899050']:
                        total_amount_wan += index['amount']

            # 转换为亿元（万元 / 10000 = 亿元）
            total_amount_yi = total_amount_wan / 10000

            data['total_amount'] = round(total_amount_yi, 2)

            return jsonify({
                'success': True,
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取指数数据'
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
                'pattern_type': pattern_type,  # 添加pattern_type以保持与daily recommend API的一致性
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
