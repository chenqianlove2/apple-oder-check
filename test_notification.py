#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试新的通知策略"""

from web_monitor import get_monitor
from notifier import get_notifier
import json

def test_notification_policy():
    """测试通知策略：
    1. 第一次查询不通知
    2. 状态变化才通知
    """
    
    m = get_monitor()
    notifier = get_notifier()
    
    print("=" * 60)
    print("通知策略测试")
    print("=" * 60)
    print(f"Telegram 启用: {notifier.enabled}\n")
    
    # 读取当前结果
    with open('order_history.json', 'r') as f:
        data = json.load(f)
        results = data.get('results', {})
    
    # 统计不同状态的订单
    status_counts = {}
    for url, result in results.items():
        status = result.get('status', 'unknown')
        if status not in status_counts:
            status_counts[status] = []
        status_counts[status].append({
            'orderNumber': result.get('orderNumber'),
            'url': url
        })
    
    print("当前订单状态分布:")
    for status, orders in status_counts.items():
        print(f"  {status}: {len(orders)} 个订单")
        if len(orders) <= 3:
            for order in orders:
                print(f"    - {order['orderNumber']}")
    
    print("\n" + "=" * 60)
    print("通知规则说明:")
    print("=" * 60)
    print("✅ 会发送通知的情况:")
    print("  - PLACED → PROCESSING")
    print("  - PROCESSING → PREPARED_FOR_SHIPMENT")
    print("  - PREPARED_FOR_SHIPMENT → SHIPPED")
    print("  - SHIPPED → DELIVERED")
    print("  - 任何状态 → CANCELED")
    print("  - 以及任何其他状态变化")
    print("\n❌ 不会发送通知的情况:")
    print("  - 第一次查询订单（无论什么状态）")
    print("  - 状态没有变化")
    
    print("\n" + "=" * 60)
    print("测试场景:")
    print("=" * 60)
    
    # 场景1: 查找一个已有订单
    if results:
        test_url = list(results.keys())[0]
        test_result = results[test_url]
        print(f"\n场景1: 已存在的订单")
        print(f"  订单号: {test_result.get('orderNumber')}")
        print(f"  当前状态: {test_result.get('status')}")
        print(f"  结果: 如果状态变化 → 会发送通知 ✅")
        print(f"       如果状态不变 → 不发送通知 ❌")
    
    # 场景2: 新订单
    print(f"\n场景2: 新添加的订单")
    print(f"  结果: 第一次查询 → 不发送通知 ❌")
    print(f"       下次状态变化 → 会发送通知 ✅")
    
    # 场景3: 取消的订单
    print(f"\n场景3: 订单被取消")
    print(f"  PLACED → CANCELED → 发送通知 🚨")
    print(f"  PROCESSING → CANCELED → 发送通知 🚨")
    print(f"  SHIPPED → CANCELED → 发送通知 🚨")
    
    # 场景4: 正常流程
    print(f"\n场景4: 订单正常流程")
    print(f"  PLACED → PROCESSING → 发送通知 ⚙️")
    print(f"  PROCESSING → PREPARED_FOR_SHIPMENT → 发送通知 📋")
    print(f"  PREPARED_FOR_SHIPMENT → SHIPPED → 发送通知 📦")
    print(f"  SHIPPED → DELIVERED → 发送通知 ✅")
    
    print("\n" + "=" * 60)
    print("提示：启动监控后，任何状态变化都会自动发送 Telegram 通知")
    print("=" * 60)

if __name__ == '__main__':
    test_notification_policy()
