# 📱 Telegram 通知推送规则说明

## 🎯 通知推送的触发条件

根据当前代码，以下情况会发送 Telegram 通知：

---

## 1️⃣ 首次查询到取消状态 ⚠️

### 条件：
- 订单**第一次**被查询（之前没有历史记录）
- 订单状态是 `CANCELED` 或 `CANCELLED`

### 通知内容：
```
🚨🚨 【重要警告：订单已取消】 🚨🚨

❌ 苹果订单状态变更

订单号: W1234567890
产品: iPhone 15 Pro Max
下单日期: 2026-01-15

状态变更:
⚠️ 首次查询发现 → ❌ Canceled

预计送达: -

检测时间: 2026-02-08 14:30:00

🔗 查看订单详情
```

### 代码位置：
- `monitor.py` 第 224-234 行
- `web_monitor.py` 第 343-350 行
- `web_server.py` 第 2174-2182 行

---

## 2️⃣ 订单状态发生变更 🔄

### 条件：
- 订单**不是第一次**查询（有历史记录）
- 新状态 ≠ 旧状态
- 两个状态都是有效状态（不是 `-`、`None`、`''`）

### 有效状态列表：
```
PLACED            - 已下单
PROCESSING        - 处理中
PREPARED_FOR_SHIPMENT - 准备发货
SHIPPED           - 已发货
DELIVERED         - 已送达
CANCELED          - 已取消
```

### 通知内容示例：

#### 取消订单（非首次）：
```
🚨 【订单已取消】

❌ 苹果订单状态变更

订单号: W1234567890
状态变更:
⏳ Processing → ❌ Canceled
```

#### 已发货：
```
🚚 苹果订单状态变更

订单号: W1234567890
状态变更:
⏳ Processing → 🚚 Shipped

📮 物流单号: 1234567890
```

#### 已送达：
```
✅ 苹果订单状态变更

订单号: W1234567890
状态变更:
🚚 Shipped → ✅ Delivered
```

### 代码位置：
- `monitor.py` 第 224-240 行
- `web_monitor.py` 第 304-327 行

---

## 3️⃣ 不会推送的情况 ❌

### 情况 1：首次查询非取消状态
```
第一次查询 → PROCESSING ❌ 不通知
第一次查询 → SHIPPED    ❌ 不通知
第一次查询 → DELIVERED  ❌ 不通知
```
**原因**：这些是正常的初始状态，不需要提醒

### 情况 2：状态未变化
```
上次查询 → PROCESSING
这次查询 → PROCESSING ❌ 不通知（状态相同）
```

### 情况 3：查询失败
```
查询失败 → 返回错误 ❌ 不通知
```

### 情况 4：状态无效
```
上次状态：-
这次状态：- ❌ 不通知（都是无效状态）
```

### 情况 5：已完成的订单
```
状态：DELIVERED（已送达）
或
状态：CANCELED（已取消）

→ 跳过查询 ❌ 不再通知
```
**原因**：这些是终态，不会再变化

---

## 📋 完整通知流程图

```
┌─────────────────┐
│  开始查询订单   │
└────────┬────────┘
         │
         ▼
   ┌──────────┐
   │ 查询成功？│
   └─┬─────┬──┘
     │ No  │
     ▼     │ Yes
   ❌不通知 │
           ▼
   ┌──────────────┐
   │ 是首次查询？  │
   └─┬─────────┬──┘
     │ Yes     │ No
     │         │
     ▼         ▼
┌─────────┐  ┌──────────────┐
│状态是    │  │ 状态是否变更？│
│CANCELED?│  └─┬─────────┬──┘
└─┬───┬───┘    │ No      │ Yes
  │Yes│No      │         │
  │   │        ▼         ▼
  │   │      ❌不通知  ┌────────┐
  │   │               │ 发送通知│
  │   ▼               │ (状态变更)│
  │  ❌不通知          └────────┘
  │
  ▼
┌────────┐
│发送通知 │
│(首次取消)│
└────────┘
```

---

## 🎯 具体场景举例

### 场景 1：新订单，正常流程
```
Day 1: 添加订单 → 查询 → PROCESSING → ❌ 不通知
Day 2: 自动查询 → PROCESSING → ❌ 不通知（未变更）
Day 3: 自动查询 → SHIPPED → ✅ 通知！（变更）
Day 4: 自动查询 → DELIVERED → ✅ 通知！（变更）
Day 5: 跳过查询（已完成）
```

### 场景 2：新订单，已取消
```
Day 1: 添加订单 → 查询 → CANCELED → ✅ 通知！（首次取消）
Day 2: 跳过查询（已完成）
```

### 场景 3：订单被取消
```
Day 1: 添加订单 → 查询 → PROCESSING → ❌ 不通知
Day 2: 自动查询 → PROCESSING → ❌ 不通知
Day 3: 自动查询 → CANCELED → ✅ 通知！（变更为取消）
Day 4: 跳过查询（已完成）
```

### 场景 4：批量添加历史订单
```
订单 A: PROCESSING → ❌ 不通知
订单 B: SHIPPED → ❌ 不通知
订单 C: CANCELED → ✅ 通知！（首次发现取消）
订单 D: DELIVERED → ❌ 不通知
```

---

## ⚙️ 配置控制（可选）

虽然当前代码默认行为已确定，但 `monitor_config.json` 中有这些配置项：

```json
{
  "notify_on_cancel": true,      // 取消时通知
  "notify_on_ship": true,        // 发货时通知
  "notify_on_deliver": true,     // 送达时通知
  "notify_all_changes": true     // 任何变更都通知
}
```

**注意**：当前 Web 版本（`web_monitor.py`）只要状态变更就会通知，不完全遵循这些配置。

---

## 📊 代码实现总结

### monitor.py（后台监控）
```python
# 判断是否首次查询
is_first_check = url not in self.order_history

# 状态变更或首次查询到取消状态时发送通知
if changed and not is_first_check:
    # 非首次，状态变更
    if self.should_notify(new_status, changed=True):
        send_notification()
        
elif is_first_check and new_status in ['CANCELED', 'CANCELLED']:
    # 首次查询就是取消状态
    send_notification()
```

### web_monitor.py（Web 监控）
```python
if url in self.results:
    # 有历史记录 - 检查状态变更
    if old_status != new_status and 都是有效状态:
        send_notification()
else:
    # 没有历史记录 - 只有取消状态才通知
    if result.get('status') == 'CANCELED':
        send_notification()
```

---

## 🤔 常见问题

### Q1: 为什么首次查询 PROCESSING 不通知？
**A**: 因为这是正常的初始状态，不需要提醒。只有异常的 CANCELED 状态才需要立即知道。

### Q2: 已经送达的订单还会通知吗？
**A**: 不会。`DELIVERED` 和 `CANCELED` 是终态，系统会跳过查询，不会再发通知。

### Q3: 我想每次查询都通知，怎么改？
**A**: 需要修改代码逻辑。不过不建议这样做，会产生大量重复通知。

### Q4: 多个机器人会收到重复通知吗？
**A**: 是的。所有启用的机器人都会收到同样的通知。这是设计行为，用于确保不同的人都能收到。

---

## 🎉 总结

### 会通知的情况：
1. ✅ 首次查询就是 CANCELED
2. ✅ 状态从任何状态变更为 CANCELED
3. ✅ 状态从 PROCESSING 变更为 SHIPPED
4. ✅ 状态从 SHIPPED 变更为 DELIVERED
5. ✅ 任何有效状态的变更

### 不会通知的情况：
1. ❌ 首次查询是 PROCESSING、SHIPPED、DELIVERED
2. ❌ 状态未发生变化
3. ❌ 查询失败
4. ❌ 已完成的订单（不再查询）

简单来说：**有意义的状态变化才通知**！ 😊
