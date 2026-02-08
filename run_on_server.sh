#!/bin/bash
# 简化版远程部署脚本 - 避免 bashrc 干扰

SERVER_USER="root"
SERVER_IP="162.43.39.81"
SERVER_PATH="/root/apple_order_query"

echo "🚀 直接在服务器上运行部署..."
echo ""
echo "📍 目标服务器: ${SERVER_USER}@${SERVER_IP}"
echo "📁 项目路径: ${SERVER_PATH}"
echo ""

# 使用 bash --noprofile --norc 避免 bashrc 干扰
ssh ${SERVER_USER}@${SERVER_IP} bash --noprofile --norc << 'ENDSSH'

cd /root/apple_order_query

echo "🚀 开始部署..."
echo ""

# 1. 停止旧服务
echo "1️⃣ 停止旧服务..."
pkill -f "python.*web_server.py" 2>/dev/null
sleep 2
echo "✅ 已停止旧服务"

# 2. 检查环境
echo ""
echo "2️⃣ 检查环境..."
python3 --version

# 3. 检查依赖
echo ""
echo "3️⃣ 检查依赖..."
python3 -c "import requests; print('✅ requests 已安装')" 2>/dev/null || {
    echo "正在安装 requests..."
    pip3 install requests -q
}

# 4. 启动服务
echo ""
echo "4️⃣ 启动服务..."
nohup python3 web_server.py > web_server.log 2>&1 &
sleep 3

# 5. 验证
echo ""
echo "5️⃣ 验证服务..."
PID=$(pgrep -f "python.*web_server.py")

if [ -n "$PID" ]; then
    echo "✅ 服务已启动 (PID: $PID)"
    
    # 测试本地访问
    sleep 2
    if curl -s -m 5 http://127.0.0.1:8846/ > /dev/null 2>&1; then
        echo "✅ 服务运行正常"
        echo ""
        echo "================================"
        echo "🎉 部署成功！"
        echo "================================"
        echo ""
        echo "🌐 访问地址: http://app.moneych.top/"
        echo "📊 监控面板: http://app.moneych.top/"
        echo "🔍 批量查询: http://app.moneych.top/query"
        echo "⚙️ 系统设置: http://app.moneych.top/settings"
        echo ""
        echo "📝 查看日志: tail -f /root/apple_order_query/web_server.log"
    else
        echo "⚠️ 服务启动但可能有问题"
        echo ""
        echo "最近的日志:"
        tail -20 web_server.log
    fi
else
    echo "❌ 服务启动失败"
    echo ""
    echo "错误日志:"
    tail -30 web_server.log 2>/dev/null || echo "没有日志文件"
fi

ENDSSH

echo ""
echo "✅ 远程执行完成"
