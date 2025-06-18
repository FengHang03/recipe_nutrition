from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from app.core.config import settings
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
    
    # 检查数据库连接
    try:
        is_connected = await check_database_connection()
        if is_connected:
            logger.info("数据库连接成功")
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
    description="基于AAFCO营养标准的专业宠物鲜食配方生成系统",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# CORS配置 - 支持局域网访问
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.12.1:3000",  # 添加局域网IP
    "http://192.168.1.*:3000",   # 支持常见局域网段
    "http://10.0.0.*:3000",      # 支持其他局域网段
] + settings.CORS_ORIGINS

# 开发环境允许所有origin（生产环境需要更严格的控制）
if settings.ENVIRONMENT == "development":
    allowed_origins.append("*")

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
        "message": f"欢迎使用 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.ENVIRONMENT == "development" else "disabled"
    }
    
def quick_test():
    """快速功能测试（不需要数据库）"""
    
    print("🚀 简化版宠物营养系统 - 快速测试")
    print("="*60)
    
    # 测试能量计算
    test_energy_calculations()
    
    print(f"\n🎯 系统核心功能:")
    print("✅ 生理状态支持: intact, neutered, pregnant, lactating")
    print("✅ 能量需求计算: 基于RER + 多重系数")
    print("✅ AAFCO标准集成: 犬猫不同生命阶段")
    print("✅ 线性规划优化: 能量需求 + 营养标准")
    print("✅ 食物分类约束: 6大类食物比例控制")
    
    print(f"\n📋 待完善功能:")
    print("⏳ 真实食材成本数据")
    print("⏳ 更多AAFCO营养素标准")
    print("⏳ 用户界面和可视化")
    print("⏳ 配方保存和历史记录")

if __name__ == "__main__":
    # 运行快速测试
    # quick_test()
    
    # 如果有数据库，运行完整示例
    example_usage()