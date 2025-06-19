# Linux环境数据库连接 - 连接到Windows ngrok PostgreSQL
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import os

from config_linux import linux_settings as settings
from logging import Logger

# 获取logger
logger = logging.getLogger(__name__)

# 创建异步引擎 - 针对ngrok连接优化
engine = create_async_engine(
    settings.DATABASE_URI_ASYNC,
    echo=settings.DB_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # 重要：对于ngrok连接，启用连接预检查
    connect_args={
        "timeout": settings.DB_CONNECT_TIMEOUT,
        "command_timeout": settings.DB_COMMAND_TIMEOUT,
        "server_settings": {
            "statement_timeout": str(settings.DB_STATEMENT_TIMEOUT),
            "timezone": "UTC"
        },
        # ngrok连接禁用SSL
        "ssl": False
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

# 数据库健康检查 - 针对ngrok连接优化
async def check_database_connection() -> bool:
    """检查数据库连接是否正常 - 适配ngrok连接"""
    try:
        logger.info(f"正在检查数据库连接: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
        
        # 尝试建立连接并执行简单查询
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test_connection"))
            row = result.fetchone()
            await conn.close()
            
            if row and row[0] == 1:
                logger.info("✅ 数据库连接测试成功")
                return True
            else:
                logger.error("❌ 数据库连接测试失败：查询结果异常")
                return False
                
    except Exception as e:
        logger.error(f"❌ 数据库连接检查失败: {str(e)}")
        logger.error("请检查：")
        logger.error("1. Windows上的ngrok是否正在运行")
        logger.error("2. ngrok配置: tcp://0.tcp.us-cal-1.ngrok.io:13775 -> localhost:5433")
        logger.error("3. PostgreSQL服务是否启动")
        logger.error("4. 网络连接是否正常")
        return False 