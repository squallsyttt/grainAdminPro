"""
数据库连接管理模块
提供 SQLAlchemy 异步数据库引擎和会话工厂
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.core.config import settings

# 创建异步数据库引擎
# 将 postgresql:// 替换为 postgresql+asyncpg://
database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,  # 开发环境打印 SQL
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建 ORM Base 类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖注入
    用于 FastAPI 路由函数的依赖项
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()