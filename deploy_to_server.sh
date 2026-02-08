#!/bin/bash
# 部署到服务器的完整脚本

echo "🚀 开始部署到服务器..."
echo ""

# 配置信息（请修改为您的实际信息）
SERVER_IP="162.43.39.81"
SERVER_USER="root"  # 修改为您的服务器用户名
SERVER_PATH="/root/apple_order_query"  # 修改为服务器上的实际路径

echo "📦 1. 打包文件..."
tar -czf deploy.tar.gz \
    *.py \
    *.sh \
    *.txt \
    *.md \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.log" \
    --exclude="deploy.tar.gz"

echo "✅ 打包完成"
echo ""

echo "📤 2. 上传到服务器..."
echo "scp deploy.tar.gz ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/"
scp deploy.tar.gz ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/

if [ $? -eq 0 ]; then
    echo "✅ 上传成功"
else
    echo "❌ 上传失败，请检查服务器地址和权限"
    exit 1
fi
echo ""

echo "🔧 3. 在服务器上部署..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /root/apple_order_query

# 解压
tar -xzf deploy.tar.gz
rm deploy.tar.gz

# 设置权限
chmod +x *.sh

# 停止旧服务
echo "停止旧服务..."
pkill -f "python.*web_server.py"
sleep 2

# 检查 Python 和依赖
echo "检查环境..."
python3 --version

# 安装依赖（如果需要）
python3 -c "import requests" 2>/dev/null || pip3 install requests

# 启动服务
echo "启动服务..."
nohup python3 web_server.py > web_server.log 2>&1 &
sleep 3

# 验证
PID=$(pgrep -f "python.*web_server.py")
if [ -n "$PID" ]; then
    echo "✅ 服务已启动 (PID: $PID)"
    
    # 测试访问
    if curl -s http://127.0.0.1:8846/ > /dev/null; then
        echo "✅ 服务运行正常"
    else
        echo "⚠️ 服务启动但访问异常，查看日志:"
        tail -10 web_server.log
    fi
else
    echo "❌ 服务启动失败，查看日志:"
    tail -20 web_server.log
fi
ENDSSH

echo ""
echo "================================"
echo "🎉 部署完成！"
echo "================================"
echo "访问地址: http://app.moneych.top/"
echo ""

# 清理本地临时文件
rm deploy.tar.gz
