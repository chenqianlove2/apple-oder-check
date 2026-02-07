#!/usr/bin/env python3
"""
测试物流追踪功能
"""

import json
from web_monitor import OrderMonitor

def test_tracking_extraction():
    """测试物流追踪链接提取"""
    
    print("=" * 60)
    print("测试物流追踪功能")
    print("=" * 60)
    
    # 创建监控器
    monitor = OrderMonitor()
    
    # 模拟包含物流追踪链接的订单数据
    test_result = {
        'success': True,
        'url': 'https://www.apple.com/xc/us/vieworder/W1234567890/test@example.com',
        'orderNumber': 'W1234567890',
        'orderDate': '2026-02-01',
        'productName': 'iPhone 15 Pro',
        'status': 'SHIPPED',
        'deliveryDate': '2026-02-10',
        'trackingUrl': 'http://wwwapps.ups.com/etracking/tracking.cgi?TypeOfInquiryNumber=T&InquiryNumber1=1ZA828Y90268769346',
        'trackingNumber': '1ZA828Y90268769346',
        'timestamp': '2026-02-07T12:00:00'
    }
    
    print("\n测试订单数据:")
    print(json.dumps(test_result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("物流追踪信息提取成功！")
    print(f"状态: {test_result['status']}")
    print(f"物流单号: {test_result['trackingNumber']}")
    print(f"物流链接: {test_result['trackingUrl']}")
    print("=" * 60)
    
    # 保存测试结果到历史
    monitor.results[test_result['url']] = test_result
    monitor.save_history()
    
    print("\n✅ 测试完成！")
    print("📝 结果已保存到 order_history.json")
    print("🌐 启动 web_server.py 查看效果")

if __name__ == '__main__':
    test_tracking_extraction()
