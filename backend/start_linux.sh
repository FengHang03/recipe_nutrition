#!/bin/bash

# Linux环境启动脚本 - 宠物营养系统
# 连接到Windows上通过ngrok暴露的PostgreSQL数据库

echo "🐾 启动宠物营养系统 (Linux版)"
echo "================================================"

# 检查Python版本
echo "📋 检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查pip
pip3 --version
if [ $? -ne 0 ]; then
    echo "❌ pip3 未安装，请先安装pip3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装Python依赖包..."
pip install -r requirements.txt

# 检查数据库连接
echo "🔍 检查数据库连接..."
echo "数据库服务器: 0.tcp.us-cal-1.ngrok.io:13775"
echo "数据库名称: pet_diet_db"

# 测试数据库连接
python3 -c "
import asyncio
import sys
sys.path.append('.')
from config_linux import linux_settings
from app.db.database import check_database_connection

async def test_db():
    try:
        result = await check_database_connection()
        if result:
            print('✅ 数据库连接成功')
            return 0
        else:
            print('❌ 数据库连接失败')
            return 1
    except Exception as e:
        print(f'❌ 数据库连接错误: {e}')
        return 1

exit_code = asyncio.run(test_db())
sys.exit(exit_code)
"

if [ $? -ne 0 ]; then
    echo "⚠️ 数据库连接失败，但程序仍会启动。请检查："
    echo "   1. Windows上的ngrok是否正在运行"
    echo "   2. 端口转发配置是否正确"
    echo "   3. 防火墙设置"
fi

echo ""
echo "🚀 启动Web服务器..."
echo "服务地址: http://0.0.0.0:8000"
echo "API文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动应用
python3 main_linux.py 