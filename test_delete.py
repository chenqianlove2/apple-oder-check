#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试删除功能"""

from web_monitor import get_monitor

def test_delete():
    monitor = get_monitor()
    
    # 获取当前订单
    orders = monitor.get_orders()
    print(f"当前订单数: {len(orders)}")
    
    if orders:
        print(f"\n前3个订单:")
        for i, url in enumerate(orders[:3]):
            print(f"{i+1}. {url}")
        
        # 测试删除第一个订单
        test_url = orders[0]
        print(f"\n尝试删除: {test_url}")
        success, msg = monitor.delete_order(test_url)
        print(f"结果: {success}, {msg}")
        
        # 验证
        orders_after = monitor.get_orders()
        print(f"删除后订单数: {len(orders_after)}")
        print(f"订单是否存在: {test_url in orders_after}")
        
        # 恢复订单
        print(f"\n恢复订单...")
        monitor.add_order(test_url)
        orders_restored = monitor.get_orders()
        print(f"恢复后订单数: {len(orders_restored)}")

if __name__ == '__main__':
    test_delete()
