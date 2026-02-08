# Bug 修复说明

## 修复日期
2024年

## 修复的问题

### 1. 检查次数不更新的问题

**问题描述:**
- 点击"立即检查"按钮后,网页显示的检查次数保持不变
- 实际上后台已经执行了检查,但数据没有持久化

**根本原因:**
`web_monitor.py` 中的 `save_history()` 和 `load_history()` 方法没有保存/加载 `check_count` 和 `last_check_time` 字段。

**修复内容:**

1. **修改 `save_history()` 方法** (web_monitor.py:79-92)
```python
def save_history(self):
    try:
        with open(self.history_file, 'w') as f:
            json.dump({
                'results': self.results,
                'changes': self.status_changes[-100:],
                'last_check_time': self.last_check_time,  # ✅ 新增
                'check_count': self.check_count,           # ✅ 新增
                'last_save': datetime.now().isoformat()
            }, f, indent=2)
        return True
    except Exception as e:
        print(f"保存历史失败: {e}")
        return False
```

2. **修改 `load_history()` 方法** (web_monitor.py:69-78)
```python
def load_history(self):
    if os.path.exists(self.history_file):
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                self.results = data.get('results', {})
                self.status_changes = data.get('changes', [])
                self.last_check_time = data.get('last_check_time', None)  # ✅ 新增
                self.check_count = data.get('check_count', 0)             # ✅ 新增
        except Exception as e:
            print(f"加载历史失败: {e}")
```

### 2. 页面刷新时机问题

**问题描述:**
- 点击"立即检查"后,页面固定等待2秒后刷新
- 如果检查操作需要超过2秒,页面会在检查完成前刷新,导致看不到更新

**根本原因:**
`checkNow()` 函数使用固定的2秒延迟,不会等待后台检查线程完成。

**修复内容:**

修改 `web_server.py` 中的 `checkNow()` 函数,改为轮询等待检查完成:

```javascript
async function checkNow() {
    const btn = document.getElementById('checkBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="refreshing">🔄</span> 检查中...';
    
    try {
        // 获取检查前的状态
        const beforeRes = await fetch('/api/monitor/status');
        const beforeStatus = await beforeRes.json();
        const beforeCheckCount = beforeStatus.checkCount;
        
        // 触发检查
        await fetch('/api/monitor/check', {method: 'POST'});
        
        // 轮询等待检查完成（最多等待15秒）
        let attempts = 0;
        const maxAttempts = 30; // 30次 * 500ms = 15秒
        
        const pollForUpdate = async () => {
            attempts++;
            const statusRes = await fetch('/api/monitor/status');
            const status = await statusRes.json();
            
            // 如果 checkCount 增加了，说明检查完成
            if (status.checkCount > beforeCheckCount || attempts >= maxAttempts) {
                await refreshData();
                btn.disabled = false;
                btn.innerHTML = '🔄 立即检查';
                
                if (attempts >= maxAttempts) {
                    console.log('检查超时，但仍刷新了数据');
                } else {
                    console.log(`检查完成，用时约 ${attempts * 0.5} 秒`);
                }
            } else {
                // 继续等待
                setTimeout(pollForUpdate, 500);
            }
        };
        
        // 开始轮询
        setTimeout(pollForUpdate, 500);
        
    } catch (e) {
        alert('检查失败: ' + e);
        btn.disabled = false;
        btn.innerHTML = '🔄 立即检查';
    }
}
```

**改进点:**
- ✅ 页面会轮询检查 `checkCount` 是否增加
- ✅ 每500毫秒检查一次状态
- ✅ 最多等待15秒(30次 × 500ms)
- ✅ 检查完成后立即刷新页面,用户能第一时间看到更新

### 3. 增强状态变更日志

**问题描述:**
- 难以调试为什么某些状态变更没有触发通知

**修复内容:**

在 `web_monitor.py` 的 `check_one()` 函数中增加详细的调试日志:

```python
def check_one(url):
    result = self.query_order(url)
    
    # 检查状态变化
    if url in self.results:
        old_status = self.results[url].get('status')
        new_status = result.get('status')
        
        # ✅ 新增: 详细的状态日志
        print(f"📊 检查订单: {result.get('orderNumber')}, 旧状态={old_status}, 新状态={new_status}, 查询成功={result.get('success')}")
        
        valid_statuses = ['PLACED', 'PROCESSING', 'PREPARED_FOR_SHIPMENT', 'SHIPPED', 'DELIVERED', 'CANCELED']
        old_valid = old_status in valid_statuses
        new_valid = new_status in valid_statuses
        
        # ✅ 新增: 验证状态的日志
        print(f"   旧状态有效={old_valid}, 新状态有效={new_valid}, 状态是否变化={old_status != new_status}")
        
        if (old_status != new_status and 
            result.get('success') and 
            old_valid and 
            new_valid):
            # ... 发送通知 ...
            
            # ✅ 修改: 显示发送到几个机器人
            print(f"{emoji} 订单 {result.get('orderNumber')} 状态变更: {old_status} → {new_status}，发送通知到 {len(enabled_bots)} 个机器人")
```

## 验证方法

### 测试检查次数更新:
1. 访问 http://127.0.0.1:8846
2. 查看当前检查次数(例如: 3次)
3. 点击"🔄 立即检查"按钮
4. 等待按钮从"检查中..."恢复为"🔄 立即检查"
5. ✅ 检查次数应该变为 4次

### 测试状态变更通知:
1. 确保至少有一个 Telegram 机器人已启用
2. 手动修改 `order_history.json` 中某个订单的状态
3. 点击"🔄 立即检查"
4. ✅ 查看终端日志,应该看到类似:
   ```
   📊 检查订单: W1502219461, 旧状态=PLACED, 新状态=PROCESSING, 查询成功=True
      旧状态有效=True, 新状态有效=True, 状态是否变化=True
   ⚙️ 订单 W1502219461 状态变更: PLACED → PROCESSING，发送通知到 1 个机器人
   ```
5. ✅ Telegram 应该收到通知消息

## 影响范围
- ✅ 修复了检查次数持久化
- ✅ 修复了页面刷新时机
- ✅ 增强了调试能力
- ✅ 不影响现有功能
- ✅ 向后兼容旧的 `order_history.json` 格式

## 相关文件
- `web_monitor.py` - 修改了 `save_history()`, `load_history()`, `check_one()`
- `web_server.py` - 修改了 `checkNow()` JavaScript 函数

## 注意事项
1. 旧的 `order_history.json` 文件不包含 `check_count` 和 `last_check_time`,加载时会使用默认值(0 和 None)
2. 第一次检查后,这些字段会被正确保存
3. 轮询检查最多等待15秒,对于大量订单可能需要调整 `maxAttempts` 值
