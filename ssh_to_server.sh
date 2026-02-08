#!/bin/bash
# 快速 SSH 连接到服务器并进入项目目录

# 配置信息（请修改为您的实际信息）
SERVER_USER="root"  # 修改为您的服务器用户名
SERVER_IP="162.43.39.81"
SERVER_PATH="/root/apple_order_query"  # 修改为服务器上的实际路径

echo "🔐 连接到服务器..."
echo "ssh ${SERVER_USER}@${SERVER_IP}"
echo ""

# SSH 连接并自动进入项目目录
ssh -t ${SERVER_USER}@${SERVER_IP} "cd ${SERVER_PATH} && exec bash"
