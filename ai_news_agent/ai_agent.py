"""
AI Agent核心逻辑
整合新闻获取、分析和实时更新功能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from dataclasses import dataclass, asdict
import schedule
import time
from threading import Thread

from news_fetcher import NewsFetcher
from ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """新闻条目数据类"""
    id: str
    title: str
    description: str
    link: str
    source: str
    published: str
    analyzed: bool = False
    analysis: Optional[Dict] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class AIInvestmentNewsAgent:
    """AI投资新闻Agent"""
    
    def __init__(self, openai_api_key: str, news_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.news_api_key = news_api_key
        self.analyzer = AIAnalyzer(openai_api_key)
        
        # 存储新闻数据
        self.news_items: List[NewsItem] = []
        self.analyses: List[Dict] = []
        
        # 配置
        self.update_interval = int(os.getenv('UPDATE_INTERVAL', 30))  # 分钟
        self.max_news_items = 100
        
        # 状态
        self.is_running = False
        self.last_update = None
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def fetch_and_analyze_news(self) -> Dict:
        """获取并分析新闻"""
        logger.info("开始获取和分析新闻...")
        
        try:
            # 获取新闻
            async with NewsFetcher() as fetcher:
                raw_news = await fetcher.fetch_all_news(self.news_api_key)
            
            logger.info(f"获取到 {len(raw_news)} 条新闻")
            
            # 转换为NewsItem对象
            new_items = []
            for i, news in enumerate(raw_news):
                news_item = NewsItem(
                    id=f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    title=news['title'],
                    description=news.get('description', ''),
                    link=news['link'],
                    source=news.get('source', 'Unknown'),
                    published=news.get('published', ''),
                )
                new_items.append(news_item)
            
            # 分析新闻
            logger.info("开始AI分析...")
            # 将NewsItem对象转换为字典格式
            news_dicts = []
            for item in new_items:
                news_dict = {
                    'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'link': item.link,
                    'source': item.source,
                    'published': item.published
                }
                news_dicts.append(news_dict)
            
            analyses = await self.analyzer.analyze_news_batch(news_dicts)
            
            # 更新分析结果
            for item, analysis in zip(new_items, analyses):
                item.analyzed = True
                item.analysis = analysis['analysis']
            
            # 更新存储
            self.news_items = new_items[:self.max_news_items]
            self.analyses = analyses
            self.last_update = datetime.now()
            
            logger.info(f"完成分析，共处理 {len(new_items)} 条新闻")
            
            return {
                'success': True,
                'news_count': len(new_items),
                'analyzed_count': len(analyses),
                'last_update': self.last_update.isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取和分析新闻失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
    
    def get_news_summary(self) -> Dict:
        """获取新闻摘要"""
        if not self.news_items:
            return {
                'total_news': 0,
                'analyzed_news': 0,
                'last_update': None,
                'market_summary': '暂无数据'
            }
        
        analyzed_count = sum(1 for item in self.news_items if item.analyzed)
        market_summary = self.analyzer.generate_market_summary(self.analyses)
        
        return {
            'total_news': len(self.news_items),
            'analyzed_news': analyzed_count,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'market_summary': market_summary
        }
    
    def get_news_by_sentiment(self, sentiment: str) -> List[Dict]:
        """根据情绪获取新闻"""
        filtered_news = []
        
        for item in self.news_items:
            if item.analyzed and item.analysis:
                if item.analysis.get('sentiment') == sentiment:
                    filtered_news.append({
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'link': item.link,
                        'source': item.source,
                        'published': item.published,
                        'analysis': item.analysis
                    })
        
        return filtered_news
    
    def get_news_by_impact(self, impact: str) -> List[Dict]:
        """根据影响程度获取新闻"""
        filtered_news = []
        
        for item in self.news_items:
            if item.analyzed and item.analysis:
                if item.analysis.get('impact') == impact:
                    filtered_news.append({
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'link': item.link,
                        'source': item.source,
                        'published': item.published,
                        'analysis': item.analysis
                    })
        
        return filtered_news
    
    def get_all_news(self) -> List[Dict]:
        """获取所有新闻"""
        return [
            {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'link': item.link,
                'source': item.source,
                'published': item.published,
                'analyzed': item.analyzed,
                'analysis': item.analysis,
                'created_at': item.created_at
            }
            for item in self.news_items
        ]
    
    def start_scheduled_updates(self):
        """启动定时更新"""
        if self.is_running:
            logger.warning("定时更新已在运行中")
            return
        
        self.is_running = True
        
        # 设置定时任务
        schedule.every(self.update_interval).minutes.do(
            lambda: asyncio.run(self.fetch_and_analyze_news())
        )
        
        # 在后台线程中运行调度器
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info(f"定时更新已启动，间隔: {self.update_interval} 分钟")
    
    def stop_scheduled_updates(self):
        """停止定时更新"""
        self.is_running = False
        schedule.clear()
        logger.info("定时更新已停止")
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'is_running': self.is_running,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'total_news': len(self.news_items),
            'analyzed_news': sum(1 for item in self.news_items if item.analyzed),
            'update_interval': self.update_interval,
            'openai_configured': bool(self.openai_api_key),
            'news_api_configured': bool(self.news_api_key)
        }
    
    async def initialize(self):
        """初始化Agent"""
        logger.info("初始化AI投资新闻Agent...")
        
        # 首次获取新闻
        result = await self.fetch_and_analyze_news()
        
        if result['success']:
            logger.info("Agent初始化成功")
        else:
            logger.error(f"Agent初始化失败: {result.get('error', 'Unknown error')}")
        
        return result