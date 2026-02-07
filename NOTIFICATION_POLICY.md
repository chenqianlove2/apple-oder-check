# 智能通知策略说明

## 📢 通知规则 (已更新)

### ✅ 会发送 Telegram 通知的情况

#### 1. 已存在订单的状态变化
任何状态变化都会发送通知：

- `PLACED` → `PROCESSING` ⚙️
- `PROCESSING` → `PREPARED_FOR_SHIPMENT` 📋  
- `PREPARED_FOR_SHIPMENT` → `SHIPPED` 📦
- `SHIPPED` → `DELIVERED` ✅
- 任何状态 → `CANCELED` 🚨
- 以及其他任何状态转换

**通知示例：**
```
📦 订单状态变更

订单号: W123456789
产品: iPhone 15 Pro Max
旧状态: PROCESSING
新状态: SHIPPED
物流单号: 1Z999AA10123456784
时间: 2024-01-15 14:30:00
```

#### 2. 新订单首次查询为 CANCELED
如果新添加的订单第一次查询就是取消状态，会发送通知：

**通知示例：**
```
🚨 新订单已取消

订单号: W987654321
产品: MacBook Pro 16"
状态: CANCELED
时间: 2024-01-15 10:15:00
```

### ❌ 不会发送通知的情况

#### 1. 新订单首次查询（非CANCELED状态）
新添加的订单第一次查询时，如果不是CANCELED状态，不会发送通知。

**示例：**
- 添加新订单，首次查询状态为 `PLACED` → 不通知
- 添加新订单，首次查询状态为 `PROCESSING` → 不通知  
- 添加新订单，首次查询状态为 `SHIPPED` → 不通知

#### 2. 状态没有变化
如果订单状态没有变化，不会发送通知。

## 📊 通知策略对比

| 场景 | 旧策略 | 新策略 |
|------|--------|--------|
| 新订单首次查询 (PLACED) | ❌ 不通知 | ❌ 不通知 |
| 新订单首次查询 (CANCELED) | ❌ 不通知 | ✅ **通知** |
| 已有订单 PLACED → PROCESSING | ✅ 通知 | ✅ 通知 |
| 已有订单 PROCESSING → SHIPPED | ✅ 通知 | ✅ 通知 |
| 已有订单任何状态 → CANCELED | ✅ 通知 | ✅ 通知 |
| 状态无变化 | ❌ 不通知 | ❌ 不通知 |

## 🎯 实际使用场景

### 场景 1: 批量导入订单
```bash
# 导入 50 个订单
添加订单 → 启动监控 → 首次查询
```

**结果：**
- 48 个订单状态正常 (PLACED/PROCESSING/SHIPPED) → 不发送通知
- 2 个订单已取消 (CANCELED) → **发送 2 条通知** 🚨

**日志输出：**
```
📥 首次查询订单 W111111111，状态: PLACED（不发送通知）
📥 首次查询订单 W222222222，状态: PROCESSING（不发送通知）
🚨 首次查询订单 W333333333，状态: CANCELED，发送通知 ✅
📥 首次查询订单 W444444444，状态: SHIPPED（不发送通知）
🚨 首次查询订单 W555555555，状态: CANCELED，发送通知 ✅
...
```

### 场景 2: 订单状态发生变化
```bash
# 监控运行中
第一次检查: PLACED
第二次检查: PROCESSING (状态变化)
```

**结果：**
- 检测到状态变化 → **发送通知** ⚙️

**日志输出：**
```
⚙️ 订单 W123456789 状态变更: PLACED → PROCESSING，发送通知
```

### 场景 3: 订单被取消
```bash
# 监控运行中
之前状态: PROCESSING
当前状态: CANCELED (状态变化)
```

**结果：**
- 检测到订单取消 → **发送通知** 🚨

**日志输出：**
```
🚨 订单 W987654321 状态变更: PROCESSING → CANCELED，发送通知
```

### 场景 4: 订单发货
```bash
# 监控运行中
之前状态: PREPARED_FOR_SHIPMENT
当前状态: SHIPPED (状态变化)
```

**结果：**
- 检测到订单发货 → **发送通知** 📦
- 通知中包含物流单号

**日志输出：**
```
📦 订单 W666666666 状态变更: PREPARED_FOR_SHIPMENT → SHIPPED，发送通知
```

## 🔧 技术实现

### check_one() 函数逻辑

```python
def check_one(url):
    result = self.query_order(url)
    
    if url in self.results:
        # 已存在的订单 - 检查状态变化
        old_status = self.results[url].get('status')
        new_status = result.get('status')
        
        if old_status != new_status and result.get('success'):
            # 状态发生变化 → 发送通知
            notifier.send_order_notification(result, old_status)
            print(f"📢 订单状态变更: {old_status} → {new_status}，发送通知")
    else:
        # 新订单首次查询
        if result.get('success') and result.get('status') == 'CANCELED':
            # 首次查询就是 CANCELED → 发送通知
            notifier.send_order_notification(result, None)
            print(f"🚨 首次查询订单，状态: CANCELED，发送通知")
        else:
            # 其他状态 → 不发送通知
            print(f"📥 首次查询订单，状态: {result.get('status')}（不发送通知）")
    
    self.results[url] = result
    return result
```

## 💡 设计理由

### 为什么首次查询 CANCELED 要通知？

1. **重要性**：取消订单是需要特别关注的异常情况
2. **及时性**：用户需要尽快知道订单被取消
3. **实用性**：批量导入订单时，可以立即发现问题订单

### 为什么其他状态首次查询不通知？

1. **避免通知轰炸**：批量导入50个订单，不会收到50条通知
2. **更有意义**：状态变化比初始状态更重要
3. **更清晰**：只关注订单的动态变化

## 🎨 状态表情符号

| 状态 | 表情 | 说明 |
|------|------|------|
| CANCELED | 🚨 | 订单已取消 |
| SHIPPED | 📦 | 已发货 |
| DELIVERED | ✅ | 已送达 |
| PROCESSING | ⚙️ | 处理中 |
| PREPARED_FOR_SHIPMENT | 📋 | 准备发货 |
| PLACED | 📝 | 已下单 |
| 其他 | 📢 | 通用通知 |

## ⚙️ 配置说明

在 `telegram_config.json` 中配置：

```json
{
  "bot_token": "你的_BOT_TOKEN",
  "chat_id": "你的_CHAT_ID"
}
```

确保 Telegram 通知已启用，否则不会发送任何通知。

## 🔍 测试方法

### 测试1: 添加已取消的订单
```bash
# 在监控面板添加一个已取消的订单
→ 应该收到 Telegram 通知 🚨
```

### 测试2: 添加正常订单
```bash
# 在监控面板添加一个 PLACED 状态的订单
→ 不应该收到通知
→ 日志显示"📥 首次查询订单...（不发送通知）"
```

### 测试3: 等待状态变化
```bash
# 等待订单状态从 PLACED 变为 PROCESSING
→ 应该收到通知 ⚙️
→ 日志显示"⚙️ 订单状态变更: PLACED → PROCESSING，发送通知"
```

## 📝 更新日志

### 2024-01-15 v2.1
- ✅ 新增：首次查询为 CANCELED 时发送通知
- ✅ 保持：已有订单的任何状态变化都发送通知
- ✅ 保持：首次查询非 CANCELED 状态不发送通知
- ✅ 优化：更清晰的日志输出和表情符号

### 2024-01-15 v2.0
- ✅ 修改通知策略：所有状态变化都发送通知
- ✅ 首次查询订单不发送通知
- ✅ 添加状态表情符号

### 2024-01-15 v1.0
- ✅ 实现智能订单筛选逻辑
- ✅ 添加待检查订单统计
