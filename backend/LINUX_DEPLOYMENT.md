# Linux环境部署指南

## 概述
此配置允许在Linux服务器上运行宠物营养系统后端，同时连接到Windows上通过ngrok暴露的PostgreSQL数据库。

## 前提条件

### Linux服务器要求
- Ubuntu 18.04+ / CentOS 7+ / 其他现代Linux发行版
- Python 3.8+
- pip3
- 至少1GB内存
- 网络连接（能访问ngrok域名）

### Windows端配置
确保Windows上已经：
1. ✅ PostgreSQL数据库正在运行（端口5433）
2. ✅ ngrok已配置数据库端口转发：
   ```
   tcp://0.tcp.us-cal-1.ngrok.io:13775 -> localhost:5433
   ```

## 部署步骤

### 1. 上传代码到Linux服务器
```bash
# 将backend目录上传到Linux服务器
scp -r backend/ user@your-linux-server:/path/to/deployment/
```

### 2. 登录Linux服务器
```bash
ssh user@your-linux-server
cd /path/to/deployment/backend
```

### 3. 给启动脚本执行权限
```bash
chmod +x start_linux.sh
```

### 4. 运行部署脚本
```bash
./start_linux.sh
```

## 配置说明

### 数据库连接配置
- **主机**: `0.tcp.us-cal-1.ngrok.io`
- **端口**: `13775`
- **用户名**: `postgres`
- **密码**: `1997`
- **数据库**: `pet_diet_db`

### 文件说明
1. **config_linux.py** - Linux环境专用配置
2. **main_linux.py** - Linux环境主应用文件
3. **start_linux.sh** - 自动化启动脚本

## 服务访问

启动成功后，服务将在以下地址可用：
- **API服务**: `http://your-linux-server:8000`
- **API文档**: `http://your-linux-server:8000/docs`
- **健康检查**: `http://your-linux-server:8000/api/v1/health/`

## 故障排除

### 数据库连接失败
1. 检查Windows上的ngrok是否正在运行
2. 验证端口转发配置：
   ```bash
   # 在Linux上测试连接
   telnet 0.tcp.us-cal-1.ngrok.io 13775
   ```
3. 检查防火墙设置

### Python环境问题
```bash
# 检查Python版本
python3 --version

# 检查虚拟环境
source venv/bin/activate
pip list
```

### 端口占用
```bash
# 检查8000端口是否被占用
netstat -tulpn | grep 8000

# 如需使用其他端口，修改main_linux.py中的端口配置
```

## 生产环境优化

### 使用Gunicorn（推荐）
```bash
# 安装Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn main_linux:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 使用systemd服务
创建服务文件 `/etc/systemd/system/pet-nutrition.service`:
```ini
[Unit]
Description=Pet Nutrition API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/deployment/backend
ExecStart=/path/to/deployment/backend/venv/bin/python main_linux.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 监控和日志

### 查看应用日志
```bash
# 实时查看日志
tail -f /var/log/pet-nutrition.log

# 或者直接查看控制台输出
```

### 性能监控
- CPU和内存使用情况
- 数据库连接状态
- API响应时间

## 安全建议

1. **更改默认密码**: 修改`config_linux.py`中的`SECRET_KEY`
2. **使用HTTPS**: 在生产环境中配置SSL证书
3. **限制CORS**: 修改允许的域名列表
4. **防火墙配置**: 只开放必要的端口

## 支持

如遇到问题，请检查：
1. Windows端ngrok状态
2. Linux服务器网络连接
3. Python依赖是否完整安装
4. 数据库连接配置是否正确 