#!/bin/bash
# 检查服务器状态

echo "🔍 检查服务器状态..."
echo ""

# 检查进程
PID=$(pgrep -f "python.*web_server.py")
if [ -n "$PID" ]; then
    echo "✅ 服务器正在运行 (PID: $PID)"
    ps aux | grep $PID | grep -v grep
else
    echo "❌ 服务器未运行"
fi

echo ""

# 检查端口
if lsof -i :8845 > /dev/null 2>&1; then
    echo "✅ 端口 8845 已占用"
    lsof -i :8845
else
    echo "❌ 端口 8845 未被占用"
fi

echo ""

# 显示最近的日志
if [ -f "web_server.log" ]; then
    echo "📝 最近的日志 (最后 10 行):"
    echo "================================"
    tail -10 web_server.log
fi
