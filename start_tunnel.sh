#!/bin/bash
echo "🔐 创建SSH隧道: 服务器12345端口 -> 本地12345端口"
echo "访问地址: http://localhost:12345"
echo "按 Ctrl+C 停止隧道"
sshpass -p "mc19950712" ssh -N -L 12345:localhost:12345 root@162.43.39.81
