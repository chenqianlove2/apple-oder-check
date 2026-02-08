#!/bin/bash
# 服务器端一键修复脚本

echo "🔧 开始修复服务..."
echo ""

# 1. 停止旧进程
echo "1️⃣ 停止旧进程..."
pkill -9 -f "python.*web_server.py"
sleep 2

# 2. 清理日志（可选）
if [ -f "web_server.log" ]; then
    mv web_server.log web_server.log.bak
    echo "✅ 已备份旧日志"
fi

# 3. 检查 Python
echo ""
echo "2️⃣ 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo "❌ Python3 未安装"
    exit 1
fi

# 4. 检查依赖
echo ""
echo "3️⃣ 检查依赖..."
python3 -c "import requests" 2>/dev/null || {
    echo "⚠️  requests 模块未安装"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    pip3 install requests
}

# 5. 重新启动
echo ""
echo "4️⃣ 启动服务..."
nohup python3 web_server.py > web_server.log 2>&1 &
sleep 3

# 6. 验证
echo ""
echo "5️⃣ 验证服务..."
PID=$(pgrep -f "python.*web_server.py")
if [ -n "$PID" ]; then
    echo "✅ 服务已启动 (PID: $PID)"
    
    # 测试访问
    if curl -s http://127.0.0.1:8846/ > /dev/null; then
        echo "✅ 本地访问正常"
        echo ""
        echo "================================"
        echo "✅ 修复完成！"
        echo "================================"
        echo "📊 本地测试: curl http://127.0.0.1:8846/"
        echo "🌐 域名访问: http://app.moneych.top/"
        echo "📝 查看日志: tail -f web_server.log"
    else
        echo "⚠️  服务启动但无法访问"
        echo "查看日志:"
        tail -20 web_server.log
    fi
else
    echo "❌ 服务启动失败"
    echo "查看日志:"
    tail -20 web_server.log
fi
