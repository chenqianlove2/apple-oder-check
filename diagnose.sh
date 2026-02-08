#!/bin/bash
# 服务器端诊断脚本 - 排查 502 错误

echo "================================"
echo "🔍 苹果订单监控系统诊断"
echo "================================"
echo ""

echo "📍 1. 检查当前位置"
echo "--------------------------------"
hostname
pwd
echo ""

echo "📊 2. 检查 Python 进程"
echo "--------------------------------"
ps aux | grep -E 'python.*web_server' | grep -v grep
echo ""

echo "🔌 3. 检查端口占用"
echo "--------------------------------"
echo "检查 8846 端口:"
lsof -i :8846 2>/dev/null || echo "❌ 端口 8846 未被占用"
echo ""

echo "📝 4. 检查最近的日志"
echo "--------------------------------"
if [ -f "web_server.log" ]; then
    echo "最后 20 行日志:"
    tail -20 web_server.log
else
    echo "❌ 日志文件不存在"
fi
echo ""

echo "🧪 5. 测试本地服务"
echo "--------------------------------"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8846/ 2>/dev/null || echo "❌ 无法连接到本地服务"
echo ""

echo "🔧 6. 检查文件权限"
echo "--------------------------------"
ls -la web_server.py
echo ""

echo "================================"
echo "💡 建议操作:"
echo "================================"

PID=$(pgrep -f "python.*web_server.py")
if [ -z "$PID" ]; then
    echo "❌ 服务未运行"
    echo "➡️  执行: ./start_server_bg.sh"
else
    echo "✅ 服务正在运行 (PID: $PID)"
    if ! curl -s http://127.0.0.1:8846/ > /dev/null 2>&1; then
        echo "⚠️  但无法访问，可能需要重启"
        echo "➡️  执行: ./stop_server.sh && ./start_server_bg.sh"
    else
        echo "✅ 本地访问正常"
        echo "⚠️  如果域名访问仍然 502，检查 1Panel 反向代理配置"
        echo "➡️  代理地址应该是: http://127.0.0.1:8846"
    fi
fi
echo ""
