#!/usr/bin/env python3
"""
数据库连接测试脚本
用于验证.env文件中的数据库配置是否正确
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_database_connection():
    """测试数据库连接"""
    
    print("🔍 数据库连接测试")
    print("=" * 50)
    
    # 显示配置信息
    print(f"📋 配置信息:")
    print(f"   数据库URL: {settings.DATABASE_URI_ASYNC}")
    print(f"   服务器: {settings.POSTGRES_SERVER}")
    print(f"   端口: {settings.POSTGRES_PORT}")
    print(f"   用户: {settings.POSTGRES_USER}")
    print(f"   数据库: {settings.POSTGRES_DB}")
    print()
    
    # 检查.env文件
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"✅ 找到.env文件: {env_path}")
        with open(env_path, 'r') as f:
            env_content = f.read()
            if 'DATABASE_URL' in env_content:
                print("✅ 检测到DATABASE_URL配置")
            else:
                print("ℹ️ 未检测到DATABASE_URL，使用单独的配置项")
    else:
        print("⚠️ 未找到.env文件")
    
    print()
    
    # 测试连接
    print("🔌 测试数据库连接...")
    
    try:
        # 创建异步引擎
        engine = create_async_engine(
            settings.DATABASE_URI_ASYNC,
            echo=False,
            pool_size=1,
            max_overflow=0
        )
        
        # 尝试连接
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ 连接成功!")
            print(f"📊 PostgreSQL版本: {version}")
            
            # 测试数据库是否存在
            result = await conn.execute(text("SELECT current_database()"))
            current_db = result.scalar()
            print(f"📂 当前数据库: {current_db}")
            
            # 测试权限
            try:
                await conn.execute(text("SELECT COUNT(*) FROM information_schema.tables"))
                print("✅ 数据库权限正常")
            except Exception as e:
                print(f"⚠️ 权限可能有限: {e}")
        
        await engine.dispose()
        print("\n🎉 数据库连接测试成功!")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查PostgreSQL是否正在运行")
        print("2. 验证用户名和密码是否正确")
        print("3. 确认数据库名称是否存在")
        print("4. 检查端口号是否正确")
        print("5. 验证.env文件中的配置")
        
        # 显示具体的URL以便调试
        print(f"\n🔍 当前使用的连接URL:")
        # 隐藏密码显示
        safe_url = settings.DATABASE_URI_ASYNC.replace(settings.POSTGRES_PASSWORD, "***")
        print(f"   {safe_url}")
        
        return False

def check_env_file():
    """检查.env文件内容"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"\n📄 .env文件内容 ({env_path}):")
        print("-" * 30)
        with open(env_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 隐藏密码
                    if 'PASSWORD' in line.upper() or 'DATABASE_URL' in line.upper():
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key, value = parts
                            if 'PASSWORD' in key.upper():
                                print(f"{line_num:2d}: {key}=***")
                            elif 'DATABASE_URL' in key.upper():
                                # 隐藏URL中的密码
                                safe_value = value
                                if ':' in value and '@' in value:
                                    try:
                                        # 尝试隐藏密码部分
                                        before_at = value.split('@')[0]
                                        after_at = '@' + value.split('@', 1)[1]
                                        if ':' in before_at:
                                            user_pass = before_at.split('://', 1)[1]
                                            protocol = before_at.split('://', 1)[0] + '://'
                                            if ':' in user_pass:
                                                user = user_pass.split(':')[0]
                                                safe_value = f"{protocol}{user}:***{after_at}"
                                    except:
                                        safe_value = "***"
                                print(f"{line_num:2d}: {key}={safe_value}")
                            else:
                                print(f"{line_num:2d}: {line}")
                    else:
                        print(f"{line_num:2d}: {line}")

if __name__ == "__main__":
    print("🐾 宠物营养系统 - 数据库连接测试工具")
    print("=" * 60)
    
    # 检查.env文件
    check_env_file()
    
    # 测试连接
    success = asyncio.run(test_database_connection())
    
    sys.exit(0 if success else 1) 