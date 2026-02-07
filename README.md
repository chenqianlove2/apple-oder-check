# 🍎 苹果订单查询监控工具

批量查询苹果官网订单状态，支持 Telegram 自动通知。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `web_app.py` | Web 界面版本 |
| `start_monitor.py` | **后台监控启动器**（推荐） |
| `orders.txt` | **订单链接列表** |
| `monitor.py` | 监控模块 |
| `notifier.py` | Telegram 通知模块 |
| `order_loader.py` | 订单文件加载器 |

---

## 🚀 快速开始

### 1. 配置 Telegram 通知

编辑 `telegram_config.json`：
```bash
cd /Users/mc/apple_order_query
source venv/bin/activate
python -c "
from notifier import get_notifier
n = get_notifier()
n.set_config('你的Bot_Token', '你的Chat_ID')
print('配置完成')
"
```

### 2. 添加订单链接

**编辑 `orders.txt` 文件**，把你的订单链接添加进去：

```text
# 苹果订单链接列表
# 每行一个链接

https://www.apple.com/xc/us/vieworder/W1234567890/你的邮箱@example.com
https://www.apple.com/xc/us/vieworder/W0987654321/你的邮箱@example.com
```

### 3. 启动监控

```bash
cd /Users/mc/apple_order_query
source venv/bin/activate
python start_monitor.py
```

监控将：
- ✅ 每 5 分钟检查一次订单状态
- ✅ 状态变更时自动发送 Telegram 通知
- ✅ 特别关注取消订单（带 🚨 标记）

---

## 📝 orders.txt 格式说明

```text
# 以 # 开头的行是注释

# 示例订单
https://www.apple.com/xc/us/vieworder/W1356190467/13160170407@163.com

# 在此添加你的订单（每行一个）
https://www.apple.com/xc/us/vieworder/你的订单号/你的邮箱
```

**规则**：
- 每行一个订单链接
- 链接必须以 `http` 开头
- `#` 开头的是注释，会被忽略
- 空行会被忽略

---

## 🔔 通知效果

**普通状态变更**:
```
🍎 苹果订单状态变更

订单号: W1234567890
产品: iPhone 15 Pro
状态: Processing → Shipped

预计送达: Arrives Feb 16 - Feb 18
[查看订单详情]
```

**订单取消** (紧急提醒):
```
🚨 【订单已取消】

❌ 苹果订单状态变更
订单号: W1234567890
产品: iPhone 15 Pro
状态: Processing → Canceled
```

---

## 🎮 Web 界面使用

```bash
cd /Users/mc/apple_order_query
source venv/bin/activate
python web_app.py
```

然后访问 http://127.0.0.1:8080

---

## ⚙️ 高级配置

### 修改监控间隔

```python
from monitor import get_monitor

monitor = get_monitor()
monitor.update_config(monitor_interval=300)  # 5分钟（秒）
```

### 只通知特定状态

```python
monitor.update_config(
    notify_all_changes=False,  # 关闭所有变更通知
    notify_on_cancel=True,     # 只通知取消
    notify_on_ship=True,       # 只通知发货
    notify_on_deliver=True     # 只通知送达
)
```

---

## 📱 Telegram 设置

1. **获取 Bot Token**
   - 在 Telegram 搜索 `@BotFather`
   - 发送 `/newbot` 创建 Bot
   - 保存 Token

2. **获取 Chat ID**
   - 搜索 `@userinfobot`
   - 点击 Start 即可看到 ID

3. **配置完成** ✅

---

## 🛑 停止监控

按 `Ctrl+C` 即可停止监控。

---

## 📊 监控状态

```bash
python -c "
from monitor import get_monitor
m = get_monitor()
status = m.get_monitoring_status()
print(f'运行中: {status[\"running\"]}')
print(f'监控订单数: {status[\"monitored_orders\"]}')
"
```
