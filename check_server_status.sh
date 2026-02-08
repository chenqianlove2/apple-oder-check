#!/bin/bash
# 检查服务器状态

SERVER_USER="root"
SERVER_IP="162.43.39.81"

echo "🔍 检查服务器状态..."
echo ""

ssh ${SERVER_USER}@${SERVER_IP} bash --noprofile --norc << 'ENDSSH'

cd /root/apple_order_query

echo "📊 服务状态"
echo "================================"

# 检查进程
PID=$(pgrep -f "python.*web_server.py")
if [ -n "$PID" ]; then
    echo "✅ 服务运行中 (PID: $PID)"
    ps aux | grep $PID | grep -v grep
else
    echo "❌ 服务未运行"
fi

echo ""
echo "🔌 端口状态"
echo "================================"
lsof -i :8846 2>/dev/null || echo "❌ 端口 8846 未监听"

echo ""
echo "🧪 本地测试"
echo "================================"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8846/ 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 本地访问成功 (HTTP $HTTP_CODE)"
else
    echo "⚠️ 本地访问失败 (HTTP $HTTP_CODE)"
fi

echo ""
echo "📝 最新日志 (最后 15 行)"
echo "================================"
tail -15 web_server.log 2>/dev/null || echo "没有日志文件"

ENDSSH
