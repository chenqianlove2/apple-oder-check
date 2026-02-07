#!/usr/bin/env python3
"""
测试批量查询功能
"""

from web_monitor import OrderMonitor

# 测试订单 URL（从截图中提取）
test_urls = [
    'https://www.apple.com/xc/us/vieworder/W1342476105/uoscknyk83918@outlook.com',
    'https://www.apple.com/xc/us/vieworder/W1470730058/goolriaw26233@outlook.com',
    'https://www.apple.com/xc/us/vieworder/W1313769919/hozykaep58971@outlook.com',
]

monitor = OrderMonitor()

print("=" * 60)
print("测试批量查询")
print("=" * 60)

for i, url in enumerate(test_urls[:2], 1):  # 只测试前2个
    print(f"\n[{i}] 查询订单: {url.split('/')[-2]}")
    try:
        result = monitor.query_order(url)
        if result.get('success'):
            print(f"  ✅ 成功")
            print(f"  订单号: {result.get('orderNumber', '-')}")
            print(f"  状态: {result.get('status', '-')}")
            print(f"  产品: {result.get('productName', '-')}")
        else:
            print(f"  ❌ 失败")
            print(f"  错误: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"  ❌ 异常: {str(e)}")
    print("-" * 60)

print("\n测试完成")
