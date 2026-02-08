#!/bin/bash
# 停止 Web 服务器

echo "🛑 停止 Web 服务器..."
pkill -f "python.*web_server.py"

sleep 1

if pgrep -f "python.*web_server.py" > /dev/null; then
    echo "❌ 进程仍在运行，强制终止..."
    pkill -9 -f "python.*web_server.py"
else
    echo "✅ 服务器已停止"
fi
