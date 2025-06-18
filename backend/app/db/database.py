# 数据库连接
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import os

from app.core.config import settings
from logging import Logger

# 获取logger
logger = logging.getLogger(__name__)

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URI_ASYNC,
    echo=settings.DB_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={
        "timeout": settings.DB_CONNECT_TIMEOUT,
        "command_timeout": settings.DB_COMMAND_TIMEOUT,
        "server_settings": {
            "statement_timeout": str(settings.DB_STATEMENT_TIMEOUT),
            "timezone": "UTC"
        },
        "ssl": settings.DB_SSL_MODE != "disable"
    }
)

# 创建会话工厂
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 创建基类
Base = declarative_base()

# 依赖函数，提供数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库会话异常: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

# 使用异步上下文管理器获取会话
@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话
    
    Yields:
        异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 仓库依赖项
async def get_repository(repo_type, session: AsyncSession):
    """
    获取仓库实例的依赖工厂
    
    Args:
        repo_type: 仓库类型
        session: 异步数据库会话
        
    Returns:
        仓库实例
    """
    return repo_type(session)

# 数据库健康检查
async def check_database_connection() -> bool:
    """检查数据库连接是否正常"""
    try:
        # 尝试建立连接并执行简单查询
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()  # 等待查询结果
            await conn.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False