#!/bin/bash
# 苹果订单监控 Web 服务器启动脚本

cd /Users/mc/apple_order_query

# 检查并激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 启动服务器
echo "🍎 启动苹果订单监控 Web 服务器..."
echo "📊 访问地址: http://162.43.39.81:8845/"
echo ""

python3 web_server.py
