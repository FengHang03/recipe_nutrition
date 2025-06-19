# Linux环境配置 - 连接到Windows上通过ngrok暴露的PostgreSQL数据库
import os
from app.core.config import Settings

class LinuxSettings(Settings):
    """Linux环境专用配置 - 连接到ngrok暴露的Windows PostgreSQL"""
    
    # 覆盖数据库配置
    POSTGRES_SERVER: str = "0.tcp.us-cal-1.ngrok.io"
    POSTGRES_USER: str = "postgres" 
    POSTGRES_PASSWORD: str = "1997"
    POSTGRES_DB: str = "pet_diet_db"
    POSTGRES_PORT: str = "13775"
    
    # 环境设置
    ENVIRONMENT: str = "production"
    
    # 数据库SSL配置（ngrok连接禁用SSL）
    DB_SSL_MODE: str = "disable"
    
    # 优化连接池配置（适用于远程连接）
    DB_POOL_SIZE: int = 5  # 减少连接池大小（远程连接）
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 60  # 增加超时时间
    DB_POOL_RECYCLE: int = 1800  # 缩短连接回收时间
    DB_CONNECT_TIMEOUT: int = 30  # 增加连接超时
    DB_COMMAND_TIMEOUT: int = 120  # 增加命令超时
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False
    
    class Config:
        case_sensitive = True

# 创建Linux专用设置对象
linux_settings = LinuxSettings() 