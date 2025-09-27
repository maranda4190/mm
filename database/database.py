from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import logging

from config.settings import settings
from .models import Base

logger = logging.getLogger(__name__)

# 同步引擎（用于初始化）
sync_engine = create_engine(
    settings.DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://') if 'postgresql' in settings.DATABASE_URL else settings.DATABASE_URL,
    echo=False
)

# 异步引擎
if 'postgresql' in settings.DATABASE_URL:
    async_database_url = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
elif 'sqlite' in settings.DATABASE_URL:
    async_database_url = settings.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
else:
    async_database_url = settings.DATABASE_URL

async_engine = create_async_engine(
    async_database_url,
    echo=False,
    future=True
)

# 异步会话
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

def create_tables():
    """创建数据库表"""
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_database():
    """初始化数据库"""
    create_tables()
    logger.info("Database initialized")