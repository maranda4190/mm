"""
新闻数据获取模块
负责从多个新闻源获取AI投资相关新闻
"""

import asyncio
import aiohttp
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class NewsFetcher:
    """新闻获取器"""
    
    def __init__(self):
        self.session = None
        self.ai_keywords = [
            "artificial intelligence", "AI", "machine learning", "ML", 
            "deep learning", "neural network", "chatbot", "GPT", "LLM",
            "人工智能", "机器学习", "深度学习", "神经网络"
        ]
        
        # 投资相关关键词
        self.investment_keywords = [
            "investment", "funding", "fund", "venture", "capital", "IPO", 
            "acquisition", "merger", "valuation", "startup", "unicorn",
            "投资", "融资", "基金", "风投", "上市", "收购", "估值", "创业公司"
        ]
        
        # RSS新闻源
        self.rss_feeds = [
            "https://techcrunch.com/feed/",
            "https://venturebeat.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://feeds.feedburner.com/oreilly/radar",
            "https://www.wired.com/feed/rss",
            "https://feeds.feedburner.com/TechCrunch/",
        ]
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def is_ai_investment_related(self, title: str, description: str = "") -> bool:
        """判断新闻是否与AI投资相关"""
        text = (title + " " + description).lower()
        
        has_ai = any(keyword.lower() in text for keyword in self.ai_keywords)
        has_investment = any(keyword.lower() in text for keyword in self.investment_keywords)
        
        return has_ai and has_investment
    
    async def fetch_rss_news(self) -> List[Dict]:
        """从RSS源获取新闻"""
        news_items = []
        
        for feed_url in self.rss_feeds:
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:10]:  # 限制每个源最多10条
                            if self.is_ai_investment_related(entry.title, entry.get('summary', '')):
                                news_item = {
                                    'title': entry.title,
                                    'description': entry.get('summary', ''),
                                    'link': entry.link,
                                    'published': entry.get('published_parsed', datetime.now().timetuple()),
                                    'source': feed.feed.get('title', 'Unknown'),
                                    'source_url': feed_url
                                }
                                news_items.append(news_item)
                                
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        
        return news_items
    
    async def fetch_news_api_news(self, api_key: Optional[str] = None) -> List[Dict]:
        """从News API获取新闻"""
        if not api_key:
            return []
        
        news_items = []
        
        try:
            # 构建查询参数
            params = {
                'apiKey': api_key,
                'q': 'artificial intelligence investment OR AI funding OR machine learning startup',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 50
            }
            
            async with self.session.get(
                'https://newsapi.org/v2/everything',
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for article in data.get('articles', []):
                        if self.is_ai_investment_related(article['title'], article.get('description', '')):
                            news_item = {
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'link': article['url'],
                                'published': article.get('publishedAt', ''),
                                'source': article['source']['name'],
                                'source_url': article['url']
                            }
                            news_items.append(news_item)
                            
        except Exception as e:
            logger.error(f"Error fetching News API: {e}")
        
        return news_items
    
    async def fetch_all_news(self, news_api_key: Optional[str] = None) -> List[Dict]:
        """获取所有新闻源的数据"""
        tasks = [
            self.fetch_rss_news(),
            self.fetch_news_api_news(news_api_key)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in news fetching: {result}")
        
        # 去重和排序
        unique_news = self._deduplicate_news(all_news)
        return sorted(unique_news, key=lambda x: x.get('published', ''), reverse=True)
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """去重新闻"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title_lower = news['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_news.append(news)
        
        return unique_news
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        # 移除HTML标签
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        
        # 移除多余的空白字符
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text