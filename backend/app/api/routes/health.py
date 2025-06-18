from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.database import get_db, check_database_connection

router = APIRouter()

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查"""
    db_status = await check_database_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }

@router.get("/db")
async def database_health(db: AsyncSession = Depends(get_db)):
    """数据库健康检查"""
    try:
        is_connected = await check_database_connection()
        return {
            "database": "healthy" if is_connected else "unhealthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }