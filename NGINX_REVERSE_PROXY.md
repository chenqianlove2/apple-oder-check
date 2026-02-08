# 🌐 反向代理配置指南

## 📍 配置信息
- 域名: `app.moneych.top`
- 后端端口: `8846`
- 后端地址: `http://127.0.0.1:8846`

---

## 🔧 在 1Panel 中配置反向代理

### 方法 1: 通过 1Panel Web 界面配置（推荐）

1. **登录 1Panel**
   - 访问: http://162.43.39.81:8845/
   - 输入用户名和密码登录

2. **进入网站管理**
   - 左侧菜单 → 网站 → 创建网站

3. **创建反向代理网站**
   - 网站类型: `反向代理`
   - 域名: `app.moneych.top`
   - 代理地址: `http://127.0.0.1:8846`
   - 协议: `HTTP` (如果需要 HTTPS，选择启用 SSL)

4. **高级配置（可选）**
   ```nginx
   # 在自定义配置中添加
   proxy_set_header Host $host;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Forwarded-Proto $scheme;
   ```

5. **保存并应用**

---

## 🔒 配置 SSL 证书（可选但推荐）

### 在 1Panel 中申请免费 SSL 证书:

1. **进入证书管理**
   - 左侧菜单 → 网站 → SSL 证书

2. **申请证书**
   - 证书类型: `Let's Encrypt`
   - 域名: `app.moneych.top`
   - 验证方式: `DNS` 或 `HTTP`

3. **应用证书到网站**
   - 在网站列表中找到 `app.moneych.top`
   - 点击编辑 → SSL 配置 → 选择刚申请的证书
   - 启用 HTTPS
   - 勾选 "强制 HTTPS" (HTTP 自动跳转到 HTTPS)

---

## 🌍 域名 DNS 配置

**在您的域名服务商（如阿里云、腾讯云、Cloudflare）配置:**

1. **添加 A 记录**
   - 主机记录: `app`
   - 记录类型: `A`
   - 记录值: `162.43.39.81`
   - TTL: `600` 或默认

2. **等待 DNS 生效**
   - 通常需要 5-30 分钟
   - 可以用 `nslookup app.moneych.top` 检查

---

## ✅ 验证配置

### 1. 检查后端服务是否运行
```bash
curl http://127.0.0.1:8846/
```

### 2. 检查域名解析
```bash
# 查看域名是否解析到正确的 IP
nslookup app.moneych.top

# 或使用 dig
dig app.moneych.top
```

### 3. 测试访问
```bash
# HTTP 访问
curl http://app.moneych.top/

# HTTPS 访问（如果配置了 SSL）
curl https://app.moneych.top/
```

### 4. 浏览器访问
- HTTP: http://app.moneych.top/
- HTTPS: https://app.moneych.top/

---

## 📋 方法 2: 手动配置 Nginx（如果不用 1Panel）

如果您想手动配置 Nginx 反向代理:

### 创建 Nginx 配置文件
```bash
sudo nano /etc/nginx/sites-available/app.moneych.top
```

### 配置内容
```nginx
server {
    listen 80;
    server_name app.moneych.top;

    # 日志
    access_log /var/log/nginx/app.moneych.top.access.log;
    error_log /var/log/nginx/app.moneych.top.error.log;

    # 反向代理配置
    location / {
        proxy_pass http://127.0.0.1:8846;
        proxy_http_version 1.1;
        
        # 设置请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 启用配置
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/app.moneych.top /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 配置 HTTPS (使用 Certbot)
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
sudo yum install certbot python3-certbot-nginx  # CentOS/RHEL

# 申请证书
sudo certbot --nginx -d app.moneych.top

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 🐛 常见问题

### 问题 1: 502 Bad Gateway
**原因**: 后端服务未启动或端口错误

**解决**:
```bash
# 检查后端服务
./check_server.sh

# 如果未运行，启动服务
./start_server_bg.sh

# 检查端口是否正确
lsof -i :8846
```

### 问题 2: 域名无法访问
**原因**: DNS 未生效或配置错误

**解决**:
```bash
# 检查 DNS 解析
nslookup app.moneych.top

# 如果解析失败，等待 DNS 生效或检查域名配置
```

### 问题 3: SSL 证书申请失败
**原因**: 域名未正确解析或端口未开放

**解决**:
1. 确保域名已解析到服务器 IP
2. 确保 80 和 443 端口已开放
3. 检查防火墙设置

---

## 📱 最终访问地址

配置完成后，您可以通过以下方式访问:

- **HTTP**: http://app.moneych.top/
- **HTTPS**: https://app.moneych.top/ (配置 SSL 后)

访问页面：
- 📊 **监控面板**: https://app.moneych.top/
- 🔍 **批量查询**: https://app.moneych.top/query
- ⚙️ **设置页面**: https://app.moneych.top/settings

---

## 🔄 更新服务

当代码更新后:
```bash
# 1. 停止服务
./stop_server.sh

# 2. 更新代码
git pull  # 或重新上传文件

# 3. 重启服务
./start_server_bg.sh

# 4. 检查状态
./check_server.sh
```

**注意**: 反向代理配置无需改动，只需重启后端服务即可。
