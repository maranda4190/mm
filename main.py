import asyncio
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func, delete
import json
from typing import List
import signal
import sys
from datetime import datetime, timedelta

from database import init_database, get_async_session, AsyncSessionLocal, NewsArticle, TrendingTopic
from scraper import NewsFetcher
from analyzer import NewsAnalyzer
from utils import NewsScheduler
from config.settings import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="AI Investment News Monitor", version="1.0.0")

# Templates
templates = Jinja2Templates(directory="web/templates")

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# 路由定义
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/news")
async def get_news(
    limit: int = 50,
    category: str = None,
    min_importance: float = None,
    db: AsyncSession = Depends(get_async_session)
):
    """获取新闻列表"""
    try:
        query = select(NewsArticle).order_by(desc(NewsArticle.published_date))
        
        # 应用过滤器
        filters = []
        if category:
            filters.append(NewsArticle.category == category)
        if min_importance:
            filters.append(NewsArticle.importance_score >= min_importance)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        news_articles = result.scalars().all()
        
        # 转换为字典格式
        news_list = []
        for article in news_articles:
            news_dict = {
                'id': article.id,
                'title': article.title,
                'link': article.link,
                'summary': article.summary,
                'content': article.content,
                'published_date': article.published_date.isoformat() if article.published_date else None,
                'source': article.source,
                'source_url': article.source_url,
                'author': article.author,
                'tags': article.tags,
                'analysis': article.analysis,
                'relevance_score': article.relevance_score,
                'importance_score': article.importance_score,
                'overall_score': article.overall_score,
                'category': article.category,
                'urgency': article.urgency,
                'fetched_at': article.fetched_at.isoformat() if article.fetched_at else None,
                'analyzed_at': article.analyzed_at.isoformat() if article.analyzed_at else None
            }
            news_list.append(news_dict)
        
        return {"news": news_list, "count": len(news_list)}
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@app.get("/api/trending")
async def get_trending_topics(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    """获取热门话题"""
    try:
        query = select(TrendingTopic).order_by(desc(TrendingTopic.count)).limit(limit)
        result = await db.execute(query)
        trending_topics = result.scalars().all()
        
        topics_with_news = []
        for topic in trending_topics:
            # 获取相关新闻 - 简化查询
            news_query = select(NewsArticle).where(
                NewsArticle.title.ilike(f"%{topic.topic}%")
            ).order_by(desc(NewsArticle.published_date)).limit(3)
            
            news_result = await db.execute(news_query)
            latest_news = []
            
            for article in news_result.scalars():
                latest_news.append({
                    'id': article.id,
                    'title': article.title,
                    'published_date': article.published_date.isoformat() if article.published_date else None,
                    'link': article.link
                })
            
            topics_with_news.append({
                'topic': topic.topic,
                'category': topic.category,
                'count': topic.count,
                'latest_mention': topic.latest_mention.isoformat() if topic.latest_mention else None,
                'latest_news': latest_news
            })
        
        return {"topics": topics_with_news}
        
    except Exception as e:
        logger.error(f"Error fetching trending topics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trending topics")

@app.get("/api/stats")
async def get_statistics(db: AsyncSession = Depends(get_async_session)):
    """获取统计信息"""
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 今日新闻数量
        today_news_query = select(func.count(NewsArticle.id)).where(
            NewsArticle.published_date >= today
        )
        today_news_result = await db.execute(today_news_query)
        today_news_count = today_news_result.scalar() or 0
        
        # 投资事件数量
        investment_query = select(func.count(NewsArticle.id)).where(
            NewsArticle.category.in_(['funding', 'acquisition', 'ipo'])
        )
        investment_result = await db.execute(investment_query)
        investment_count = investment_result.scalar() or 0
        
        # 重要新闻数量
        important_query = select(func.count(NewsArticle.id)).where(
            NewsArticle.importance_score >= 0.7
        )
        important_result = await db.execute(important_query)
        important_count = important_result.scalar() or 0
        
        # 热门话题数量
        trending_query = select(func.count(TrendingTopic.id)).where(
            TrendingTopic.count >= 2
        )
        trending_result = await db.execute(trending_query)
        trending_count = trending_result.scalar() or 0
        
        return {
            "today_news": today_news_count,
            "investment_events": investment_count,
            "important_news": important_count,
            "trending_topics": trending_count
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@app.post("/api/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    """手动刷新新闻"""
    background_tasks.add_task(fetch_and_analyze_news_task)
    return {"message": "News refresh started"}

@app.get("/api/search")
async def search_news(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session)
):
    """搜索新闻"""
    try:
        query = select(NewsArticle).where(
            NewsArticle.title.ilike(f"%{q}%") |
            NewsArticle.summary.ilike(f"%{q}%")
        ).order_by(desc(NewsArticle.published_date)).limit(limit)
        
        result = await db.execute(query)
        news_articles = result.scalars().all()
        
        news_list = []
        for article in news_articles:
            news_dict = {
                'id': article.id,
                'title': article.title,
                'link': article.link,
                'summary': article.summary,
                'published_date': article.published_date.isoformat() if article.published_date else None,
                'source': article.source,
                'analysis': article.analysis,
                'relevance_score': article.relevance_score,
                'importance_score': article.importance_score,
                'category': article.category,
                'urgency': article.urgency
            }
            news_list.append(news_dict)
        
        return {"news": news_list, "query": q, "count": len(news_list)}
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to search news")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "status": "running",
        "scheduler_active": scheduler.is_running if scheduler else False,
        "websocket_connections": len(manager.active_connections),
        "update_interval_minutes": settings.NEWS_UPDATE_INTERVAL,
        "last_check": datetime.utcnow().isoformat()
    }

@app.post("/api/trigger-update")
async def trigger_news_update():
    """手动触发新闻更新"""
    try:
        await fetch_and_analyze_news_task()
        return {"message": "News update triggered successfully"}
    except Exception as e:
        logger.error(f"Error triggering update: {e}")
        return {"error": "Failed to trigger update"}

# 全局变量
scheduler = None

async def fetch_and_analyze_news_task():
    """获取并分析新闻的任务"""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting news fetch and analysis")
            
            # 获取新闻
            async with NewsFetcher() as fetcher:
                news_list = await fetcher.fetch_all_news()
            
            if not news_list:
                logger.warning("No news fetched")
                return
            
            # 分析新闻
            analyzer = NewsAnalyzer()
            analyzed_news = await analyzer.analyze_news_batch(news_list)
            
            # 保存到数据库
            saved_count = 0
            for news_data in analyzed_news:
                try:
                    # 检查是否已存在
                    existing_query = select(NewsArticle).where(NewsArticle.link == news_data['link'])
                    existing_result = await db.execute(existing_query)
                    existing_article = existing_result.scalar_one_or_none()
                    
                    if existing_article:
                        continue  # 跳过已存在的新闻
                    
                    # 创建新闻记录
                    analysis = news_data.get('analysis', {})
                    article = NewsArticle(
                        title=news_data.get('title', ''),
                        link=news_data.get('link', ''),
                        summary=news_data.get('summary', ''),
                        content=news_data.get('content', ''),
                        published_date=news_data.get('published_date'),
                        source=news_data.get('source', ''),
                        source_url=news_data.get('source_url', ''),
                        author=news_data.get('author', ''),
                        tags=news_data.get('tags', []),
                        analysis=analysis,
                        relevance_score=analysis.get('relevance_score', 0.0),
                        importance_score=analysis.get('importance_score', 0.0),
                        overall_score=analysis.get('overall_score', 0.0),
                        category=analysis.get('category', 'general'),
                        urgency=analysis.get('urgency', 'low'),
                        analyzed_at=datetime.utcnow(),
                        is_processed=True
                    )
                    
                    db.add(article)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving news article: {e}")
                    continue
            
            await db.commit()
            
            # 更新热门话题
            await update_trending_topics(analyzed_news, db)
            
            # 广播更新通知
            update_message = {
                "type": "news_update",
                "message": f"已更新 {saved_count} 条新闻",
                "timestamp": datetime.utcnow().isoformat()
            }
            await manager.broadcast(json.dumps(update_message))
            
            logger.info(f"Successfully processed {saved_count} new articles")
            
        except Exception as e:
            logger.error(f"Error in fetch_and_analyze_news: {e}")
            await db.rollback()

async def update_trending_topics(news_list: List[dict], db: AsyncSession):
    """更新热门话题"""
    try:
        analyzer = NewsAnalyzer()
        trending_topics = await analyzer.get_trending_topics(news_list)
        
        for topic_data in trending_topics:
            # 查找现有话题
            existing_query = select(TrendingTopic).where(
                TrendingTopic.topic == topic_data['topic']
            )
            result = await db.execute(existing_query)
            existing_topic = result.scalar_one_or_none()
            
            if existing_topic:
                # 更新现有话题
                existing_topic.count = topic_data['count']
                existing_topic.latest_mention = datetime.utcnow()
            else:
                # 创建新话题
                new_topic = TrendingTopic(
                    topic=topic_data['topic'],
                    category=topic_data['category'],
                    count=topic_data['count'],
                    latest_mention=datetime.utcnow()
                )
                db.add(new_topic)
        
        await db.commit()
        logger.info("Trending topics updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating trending topics: {e}")
        await db.rollback()

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global scheduler
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("Database initialized successfully")
        
        # 初始获取新闻
        await fetch_and_analyze_news_task()
        logger.info("Initial news fetch completed")
        
        # 启动调度器
        scheduler = NewsScheduler(fetch_and_analyze_news_task)
        scheduler.start()
        logger.info("News scheduler started")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global scheduler
    
    if scheduler:
        scheduler.stop()
        logger.info("News scheduler stopped")
    
    logger.info("Application shutdown completed")

# 信号处理
def signal_handler(signum, frame):
    """处理系统信号"""
    logger.info(f"Received signal {signum}, shutting down...")
    if scheduler:
        scheduler.stop()
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_server():
    """运行服务器"""
    logger.info(f"Starting AI Investment News Monitor on {settings.HOST}:{settings.PORT}")
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查必要的配置
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set. AI analysis will be disabled.")
    
    logger.info("=" * 60)
    logger.info("AI Investment News Monitor")
    logger.info("=" * 60)
    logger.info(f"Update interval: {settings.NEWS_UPDATE_INTERVAL} minutes")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info("=" * 60)
    
    run_server()