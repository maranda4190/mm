from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    link = Column(String(1000), unique=True, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    published_date = Column(DateTime, index=True)
    source = Column(String(100), index=True)
    source_url = Column(String(500))
    author = Column(String(200))
    tags = Column(JSON)
    
    # 分析结果
    analysis = Column(JSON)
    relevance_score = Column(Float, default=0.0, index=True)
    importance_score = Column(Float, default=0.0, index=True)
    overall_score = Column(Float, default=0.0, index=True)
    category = Column(String(50), index=True)
    urgency = Column(String(20), default='low', index=True)
    
    # 元数据
    fetched_at = Column(DateTime, default=func.now())
    analyzed_at = Column(DateTime)
    is_processed = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', source='{self.source}')>"

class TrendingTopic(Base):
    __tablename__ = "trending_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # 'company', 'topic', 'investor'
    count = Column(Integer, default=0)
    latest_mention = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TrendingTopic(topic='{self.topic}', count={self.count})>"

class UserAlert(Base):
    __tablename__ = "user_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    keywords = Column(JSON)  # 关键词列表
    min_importance = Column(Float, default=0.5)
    categories = Column(JSON)  # 关注的分类
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_triggered = Column(DateTime)
    
    def __repr__(self):
        return f"<UserAlert(keywords={self.keywords}, active={self.is_active})>"