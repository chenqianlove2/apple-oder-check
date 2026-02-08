#!/bin/bash
# 后台启动 Web 服务器

cd /Users/mc/apple_order_query

# 停止之前的进程
echo "🛑 停止旧进程..."
pkill -f "python.*web_server.py"
sleep 2

# 检查并激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 后台启动服务器
echo "🚀 启动 Web 服务器..."
nohup python3 web_server.py > web_server.log 2>&1 &

# 获取进程 ID
sleep 2
PID=$(pgrep -f "python.*web_server.py")

if [ -n "$PID" ]; then
    echo "✅ 服务器已启动 (PID: $PID)"
    echo "📊 本地访问: http://127.0.0.1:8846/"
    echo "🌐 域名访问: http://app.moneych.top/ (需要先配置反向代理)"
    echo "📝 日志文件: web_server.log"
else
    echo "❌ 启动失败，请查看日志"
    tail -20 web_server.log
fi
