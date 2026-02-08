# 🚀 服务器部署操作指南

## ⚠️ 重要提示
您刚才在**本地 Mac** 上运行了服务器脚本，所以失败了。
需要在**远程服务器** (162.43.39.81) 上运行才能生效！

---

## 📝 第一步：修改配置信息

在以下两个文件中，修改服务器信息为您的实际配置：

### 1. `deploy_to_server.sh` (第6-8行)
```bash
SERVER_IP="162.43.39.81"
SERVER_USER="root"  # 改成您的服务器用户名
SERVER_PATH="/root/apple_order_query"  # 改成服务器上的实际路径
```

### 2. `ssh_to_server.sh` (第4-6行)
```bash
SERVER_USER="root"  # 改成您的服务器用户名
SERVER_IP="162.43.39.81"
SERVER_PATH="/root/apple_order_query"  # 改成服务器上的实际路径
```

---

## 🎯 第二步：选择部署方式

### 方式 1：一键部署（推荐）

在**本地 Mac** 上运行：
```bash
./deploy_to_server.sh
```

这会自动：
1. 打包所有文件
2. 上传到服务器
3. 在服务器上解压
4. 安装依赖
5. 启动服务
6. 验证运行状态

---

### 方式 2：手动部署

#### 2.1 SSH 连接到服务器
```bash
./ssh_to_server.sh
```

或者手动连接：
```bash
ssh root@162.43.39.81
cd /root/apple_order_query
```

#### 2.2 在服务器上运行修复脚本
```bash
./fix_server.sh
```

---

## 🔍 第三步：验证部署

### 在服务器上检查
```bash
# 查看进程
ps aux | grep web_server

# 查看端口
lsof -i :8846

# 测试访问
curl http://127.0.0.1:8846/

# 查看日志
tail -f web_server.log
```

### 在浏览器访问
```
http://app.moneych.top/
```

---

## 🐛 常见错误和解决方案

### 错误 1: 在本地 Mac 运行了服务器脚本
**症状**: 看到 `mc@mcdeMac-mini` 提示符
**解决**: 
- ❌ 不要在本地运行 `./fix_server.sh` 或 `./start_server_bg.sh`
- ✅ 使用 `./deploy_to_server.sh` 部署
- ✅ 或者先 SSH 到服务器再运行脚本

### 错误 2: OpenSSL/LibreSSL 警告
**原因**: 这是本地 Mac 的 Python 环境问题
**解决**: 忽略此警告，或在服务器上运行（服务器通常没有这个问题）

### 错误 3: 权限不足
```bash
# 在服务器上运行
chmod +x *.sh
```

### 错误 4: 找不到 requests 模块
```bash
# 在服务器上运行
pip3 install requests
```

---

## 📋 快速命令参考

### 本地操作（Mac）
```bash
# 一键部署到服务器
./deploy_to_server.sh

# SSH 连接到服务器
./ssh_to_server.sh
```

### 服务器操作（162.43.39.81）
```bash
# 诊断问题
./diagnose.sh

# 一键修复
./fix_server.sh

# 启动服务
./start_server_bg.sh

# 停止服务
./stop_server.sh

# 查看状态
./check_server.sh

# 查看日志
tail -f web_server.log
```

---

## ✅ 部署成功标志

1. ✅ 服务器上可以访问: `curl http://127.0.0.1:8846/`
2. ✅ 浏览器可以打开: `http://app.moneych.top/`
3. ✅ 没有 502 错误
4. ✅ 能看到苹果订单监控界面

---

## 🎓 记住这个规则

```
┌─────────────────────────────────────────────────┐
│  本地 Mac (您现在的位置)                        │
│  ├─ 开发和编辑代码                              │
│  ├─ 运行 ./deploy_to_server.sh                 │
│  └─ 运行 ./ssh_to_server.sh                    │
└─────────────────────────────────────────────────┘
                    ⬇️ 部署
┌─────────────────────────────────────────────────┐
│  服务器 162.43.39.81 (运行服务的地方)          │
│  ├─ 运行 ./fix_server.sh                        │
│  ├─ 运行 ./start_server_bg.sh                   │
│  └─ 查看 web_server.log                         │
└─────────────────────────────────────────────────┘
```

---

## 📞 需要帮助？

1. 确认您的服务器用户名和路径
2. 修改 `deploy_to_server.sh` 中的配置
3. 运行 `./deploy_to_server.sh`
4. 如有问题，查看输出的错误信息
