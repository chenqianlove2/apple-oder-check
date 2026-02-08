#!/bin/bash
# 直接在服务器上执行所有操作的脚本

echo "🔍 正在检测服务器配置..."
echo ""

# 服务器信息
SERVER_IP="162.43.39.81"

# 尝试不同的用户名和常见路径
USERS=("root" "ubuntu" "admin" "www")
PATHS=(
    "/root/apple_order_query"
    "/home/ubuntu/apple_order_query"
    "/home/admin/apple_order_query"
    "/opt/apple_order_query"
    "/www/wwwroot/apple_order_query"
)

echo "🔎 测试连接和查找项目路径..."
echo "================================"

# 函数：测试 SSH 连接
test_ssh() {
    local user=$1
    local ip=$2
    
    echo -n "测试 ${user}@${ip} ... "
    
    # 测试连接
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${user}@${ip} "echo 'OK'" 2>/dev/null | grep -q "OK"; then
        echo "✅ 连接成功"
        
        # 查找项目路径
        echo "  🔍 查找项目文件..."
        
        for path in "${PATHS[@]}"; do
            if ssh ${user}@${ip} "[ -f ${path}/web_server.py ] && echo 'FOUND'" 2>/dev/null | grep -q "FOUND"; then
                echo "  ✅ 找到项目: ${path}"
                
                # 找到了，执行部署
                FOUND_USER=$user
                FOUND_PATH=$path
                return 0
            fi
        done
        
        # 尝试搜索
        echo "  🔍 在常见位置搜索 web_server.py..."
        SEARCH_RESULT=$(ssh ${user}@${ip} "find /root /home /opt /www -name 'web_server.py' 2>/dev/null | head -1")
        
        if [ -n "$SEARCH_RESULT" ]; then
            FOUND_PATH=$(dirname "$SEARCH_RESULT")
            echo "  ✅ 找到项目: ${FOUND_PATH}"
            FOUND_USER=$user
            return 0
        fi
        
        echo "  ❌ 未找到项目文件"
        return 1
    else
        echo "❌ 连接失败"
        return 1
    fi
}

# 遍历测试
FOUND_USER=""
FOUND_PATH=""

for user in "${USERS[@]}"; do
    if test_ssh "$user" "$SERVER_IP"; then
        break
    fi
done

echo ""
echo "================================"

if [ -z "$FOUND_USER" ] || [ -z "$FOUND_PATH" ]; then
    echo "❌ 自动检测失败"
    echo ""
    echo "请手动提供信息："
    echo "1. 服务器用户名是什么？(root/ubuntu/其他)"
    echo "2. 项目在服务器上的完整路径是什么？"
    echo ""
    echo "然后手动连接："
    echo "  ssh YOUR_USER@162.43.39.81"
    echo "  cd YOUR_PROJECT_PATH"
    echo "  ./fix_server.sh"
    exit 1
fi

echo "✅ 检测完成！"
echo ""
echo "📍 服务器信息："
echo "   用户名: ${FOUND_USER}"
echo "   项目路径: ${FOUND_PATH}"
echo ""

# 创建临时部署脚本
REMOTE_SCRIPT=$(cat << 'REMOTE_SCRIPT_EOF'
#!/bin/bash
echo "🚀 开始在服务器上部署..."
echo ""

# 停止旧服务
echo "1️⃣ 停止旧服务..."
pkill -f "python.*web_server.py" 2>/dev/null
sleep 2

# 检查环境
echo ""
echo "2️⃣ 检查环境..."
echo "Python 版本:"
python3 --version

echo ""
echo "检查依赖..."
python3 -c "import requests; print('✅ requests 已安装')" 2>/dev/null || {
    echo "⚠️ 正在安装 requests..."
    pip3 install requests
}

# 启动服务
echo ""
echo "3️⃣ 启动服务..."
nohup python3 web_server.py > web_server.log 2>&1 &
sleep 3

# 验证
echo ""
echo "4️⃣ 验证服务..."
PID=$(pgrep -f "python.*web_server.py")

if [ -n "$PID" ]; then
    echo "✅ 服务已启动 (PID: $PID)"
    
    # 测试本地访问
    if curl -s http://127.0.0.1:8846/ > /dev/null 2>&1; then
        echo "✅ 本地访问正常"
        echo ""
        echo "================================"
        echo "🎉 部署成功！"
        echo "================================"
        echo ""
        echo "📊 测试命令: curl http://127.0.0.1:8846/"
        echo "🌐 访问地址: http://app.moneych.top/"
        echo "📝 查看日志: tail -f web_server.log"
        echo ""
    else
        echo "⚠️ 服务启动但无法访问"
        echo "查看日志:"
        tail -20 web_server.log
    fi
else
    echo "❌ 服务启动失败"
    echo "查看日志:"
    if [ -f "web_server.log" ]; then
        tail -30 web_server.log
    else
        echo "日志文件不存在"
    fi
fi
REMOTE_SCRIPT_EOF
)

echo "🚀 开始远程部署..."
echo "================================"
echo ""

# 在服务器上执行
ssh -t ${FOUND_USER}@${SERVER_IP} "cd ${FOUND_PATH} && bash -c '${REMOTE_SCRIPT}'"

EXIT_CODE=$?

echo ""
echo "================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 部署完成！"
    echo ""
    echo "🌐 现在可以访问: http://app.moneych.top/"
    echo ""
    echo "💡 如需查看服务器日志，运行："
    echo "   ssh ${FOUND_USER}@${SERVER_IP}"
    echo "   cd ${FOUND_PATH}"
    echo "   tail -f web_server.log"
else
    echo "❌ 部署过程中出现错误"
    echo ""
    echo "💡 请手动连接服务器查看："
    echo "   ssh ${FOUND_USER}@${SERVER_IP}"
    echo "   cd ${FOUND_PATH}"
    echo "   tail -f web_server.log"
fi
