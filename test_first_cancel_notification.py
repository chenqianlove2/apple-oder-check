#!/usr/bin/env python3
"""
测试首次查询取消订单的通知功能
"""

from notifier import get_notifier
from datetime import datetime

def test_first_check_canceled():
    """测试首次查询到取消订单的通知"""
    
    # 模拟订单查询结果
    result = {
        'success': True,
        'url': 'https://www.apple.com/xc/us/vieworder/W1234567890/test@example.com',
        'orderNumber': 'W1234567890',
        'orderDate': '2026-01-15',
        'productName': 'iPhone 15 Pro Max 256GB Natural Titanium',
        'status': 'CANCELED',
        'deliveryDate': '-',
        'timestamp': datetime.now().isoformat()
    }
    
    print("=" * 60)
    print("测试场景 1：首次查询发现订单已取消")
    print("=" * 60)
    
    notifier = get_notifier()
    
    # 检查是否有启用的机器人
    enabled_bots = notifier.get_enabled_bots()
    if not enabled_bots:
        print("❌ 没有启用的 Telegram 机器人")
        print("请先在 http://127.0.0.1:8846/settings 添加机器人")
        return
    
    print(f"✅ 找到 {len(enabled_bots)} 个启用的机器人:")
    for bot in enabled_bots:
        print(f"   - {bot['name']} (Chat ID: {bot['chat_id']})")
    
    print("\n📤 发送通知...")
    
    # 首次查询（old_status = None）
    success, msg = notifier.send_order_notification(result, old_status=None)
    
    if success:
        print(f"✅ {msg}")
        print("\n📱 请检查您的 Telegram，应该收到带有以下内容的消息：")
        print("   🚨🚨 【重要警告：订单已取消】 🚨🚨")
        print("   状态变更: ⚠️ 首次查询发现 → ❌ Canceled")
    else:
        print(f"❌ 发送失败: {msg}")
    
    print("\n" + "=" * 60)
    print("测试场景 2：状态变更为取消（非首次）")
    print("=" * 60)
    
    # 状态变更（有旧状态）
    success, msg = notifier.send_order_notification(result, old_status='PROCESSING')
    
    if success:
        print(f"✅ {msg}")
        print("\n📱 请检查您的 Telegram，应该收到带有以下内容的消息：")
        print("   🚨 【订单已取消】")
        print("   状态变更: ⏳ Processing → ❌ Canceled")
    else:
        print(f"❌ 发送失败: {msg}")
    
    print("\n" + "=" * 60)
    print("测试场景 3：首次查询正常订单（不发送通知）")
    print("=" * 60)
    
    result_normal = result.copy()
    result_normal['status'] = 'PROCESSING'
    result_normal['orderNumber'] = 'W9876543210'
    
    print("📝 首次查询到 PROCESSING 状态的订单")
    print("   （这种情况不会发送通知，除非后续状态变更）")
    
    # 这个通知会发送，但显示为"新订单"
    success, msg = notifier.send_order_notification(result_normal, old_status=None)
    if success:
        print(f"✅ {msg}")
        print("   （虽然会发送，但显示为'新订单'，不是紧急警告）")

if __name__ == '__main__':
    print("\n🧪 测试首次查询取消订单通知功能\n")
    
    try:
        test_first_check_canceled()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 测试完成！")
