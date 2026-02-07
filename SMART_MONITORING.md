# 智能监控功能说明

## 功能概述

智能监控系统会根据订单信息的完整性,自动决定是否需要重新查询订单,避免浪费资源重复查询已完整的订单信息。

## 核心特性

### 1. 智能筛选 - 只查询不完整的订单

监控系统会自动识别以下订单需要查询:

- **从未查询过的订单**: 第一次加入监控的订单
- **查询失败的订单**: 上次查询时返回 `success: false` 的订单
- **信息不完整的订单**: 关键字段为空或为 `-` 的订单
  - `orderNumber` 为空或为 `-`
  - `productName` 为空或为 `-`
  - `status` 为空或为 `-`

### 2. 高效轮询策略

```
┌─────────────────────────────────────────┐
│  启动监控                                 │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  检查所有订单,识别不完整订单              │
└────────────┬────────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ 有不完整订单? │
      └──────┬───────┘
             │
        ┌────┴────┐
        │ 是      │ 否
        ▼         ▼
  ┌──────────┐  ┌──────────────────┐
  │查询不完整│  │跳过查询,所有订单 │
  │的订单    │  │信息已完整         │
  └────┬─────┘  └──────────────────┘
       │
       ▼
  ┌──────────────────────────┐
  │  等待 5 分钟后下一轮检查  │
  └──────────────────────────┘
```

### 3. 智能通知 - 所有状态变化都通知

通知策略:
- ✅ **发送通知**: 订单状态发生任何变化时
  - PLACED → PROCESSING
  - PROCESSING → PREPARED_FOR_SHIPMENT
  - PREPARED_FOR_SHIPMENT → SHIPPED
  - SHIPPED → DELIVERED
  - 任何状态 → CANCELED
- ❌ **不发送通知**: 第一次查询订单时（无论什么状态）
- 📝 **状态变更记录**: 所有变更都会记录在日志中

通知示例:
```
🚨 订单 W123456789 状态变更: PLACED → CANCELED
产品: iPhone 15 Pro Max
时间: 2024-01-15 10:30:45

📦 订单 W987654321 状态变更: PROCESSING → SHIPPED
产品: MacBook Pro 16"
物流单号: 1Z999AA10123456784
时间: 2024-01-15 14:20:30
```

状态表情符号:
- 🚨 CANCELED - 订单已取消
- 📦 SHIPPED - 已发货
- ✅ DELIVERED - 已送达
- ⚙️ PROCESSING - 处理中
- 📋 PREPARED_FOR_SHIPMENT - 准备发货
- 📝 PLACED - 已下单
- 📢 其他状态

## 实现细节

### check_all_orders() 核心逻辑

```python
def check_all_orders(self):
    """智能检查所有订单"""
    # 1. 获取所有订单
    orders = self.get_orders()
    
    # 2. 识别需要查询的订单
    orders_to_check = []
    for url in orders:
        # 从未查询过
        if url not in self.results:
            orders_to_check.append(url)
            continue
        
        prev_result = self.results[url]
        
        # 查询失败
        if not prev_result.get('success'):
            orders_to_check.append(url)
            continue
        
        # 信息不完整
        if (prev_result.get('orderNumber') in ['-', None, ''] or
            prev_result.get('productName') in ['-', None, ''] or
            prev_result.get('status') in ['-', None, '']):
            orders_to_check.append(url)
            continue
    
    # 3. 如果没有需要查询的订单,直接返回
    if not orders_to_check:
        print("✅ 所有订单信息已完整,无需查询")
        return []
    
    # 4. 查询需要检查的订单
    print(f"🔍 开始查询 {len(orders_to_check)} 个订单...")
    with ThreadPoolExecutor(max_workers=self.config['threads']) as executor:
        results = list(executor.map(check_one, orders_to_check))
    
    return results
```

### 状态检测与通知

```python
def check_one(url):
    result = self.query_order(url)
    
    # 检查状态变化
    if url in self.results:
        old_status = self.results[url].get('status')
        new_status = result.get('status')
        
        # 只要状态发生变化就发送通知
        if old_status != new_status and result.get('success'):
            # 记录状态变化
            self.status_changes.append({...})
            
            # 发送 Telegram 通知（所有状态变化）
            notifier.send_order_notification(result, old_status)
            print(f"📢 订单状态变更: {old_status} → {new_status}，发送通知")
    else:
        # 第一次查询该订单，不发送通知
        print(f"� 首次查询订单，状态: {new_status}（不发送通知）")
    
    self.results[url] = result
    return result
```

## 前端显示

### 状态面板显示

监控运行时会显示:
- **智能检查中**: `智能检查中 (已完成数/待检查数)` 
  - 例如: "智能检查中 (5/10)"
- **监控轮询中**: 所有订单信息完整时显示

### 状态 API 返回

`/api/monitor/status` 接口增加字段:
```json
{
  "running": true,
  "pendingOrders": 10,      // 待检查订单数
  "checkedOrders": 45,      // 已完整订单数
  "totalOrders": 55,
  "lastCheck": "2024-01-15T10:30:45",
  "checkCount": 123
}
```

## 性能优化

### 优化前后对比

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 50个订单,45个完整 | 查询50个 | 查询5个 | **90%减少** |
| 100个订单,95个完整 | 查询100个 | 查询5个 | **95%减少** |
| 所有订单完整 | 查询全部 | 跳过查询 | **100%节省** |

### 资源节省

- ⚡ **减少网络请求**: 只查询必要的订单
- 🔋 **降低服务器负载**: Apple服务器压力减小
- ⏱️ **加快响应速度**: 查询时间大幅缩短
- 🛡️ **降低封禁风险**: 请求频率降低

## 使用场景

### 场景 1: 初次启动

```
总订单: 50个
需要查询: 50个 (全部未查询过)
动作: 查询所有订单
```

### 场景 2: 部分订单信息不完整

```
总订单: 50个
已完整: 45个
需要查询: 5个 (信息不完整)
动作: 只查询这5个订单
性能: 节省90%查询
```

### 场景 3: 所有订单信息完整

```
总订单: 50个
已完整: 50个
需要查询: 0个
动作: 跳过查询,直接进入下一轮轮询
性能: 节省100%查询
```

### 场景 4: 订单被取消

```
订单状态变化: PLACED → CANCELED
动作: 
1. 检测到状态变化
2. 发送 Telegram 通知
3. 记录状态变更日志
4. 更新订单结果
```

## 日志输出

### 智能检查日志

```bash
📊 总订单数: 50, 需要查询: 5, 已完成: 45
🔍 开始查询 5 个订单...
� 首次查询订单 W123456789，状态: PLACED（不发送通知）
📦 订单 W987654321 状态变更: PROCESSING → SHIPPED，发送通知
⚙️ 订单 W555555555 状态变更: PLACED → PROCESSING，发送通知
✅ 所有订单信息已完整,无需查询
```

### 状态变更通知日志

```bash
� 订单 W987654321 状态变更: PROCESSING → SHIPPED，发送通知
🚨 订单 W111111111 状态变更: PLACED → CANCELED，发送通知
📋 订单 W222222222 状态变更: PROCESSING → PREPARED_FOR_SHIPMENT，发送通知
```

## 配置说明

在 `monitor_config.json` 中配置:

```json
{
  "interval": 300,          // 轮询间隔 (秒)
  "threads": 5,             // 并发线程数
  "check_on_startup": true  // 启动时立即检查
}
```

## 兼容性

- ✅ 向后兼容之前的订单数据
- ✅ 支持所有订单状态
- ✅ 自动修复不完整的历史数据
- ✅ 支持批量查询和单个重检

## 注意事项

1. **首次运行**: 第一次启动监控时会查询所有订单,建立完整数据库，但不会发送通知
2. **网络异常**: 查询失败的订单会在下一轮自动重试
3. **状态变更通知**: 任何状态变化都会发送 Telegram 消息（PLACED→PROCESSING、PROCESSING→SHIPPED、→CANCELED等）
4. **首次查询不通知**: 新添加的订单第一次查询时不发送通知，只有状态发生变化时才通知
5. **轮询间隔**: 建议设置为 5 分钟 (300秒) 以避免频繁请求

## 更新日志

### 2024-01-15 v2.0
- ✅ 修改通知策略：所有状态变化都发送通知
- ✅ 首次查询订单不发送通知
- ✅ 添加状态表情符号区分不同状态变化
- ✅ 优化日志输出，更清晰地显示通知状态

### 2024-01-15 v1.0
- ✅ 实现智能订单筛选逻辑
- ✅ 添加待检查订单统计
- ✅ 更新前端状态显示
- ✅ 添加详细日志输出
