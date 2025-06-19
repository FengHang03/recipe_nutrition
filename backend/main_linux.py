from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# 使用Linux专用配置
from config_linux import linux_settings as settings
from app.db.database import get_db, check_database_connection
from app.api.routes import pets, recipes, health
from app.db.models import Base
from app.db.database import engine

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动事件
    logger.info(f"启动 {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"数据库连接: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    
    # 检查数据库连接
    try:
        is_connected = await check_database_connection()
        if is_connected:
            logger.info("数据库连接成功 - 通过ngrok连接到Windows PostgreSQL")
        else:
            logger.error("数据库连接失败")
    except Exception as e:
        logger.error(f"数据库连接检查失败: {e}")
    
    yield
    
    # 关闭事件
    logger.info("应用正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于AAFCO营养标准的专业宠物鲜食配方生成系统 (Linux部署版)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS配置 - Linux环境允许更多源
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://d130-113-87-81-162.ngrok-free.app",  # ngrok前端域名
    "https://a92e-113-87-81-162.ngrok-free.app",  # ngrok后端域名
    "*"  # Linux环境允许所有来源（如需要更严格控制可修改）
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(health.router, prefix=f"{settings.API_V1_STR}/health", tags=["健康检查"])
app.include_router(pets.router, prefix=f"{settings.API_V1_STR}/pets", tags=["宠物管理"])
app.include_router(recipes.router, prefix=f"{settings.API_V1_STR}/recipes", tags=["配方生成"])

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """全局HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "内部服务器错误",
            "timestamp": datetime.now().isoformat()
        }
    )

# 根路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "message": f"欢迎使用 {settings.PROJECT_NAME} (Linux部署版)",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Linux环境启动配置
    uvicorn.run(
        "main_linux:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 生产环境关闭自动重载
        log_level="info"
    ) 