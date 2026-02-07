#!/usr/bin/env python3
"""
测试从实际订单提取物流单号
"""

from web_monitor import OrderMonitor
import json

# 创建监控器
monitor = OrderMonitor()

# 读取已有的订单历史
print("=" * 60)
print("检查订单历史中的物流追踪信息")
print("=" * 60)

if monitor.results:
    for url, result in list(monitor.results.items())[:5]:  # 只显示前5个
        print(f"\n订单: {result.get('orderNumber', 'N/A')}")
        print(f"状态: {result.get('status', 'N/A')}")
        print(f"物流单号: {result.get('trackingNumber', '-')}")
        print(f"物流链接: {result.get('trackingUrl', '-')}")
        print("-" * 60)
else:
    print("\n没有订单历史数据")

print("\n提示: 订单状态为 SHIPPED 时才会有物流信息")
