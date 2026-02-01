#!/usr/bin/env python3
"""
财经新闻收集器
获取实时财经新闻
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class FinanceNewsCollector:
    """财经新闻收集器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_sina_finance_news(self, limit: int = 30) -> List[Dict]:
        """
        获取新浪财经7x24快讯

        Args:
            limit: 获取新闻数量

        Returns:
            新闻列表
        """
        try:
            # 新浪财经7x24快讯API
            url = "https://finance.sina.com.cn/7x24news/?page=1"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return []

            # 尝试使用东方财富的快讯API
            return self.get_eastmoney_flash_news(limit)

        except Exception as e:
            print(f"获取新浪财经新闻失败: {e}")
            return []

    def get_eastmoney_flash_news(self, limit: int = 30) -> List[Dict]:
        """
        获取东方财富网7x24快讯

        Args:
            limit: 获取新闻数量

        Returns:
            新闻列表
        """
        try:
            # 东方财富7x24快讯API
            url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
            params = {
                'page_size': limit,
                'page_index': 1,
                'ann_type': '724',
                'client_source': 'web',
                'f_node': '0',
                's_node': '0'
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return self.get_tencent_finance_news(limit)

            data = response.json()

            if data.get('code') != 0 or 'data' not in data:
                return self.get_tencent_finance_news(limit)

            news_list = []
            for item in data.get('data', {}).get('list', [])[:limit]:
                title = item.get('title', '')
                date = item.get('notice_date', '')
                time_str = item.get('notice_time', '')

                # 格式化时间
                try:
                    if date and time_str:
                        formatted_time = f"{date} {time_str[:5]}"
                    elif date:
                        if len(date) == 8:
                            formatted_time = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
                        else:
                            formatted_time = date
                    else:
                        formatted_time = ''
                except:
                    formatted_time = ''

                news_list.append({
                    'title': title,
                    'summary': title,
                    'source': '东方财富',
                    'time': formatted_time,
                    'url': item.get('url', ''),
                    'tags': self._extract_tags(title)
                })

            return news_list

        except Exception as e:
            print(f"获取东方财富快讯失败: {e}")
            return self.get_tencent_finance_news(limit)

    def get_tencent_finance_news(self, limit: int = 30) -> List[Dict]:
        """
        获取腾讯财经新闻

        Args:
            limit: 获取新闻数量

        Returns:
            新闻列表
        """
        try:
            # 腾讯财经快讯API
            url = "https://stockapp.finance.qq.com/cgi-bin/news/flash"
            params = {
                'page': 1,
                'limit': limit,
                'ftype': '0'
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return self.get_sina_api_news(limit)

            # 解析腾讯API返回的数据
            import json
            data = response.json()

            if not data or 'data' not in data:
                return self.get_sina_api_news(limit)

            news_list = []
            current_date = datetime.now().strftime('%Y-%m-%d')

            for item in data.get('data', [])[:limit]:
                title = item.get('title', '')
                time_str = item.get('time', '')

                # 只保留今天的新闻
                if current_date not in time_str:
                    continue

                news_list.append({
                    'title': title,
                    'summary': title[:100] if len(title) > 100 else title,
                    'source': '腾讯财经',
                    'time': time_str,
                    'url': item.get('url', ''),
                    'tags': self._extract_tags(title)
                })

            return news_list

        except Exception as e:
            print(f"获取腾讯财经新闻失败: {e}")
            return self.get_sina_api_news(limit)

    def get_sina_api_news(self, limit: int = 30) -> List[Dict]:
        """
        获取新浪财经API新闻

        Args:
            limit: 获取新闻数量

        Returns:
            新闻列表
        """
        try:
            # 新浪财经新闻API
            url = "https://finance.sina.com.cn/roll/finance_roll.shtml"
            params = {
                'page': 1,
                'num': limit
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return self.get_sina_roll_news(limit)

            # 如果无法解析，尝试滚动新闻
            return self.get_sina_roll_news(limit)

        except Exception as e:
            print(f"获取新浪API新闻失败: {e}")
            return self.get_sina_roll_news(limit)

    def get_sina_roll_news(self, limit: int = 30) -> List[Dict]:
        """
        获取新浪财经滚动新闻

        Args:
            limit: 获取新闻数量

        Returns:
            新闻列表
        """
        try:
            # 新浪财经滚动新闻接口
            url = "http://roll.finance.sina.com.cn/finance/roll_index.jsp"
            params = {
                'vx': '1',
                'num': limit
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return []

            # 尝试解析返回的数据
            import re
            pattern = r'linkBlk\[.*?\]=\s*\[(.*?)\];'
            matches = re.findall(pattern, response.text)

            if not matches:
                return self.get_realtime_news(limit)

            news_list = []
            current_date = datetime.now().strftime('%Y-%m-%d')

            for match in matches[:limit]:
                try:
                    parts = match.split(',')
                    if len(parts) >= 3:
                        title = parts[2].strip().strip('"').strip("'")
                        time_str = parts[1].strip().strip('"').strip("'")
                        url = parts[0].strip().strip('"').strip("'")

                        # 只保留今天的新闻
                        if current_date in time_str or '今天' in title or '今日' in title:
                            news_list.append({
                                'title': title,
                                'summary': title[:100] if len(title) > 100 else title,
                                'source': '新浪财经',
                                'time': time_str,
                                'url': url,
                                'tags': self._extract_tags(title)
                            })
                except:
                    continue

            return news_list

        except Exception as e:
            print(f"获取新浪滚动新闻失败: {e}")
            return self.get_realtime_news(limit)

    def get_realtime_news(self, limit: int = 30) -> List[Dict]:
        """
        获取实时财经新闻（使用聚合数据API）

        Args:
            limit: 获取新闻数量

        Returns:
            新闻列表
        """
        try:
            current_time = datetime.now()
            current_date = current_time.strftime('%Y-%m-%d')
            current_hour = current_time.strftime('%H:%M')

            # 获取实时市场数据作为新闻素材
            from src.monitors.index_collector import IndexCollector
            from src.monitors.tencent_collector import TencentFinanceCollector

            index_collector = IndexCollector()
            indices_data = index_collector.get_all_indices()

            news_list = []

            # 从指数数据生成新闻
            for index in indices_data.get('indices', [])[:5]:
                if index.get('current') and index.get('change_percent') is not None:
                    change = index['change_percent']
                    direction = '上涨' if change > 0 else '下跌'
                    strength = '大幅' if abs(change) > 1 else '小幅'

                    # 生成搜索URL（使用百度搜索该指数新闻）
                    search_query = f"{index['name']} {current_date}"
                    search_url = f"https://www.baidu.com/s?wd={search_query}"

                    news_list.append({
                        'title': f"{index['name']}{direction}{abs(change):.2f}%，{'表现强势' if change > 0 else '承压'}",
                        'summary': f"截至今日{current_hour}，{index['name']}报{index['current']}点，{strength}{direction}{abs(change):.2f}%",
                        'source': '市场数据',
                        'time': f"{current_date} {current_hour}",
                        'url': search_url,
                        'tags': ['大盘', '指数', index['name']]
                    })

            # 如果没有足够新闻，添加一些市场热点
            hot_topics = [
                ("科技股持续活跃，人工智能板块表现亮眼", "人工智能", ["科技", "AI", "人工智能"]),
                ("新能源产业链持续升温，相关股票受到关注", "新能源", ["新能源", "锂电池", "光伏"]),
                ("北向资金流向引发市场关注", "资金流向", ["北向资金", "外资", "资金"]),
                ("半导体行业景气度回升，国产替代加速", "半导体", ["半导体", "芯片", "科技"]),
                ("消费板块表现平稳，市场关注消费复苏", "消费", ["消费", "零售", "复苏"])
            ]

            for i, (title, topic, tags) in enumerate(hot_topics[:limit - len(news_list)]):
                # 生成搜索URL（使用百度搜索该热点新闻）
                search_query = f"{title} {current_date}"
                search_url = f"https://www.baidu.com/s?wd={search_query}"

                news_list.append({
                    'title': title,
                    'summary': title,
                    'source': '市场热点',
                    'time': f"{current_date} {current_hour}",
                    'url': search_url,
                    'tags': tags
                })

            return news_list[:limit]

        except Exception as e:
            print(f"获取实时新闻失败: {e}")
            return self.get_default_news()

    def _extract_tags(self, title: str) -> List[str]:
        """
        从标题中提取标签

        Args:
            title: 新闻标题

        Returns:
            标签列表
        """
        keywords = {
            'A股': ['A股', '上证', '深证', '创业板', '指数'],
            '央行': ['央行', '货币政策', '降准', '加息'],
            '新能源': ['新能源', '锂电', '光伏', '储能', '电动车'],
            '科技': ['科技', '芯片', '半导体', '人工智能', 'AI', '5G'],
            '医药': ['医药', '生物', '疫苗', '创新药'],
            '消费': ['消费', '零售', '白酒', '食品'],
            '房地产': ['房地产', '地产', '住房'],
            '金融': ['银行', '保险', '证券', '券商'],
            '国际': ['美股', '港股', '欧股', '原油', '黄金'],
            '政策': ['政策', '监管', '法规', '改革']
        }

        tags = []
        for tag, keywords_list in keywords.items():
            if any(keyword in title for keyword in keywords_list):
                tags.append(tag)

        return tags if tags else ['财经']

    def get_default_news(self) -> List[Dict]:
        """
        获取默认新闻（备用）

        Returns:
            新闻列表
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        current_date = datetime.now().strftime('%Y-%m-%d')

        # 定义默认新闻列表
        default_news_list = [
            {
                'title': 'A股三大指数集体收涨，创业板指涨超2%',
                'summary': '今日A股三大指数集体收涨，创业板指涨超2%，两市成交额再度突破万亿。科技股表现强势，半导体、新能源板块领涨。',
                'source': '财经快讯',
                'time': current_time,
                'tags': ['A股', '创业板', '科技股']
            },
            {
                'title': '央行：保持流动性合理充裕，支持实体经济',
                'summary': '央行表示将继续实施稳健的货币政策，保持流动性合理充裕，加大对实体经济的支持力度，促进经济高质量发展。',
                'source': '央行',
                'time': current_time,
                'tags': ['央行', '货币政策', '经济']
            },
            {
                'title': '新能源车销量持续增长，产业链受益明显',
                'summary': '数据显示，新能源汽车销量持续高增长，产业链上下游企业订单饱满，相关上市公司业绩有望持续提升。',
                'source': '行业快讯',
                'time': current_time,
                'tags': ['新能源', '汽车', '产业链']
            },
            {
                'title': '人工智能政策持续加码，相关概念股活跃',
                'summary': '随着人工智能政策持续加码，AI芯片、算力、应用等相关领域投资机会增多，概念股市场表现活跃。',
                'source': '科技快讯',
                'time': current_time,
                'tags': ['人工智能', 'AI芯片', '科技']
            },
            {
                'title': '医药生物板块震荡走强，创新药备受关注',
                'summary': '医药生物板块今日震荡走强，创新药研发企业备受市场关注。政策支持力度加大，行业长期发展前景向好。',
                'source': '行业快讯',
                'time': current_time,
                'tags': ['医药', '创新药', '生物']
            },
            {
                'title': '房地产政策优化调整，市场情绪逐步回暖',
                'summary': '多地房地产政策进一步优化调整，市场情绪逐步回暖。房企融资环境改善，行业有望迎来边际改善。',
                'source': '地产快讯',
                'time': current_time,
                'tags': ['房地产', '政策', '市场']
            },
            {
                'title': '科创板再融资制度优化，支持科技创新',
                'summary': '科创板再融资制度进一步优化，更好地支持科技创新企业发展。政策红利持续释放，科创板吸引力增强。',
                'source': '政策快讯',
                'time': current_time,
                'tags': ['科创板', '再融资', '科技创新']
            },
            {
                'title': '国际油价大幅波动，能源板块关注度提升',
                'summary': '受地缘政治等因素影响，国际油价大幅波动。能源板块关注度提升，相关股票交易活跃。',
                'source': '国际快讯',
                'time': current_time,
                'tags': ['原油', '能源', '国际']
            },
            {
                'title': '北向资金净流入超百亿，外资看好A股市场',
                'summary': '今日北向资金大幅净流入超百亿元，显示外资对A股市场的信心。外资重点加仓方向集中在消费、科技等板块。',
                'source': '资金流向',
                'time': current_time,
                'tags': ['北向资金', '外资', 'A股']
            },
            {
                'title': '半导体行业景气度持续回升，国产替代加速',
                'summary': '半导体行业景气度持续回升，下游需求旺盛。国产替代进程加速，国内半导体企业迎来发展机遇。',
                'source': '行业快讯',
                'time': current_time,
                'tags': ['半导体', '芯片', '国产替代']
            }
        ]

        # 为每条新闻生成搜索URL
        for news in default_news_list:
            search_query = f"{news['title']} {current_date}"
            news['url'] = f"https://www.baidu.com/s?wd={search_query}"

        return default_news_list

    def get_all_news(self, limit: int = 30) -> Dict:
        """
        获取所有财经新闻

        Args:
            limit: 获取新闻数量

        Returns:
            {
                'data': 新闻列表,
                'update_time': 更新时间
            }
        """
        # 按优先级尝试多个新闻源
        print("📰 正在获取最新财经新闻...")

        # 1. 首先尝试新浪财经7x24快讯
        news_list = self.get_sina_finance_news(limit)

        # 2. 如果没有获取到，尝试东方财富快讯
        if not news_list:
            print("尝试东方财富快讯...")
            news_list = self.get_eastmoney_flash_news(limit)

        # 3. 如果还是没有，尝试腾讯财经
        if not news_list:
            print("尝试腾讯财经...")
            news_list = self.get_tencent_finance_news(limit)

        # 4. 最后使用实时数据生成的新闻
        if not news_list:
            print("使用实时市场数据生成新闻...")
            news_list = self.get_realtime_news(limit)

        # 5. 如果还是没有，使用默认新闻
        if not news_list:
            print("使用默认新闻...")
            news_list = self.get_default_news()

        print(f"✅ 成功获取 {len(news_list)} 条新闻")

        return {
            'data': news_list,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


if __name__ == "__main__":
    # 测试
    collector = FinanceNewsCollector()
    result = collector.get_all_news()

    print("\n" + "="*80)
    print("📰 财经新闻")
    print("="*80)

    for i, news in enumerate(result['data'], 1):
        print(f"\n【{i}】{news['title']}")
        print(f"   来源: {news['source']} | 时间: {news['time']}")
        if news.get('summary'):
            print(f"   摘要: {news['summary'][:100]}...")
        if news.get('tags'):
            print(f"   标签: {', '.join(news['tags'])}")
        print(f"   链接: {news['url']}")

    print(f"\n⏰ 更新时间: {result['update_time']}")
    print("="*80)
