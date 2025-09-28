import asyncio
import schedule
import logging
from datetime import datetime
from typing import Callable

from config.settings import settings

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self, fetch_function: Callable):
        self.fetch_function = fetch_function
        self.is_running = False
        self.scheduler_task = None
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # 设置定时任务
        schedule.every(settings.NEWS_UPDATE_INTERVAL).minutes.do(
            self._schedule_fetch
        )
        
        # 每小时清理旧的热门话题
        schedule.every().hour.do(self._cleanup_trending_topics)
        
        # 每天清理旧新闻（保留30天）
        schedule.every().day.at("02:00").do(self._cleanup_old_news)
        
        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info(f"News scheduler started with {settings.NEWS_UPDATE_INTERVAL} minute intervals")
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
        schedule.clear()
        logger.info("News scheduler stopped")
    
    async def _run_scheduler(self):
        """运行调度器的主循环"""
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    def _schedule_fetch(self):
        """调度新闻获取任务"""
        asyncio.create_task(self._async_fetch())
    
    async def _async_fetch(self):
        """异步执行新闻获取"""
        try:
            logger.info("Scheduled news fetch started")
            await self.fetch_function()
            logger.info("Scheduled news fetch completed")
        except Exception as e:
            logger.error(f"Scheduled fetch error: {e}")
    
    def _cleanup_trending_topics(self):
        """清理过期的热门话题"""
        asyncio.create_task(self._async_cleanup_trending())
    
    async def _async_cleanup_trending(self):
        """异步清理热门话题"""
        try:
            from database import get_async_session, TrendingTopic
            from sqlalchemy import delete
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            async with get_async_session() as db:
                # 删除7天前的话题
                delete_query = delete(TrendingTopic).where(
                    TrendingTopic.latest_mention < cutoff_date
                )
                await db.execute(delete_query)
                await db.commit()
                
            logger.info("Trending topics cleanup completed")
            
        except Exception as e:
            logger.error(f"Trending topics cleanup error: {e}")
    
    def _cleanup_old_news(self):
        """清理旧新闻"""
        asyncio.create_task(self._async_cleanup_news())
    
    async def _async_cleanup_news(self):
        """异步清理旧新闻"""
        try:
            from database import get_async_session, NewsArticle
            from sqlalchemy import delete
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            async with get_async_session() as db:
                # 删除30天前的新闻（保留重要新闻）
                delete_query = delete(NewsArticle).where(
                    (NewsArticle.published_date < cutoff_date) &
                    (NewsArticle.importance_score < 0.8)  # 保留高重要性新闻
                )
                result = await db.execute(delete_query)
                await db.commit()
                
                deleted_count = result.rowcount
                logger.info(f"Cleaned up {deleted_count} old news articles")
                
        except Exception as e:
            logger.error(f"News cleanup error: {e}")