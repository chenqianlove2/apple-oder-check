# 🚀 快速配置指南：app.moneych.top

## ✅ 第一步：后端服务已就绪

✔️ 服务已启动在 `127.0.0.1:8846`
✔️ 可以通过 `curl http://127.0.0.1:8846/` 测试

---

## 🔧 第二步：在 1Panel 中配置反向代理

### 📝 操作步骤：

1. **登录 1Panel**
   ```
   访问: http://162.43.39.81:8845/
   输入您的用户名和密码
   ```

2. **创建反向代理网站**
   - 点击左侧菜单 → **网站**
   - 点击右上角 **创建网站** 按钮
   - 选择 **反向代理** 类型

3. **填写配置信息**
   ```
   域名: app.moneych.top
   代理地址: http://127.0.0.1:8846
   ```

4. **保存并应用**

5. **（可选）配置 SSL 证书**
   - 在网站列表中找到 `app.moneych.top`
   - 点击 SSL 图标
   - 申请 Let's Encrypt 免费证书
   - 启用 HTTPS 和强制跳转

---

## 🌍 第三步：配置域名 DNS

在您的域名服务商（阿里云/腾讯云/Cloudflare）添加 DNS 记录：

```
类型: A 记录
主机记录: app
记录值: 162.43.39.81
TTL: 600 (或默认)
```

**验证 DNS 是否生效:**
```bash
nslookup app.moneych.top
# 应该返回 IP: 162.43.39.81
```

---

## ✅ 完成！访问您的网站

- **HTTP**: http://app.moneych.top/
- **HTTPS**: https://app.moneych.top/ (配置 SSL 后)

### 可用页面：
- 📊 监控面板: https://app.moneych.top/
- 🔍 批量查询: https://app.moneych.top/query
- ⚙️ 系统设置: https://app.moneych.top/settings

---

## 🐛 故障排查

### 如果出现 502 错误：
```bash
# 检查后端服务状态
./check_server.sh

# 重启服务
./stop_server.sh
./start_server_bg.sh
```

### 如果无法访问：
1. 检查 DNS 是否生效: `nslookup app.moneych.top`
2. 检查防火墙: 确保 80 和 443 端口开放
3. 检查 1Panel 反向代理配置是否正确

---

## 📞 需要帮助？

查看详细文档: `NGINX_REVERSE_PROXY.md`
