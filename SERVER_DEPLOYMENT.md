# 🌐 服务器部署指南

## 📍 服务器信息
- 服务器 IP: `162.43.39.81`
- Web 端口: `8845`
- 访问地址: http://162.43.39.81:8845/

---

## 🚀 在服务器上部署步骤

### 1. 上传代码到服务器
```bash
# 在本地打包
cd /Users/mc/apple_order_query
tar -czf apple_order_query.tar.gz *.py *.txt *.md *.sh *.json

# 上传到服务器
scp apple_order_query.tar.gz user@162.43.39.81:/path/to/project/

# 在服务器上解压
ssh user@162.43.39.81
cd /path/to/project/
tar -xzf apple_order_query.tar.gz
```

### 2. 在服务器上安装依赖
```bash
# 创建虚拟环境（如果还没有）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install requests
```

### 3. 启动服务器
```bash
# 方法 1：后台启动（推荐）
./start_server_bg.sh

# 方法 2：前台启动（用于调试）
python3 web_server.py
```

### 4. 检查服务器状态
```bash
./check_server.sh
```

### 5. 停止服务器
```bash
./stop_server.sh
```

---

## 🔧 防火墙配置

### 如果无法访问，需要开放 8845 端口：

**CentOS/RHEL (firewalld):**
```bash
sudo firewall-cmd --zone=public --add-port=8845/tcp --permanent
sudo firewall-cmd --reload
```

**Ubuntu/Debian (ufw):**
```bash
sudo ufw allow 8845/tcp
sudo ufw reload
```

**阿里云/腾讯云:**
在云服务器控制台 → 安全组 → 添加入站规则：
- 端口: 8845
- 协议: TCP
- 源地址: 0.0.0.0/0 (或指定 IP)

---

## 📊 验证服务器是否运行

### 1. 在服务器上测试
```bash
curl http://127.0.0.1:8845/
```

### 2. 从本地测试
```bash
curl http://162.43.39.81:8845/
```

### 3. 浏览器访问
打开浏览器访问: http://162.43.39.81:8845/

---

## 🐛 常见问题

### 问题1: 端口被占用
```bash
# 查看占用端口的进程
lsof -i :8845

# 杀死进程
kill -9 <PID>
```

### 问题2: 权限不足
```bash
# 给脚本添加执行权限
chmod +x *.sh

# 如果需要 root 权限
sudo ./start_server_bg.sh
```

### 问题3: Python 模块未找到
```bash
# 确保激活虚拟环境
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题4: 防火墙阻止
```bash
# 临时关闭防火墙测试（不推荐用于生产环境）
sudo systemctl stop firewalld  # CentOS
sudo ufw disable               # Ubuntu
```

---

## 🔄 开机自启动（可选）

### 使用 systemd 服务

创建服务文件 `/etc/systemd/system/apple-order-monitor.service`:
```ini
[Unit]
Description=Apple Order Monitor Web Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/apple_order_query
ExecStart=/path/to/apple_order_query/venv/bin/python3 /path/to/apple_order_query/web_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable apple-order-monitor
sudo systemctl start apple-order-monitor
sudo systemctl status apple-order-monitor
```

---

## 📱 访问页面

启动成功后，可以访问以下页面：

- 📊 **监控面板**: http://162.43.39.81:8845/
- 🔍 **批量查询**: http://162.43.39.81:8845/query
- ⚙️ **设置页面**: http://162.43.39.81:8845/settings

**注意**: 此项目没有登录功能，直接访问即可使用！

---

## 📝 查看日志

```bash
# 实时查看日志
tail -f web_server.log

# 查看最近的错误
grep -i error web_server.log
```
