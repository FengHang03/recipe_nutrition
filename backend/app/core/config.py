# 应用配置
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union, Dict, Any
from pathlib import Path

class Settings(BaseSettings):
    """应用配置设置"""
    
    # API设置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pet Fresh Diet API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # 数据库配置 - 主库（读写）
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "1997")  # 改为普通字符串
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "pet_diet_db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5433")
    
    # 数据库配置 - 从库（只读）
    POSTGRES_REPLICA_SERVERS: List[str] = []

    @field_validator("POSTGRES_REPLICA_SERVERS")
    def assemble_replica_servers(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    # Debug模式下显示SQL
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "False").lower() == "true"

    # 数据库连接池配置（企业级优化）
    DB_POOL_SIZE: int = 20  # 连接池大小
    DB_MAX_OVERFLOW: int = 40  # 最大溢出连接数
    DB_POOL_TIMEOUT: int = 30  # 连接超时（秒）
    DB_POOL_RECYCLE: int = 3600  # 连接回收时间（秒）
    DB_POOL_PRE_PING: bool = True  # 连接健康检查
    DB_ECHO: bool = False  # SQL日志（生产环境必须为False）
    DB_CONNECT_TIMEOUT: int = 10  # 连接超时
    DB_COMMAND_TIMEOUT: int = 30  # 命令执行超时
    DB_STATEMENT_TIMEOUT: int = 300000  # 语句超时（毫秒）

    # 数据库SSL配置（生产环境）
    DB_SSL_MODE: str = "disable"  # 开发环境禁用 SSL
    DB_SSL_CERT_PATH: Optional[str] = None
    DB_SSL_KEY_PATH: Optional[str] = None
    DB_SSL_CA_PATH: Optional[str] = None

    # 数据库连接字符串
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """获取同步数据库URL"""
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    SQLALCHEMY_REPLICA_URI: Optional[List[str]] = None
    
    @property
    def DATABASE_URI(self) -> str:
        """获取数据库URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URI_ASYNC(self) -> str:
        """获取异步数据库URL"""
        # 优先使用环境变量中的DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
        
        # 否则使用单独的配置项构建
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # LLM设置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # 从环境变量获取，不硬编码
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # 安全
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "c00100de7ce55d217c051c4e2c3e0909b5fdf7bf6349766fac35d0a9311c8a8b"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    
    # CORS
    CORS_ORIGINS: List[str] = []

    @field_validator("CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # 日志
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置对象
settings = Settings()