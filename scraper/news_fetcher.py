import asyncio
import aiohttp
import feedparser
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

from config.settings import settings

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_all_news(self) -> List[Dict]:
        """获取所有新闻源的新闻"""
        all_news = []
        
        tasks = []
        for source in settings.NEWS_SOURCES:
            tasks.append(self._fetch_from_source(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching news: {result}")
                continue
            if result:
                all_news.extend(result)
        
        # 按时间排序并去重
        all_news = self._deduplicate_news(all_news)
        all_news.sort(key=lambda x: x.get('published_date', datetime.min), reverse=True)
        
        return all_news[:settings.MAX_NEWS_PER_FETCH]
    
    async def _fetch_from_source(self, source: Dict) -> List[Dict]:
        """从单个新闻源获取新闻"""
        try:
            logger.info(f"Fetching news from {source['name']}")
            
            async with self.session.get(source['rss_url']) as response:
                content = await response.text()
                
            feed = feedparser.parse(content)
            news_items = []
            
            for entry in feed.entries:
                # 检查是否包含AI和投资相关关键词
                if self._is_relevant_news(entry):
                    news_item = await self._parse_news_entry(entry, source)
                    if news_item:
                        news_items.append(news_item)
            
            logger.info(f"Found {len(news_items)} relevant news items from {source['name']}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching from {source['name']}: {e}")
            return []
    
    def _is_relevant_news(self, entry) -> bool:
        """检查新闻是否与AI投资相关"""
        title = getattr(entry, 'title', '').lower()
        summary = getattr(entry, 'summary', '').lower()
        content = f"{title} {summary}"
        
        # 检查AI关键词
        has_ai_keyword = any(keyword.lower() in content for keyword in settings.AI_KEYWORDS)
        
        # 检查投资关键词
        has_investment_keyword = any(keyword.lower() in content for keyword in settings.INVESTMENT_KEYWORDS)
        
        return has_ai_keyword and has_investment_keyword
    
    async def _parse_news_entry(self, entry, source: Dict) -> Optional[Dict]:
        """解析新闻条目"""
        try:
            # 获取完整内容
            full_content = await self._fetch_full_content(entry.link)
            
            published_date = self._parse_date(entry)
            
            return {
                'title': getattr(entry, 'title', ''),
                'link': getattr(entry, 'link', ''),
                'summary': getattr(entry, 'summary', ''),
                'content': full_content,
                'published_date': published_date,
                'source': source['name'],
                'source_url': source['base_url'],
                'author': getattr(entry, 'author', ''),
                'tags': [tag.term for tag in getattr(entry, 'tags', [])],
                'fetched_at': datetime.now(timezone.utc)
            }
        except Exception as e:
            logger.error(f"Error parsing news entry: {e}")
            return None
    
    async def _fetch_full_content(self, url: str) -> str:
        """获取新闻的完整内容"""
        try:
            async with self.session.get(url) as response:
                html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试多种内容选择器
            content_selectors = [
                'article',
                '.post-content',
                '.article-content',
                '.entry-content',
                '.content',
                'main',
                '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([el.get_text(strip=True) for el in elements])
                    break
            
            if not content:
                # 后备方案：获取所有p标签内容
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # 清理内容
            content = re.sub(r'\s+', ' ', content).strip()
            return content[:5000]  # 限制长度
            
        except Exception as e:
            logger.warning(f"Could not fetch full content for {url}: {e}")
            return ""
    
    def _parse_date(self, entry) -> datetime:
        """解析发布日期"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                return datetime.now(timezone.utc)
        except:
            return datetime.now(timezone.utc)
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """去重新闻"""
        seen_urls = set()
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            url = news.get('link', '')
            title = news.get('title', '').lower().strip()
            
            # 基于URL和标题去重
            if url not in seen_urls and title not in seen_titles:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news

    async def search_news_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """根据关键词搜索新闻"""
        all_news = await self.fetch_all_news()
        
        filtered_news = []
        for news in all_news:
            content = f"{news.get('title', '')} {news.get('summary', '')} {news.get('content', '')}".lower()
            
            if any(keyword.lower() in content for keyword in keywords):
                filtered_news.append(news)
        
        return filtered_news