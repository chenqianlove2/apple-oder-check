#!/usr/bin/env python3
"""
测试脚本：演示什么情况下会推送 Telegram 通知
"""

def print_scenario(title, description, will_notify, reason):
    """打印测试场景"""
    emoji = "✅ 会通知" if will_notify else "❌ 不通知"
    print(f"\n{'='*60}")
    print(f"📋 场景: {title}")
    print(f"{'='*60}")
    print(f"说明: {description}")
    print(f"\n结果: {emoji}")
    print(f"原因: {reason}")


def main():
    print("\n" + "="*60)
    print("🧪 Telegram 通知推送测试场景")
    print("="*60)
    
    # 场景 1：首次查询
    print("\n\n📌 第一组：首次查询场景")
    
    print_scenario(
        "首次查询 - PROCESSING",
        "新添加的订单，第一次查询，状态是 PROCESSING",
        will_notify=False,
        reason="首次查询且是正常状态，不需要通知"
    )
    
    print_scenario(
        "首次查询 - SHIPPED",
        "新添加的订单，第一次查询，状态是 SHIPPED",
        will_notify=False,
        reason="首次查询且是正常状态，不需要通知"
    )
    
    print_scenario(
        "首次查询 - DELIVERED",
        "新添加的订单，第一次查询，状态是 DELIVERED",
        will_notify=False,
        reason="首次查询且是正常状态，不需要通知"
    )
    
    print_scenario(
        "首次查询 - CANCELED ⚠️",
        "新添加的订单，第一次查询，状态是 CANCELED",
        will_notify=True,
        reason="🚨 首次查询就是取消状态！需要立即通知！"
    )
    
    # 场景 2：状态变更
    print("\n\n📌 第二组：状态变更场景")
    
    print_scenario(
        "状态变更 - PROCESSING → SHIPPED",
        "之前是 PROCESSING，现在变成 SHIPPED",
        will_notify=True,
        reason="状态发生变更，需要通知"
    )
    
    print_scenario(
        "状态变更 - SHIPPED → DELIVERED",
        "之前是 SHIPPED，现在变成 DELIVERED",
        will_notify=True,
        reason="状态发生变更，需要通知"
    )
    
    print_scenario(
        "状态变更 - PROCESSING → CANCELED ⚠️",
        "之前是 PROCESSING，现在变成 CANCELED",
        will_notify=True,
        reason="🚨 订单被取消！需要紧急通知！"
    )
    
    print_scenario(
        "状态变更 - SHIPPED → CANCELED ⚠️",
        "之前是 SHIPPED，现在变成 CANCELED",
        will_notify=True,
        reason="🚨 已发货订单被取消！需要紧急通知！"
    )
    
    # 场景 3：状态未变化
    print("\n\n📌 第三组：状态未变化场景")
    
    print_scenario(
        "状态未变 - PROCESSING → PROCESSING",
        "之前是 PROCESSING，现在还是 PROCESSING",
        will_notify=False,
        reason="状态没有变化，不需要重复通知"
    )
    
    print_scenario(
        "状态未变 - SHIPPED → SHIPPED",
        "之前是 SHIPPED，现在还是 SHIPPED",
        will_notify=False,
        reason="状态没有变化，不需要重复通知"
    )
    
    # 场景 4：查询失败
    print("\n\n📌 第四组：异常场景")
    
    print_scenario(
        "查询失败",
        "网络错误或订单不存在，查询失败",
        will_notify=False,
        reason="查询失败，无法获取有效状态，不通知"
    )
    
    print_scenario(
        "无效状态 - '-' → '-'",
        "两次查询都返回无效状态",
        will_notify=False,
        reason="状态无效，不是有效的订单状态，不通知"
    )
    
    # 场景 5：终态订单
    print("\n\n📌 第五组：终态订单")
    
    print_scenario(
        "已送达订单",
        "订单状态是 DELIVERED，系统跳过查询",
        will_notify=False,
        reason="已送达是终态，系统不再查询此订单"
    )
    
    print_scenario(
        "已取消订单",
        "订单状态是 CANCELED，系统跳过查询",
        will_notify=False,
        reason="已取消是终态，系统不再查询此订单"
    )
    
    # 实际时间线示例
    print("\n\n" + "="*60)
    print("📅 完整时间线示例")
    print("="*60)
    
    print("\n【示例 1：正常订单流程】")
    print("-" * 60)
    timeline1 = [
        ("Day 1 - 11:00", "添加订单，首次查询", "PROCESSING", "❌ 不通知"),
        ("Day 1 - 17:00", "定时检查", "PROCESSING", "❌ 不通知（未变）"),
        ("Day 2 - 09:00", "定时检查", "PROCESSING", "❌ 不通知（未变）"),
        ("Day 2 - 15:00", "定时检查", "SHIPPED", "✅ 通知！（已发货）"),
        ("Day 3 - 09:00", "定时检查", "SHIPPED", "❌ 不通知（未变）"),
        ("Day 4 - 10:00", "定时检查", "DELIVERED", "✅ 通知！（已送达）"),
        ("Day 5 onwards", "---", "DELIVERED", "⏭️ 跳过查询（终态）"),
    ]
    for time, action, status, result in timeline1:
        print(f"{time:20} | {action:15} | {status:12} | {result}")
    
    print("\n【示例 2：订单被取消】")
    print("-" * 60)
    timeline2 = [
        ("Day 1 - 11:00", "添加订单，首次查询", "PROCESSING", "❌ 不通知"),
        ("Day 1 - 17:00", "定时检查", "PROCESSING", "❌ 不通知（未变）"),
        ("Day 2 - 09:00", "定时检查", "CANCELED", "✅ 通知！（被取消）"),
        ("Day 3 onwards", "---", "CANCELED", "⏭️ 跳过查询（终态）"),
    ]
    for time, action, status, result in timeline2:
        print(f"{time:20} | {action:15} | {status:12} | {result}")
    
    print("\n【示例 3：首次查询就是取消】")
    print("-" * 60)
    timeline3 = [
        ("Day 1 - 11:00", "添加订单，首次查询", "CANCELED", "✅ 通知！（首次取消）"),
        ("Day 2 onwards", "---", "CANCELED", "⏭️ 跳过查询（终态）"),
    ]
    for time, action, status, result in timeline3:
        print(f"{time:20} | {action:15} | {status:12} | {result}")
    
    # 统计
    print("\n\n" + "="*60)
    print("📊 通知统计")
    print("="*60)
    print("\n✅ 会通知的情况：")
    print("   1. 首次查询就是 CANCELED")
    print("   2. 状态从任何状态变更为 CANCELED")
    print("   3. 状态从 PROCESSING 变更为 SHIPPED")
    print("   4. 状态从 SHIPPED 变更为 DELIVERED")
    print("   5. 任何有效状态的变更")
    
    print("\n❌ 不会通知的情况：")
    print("   1. 首次查询是 PROCESSING、SHIPPED、DELIVERED")
    print("   2. 状态未发生变化")
    print("   3. 查询失败或状态无效")
    print("   4. 已完成的订单（DELIVERED、CANCELED）不再查询")
    
    print("\n" + "="*60)
    print("🎯 核心规则：只有【有意义的状态变化】才会通知！")
    print("="*60)
    print()


if __name__ == '__main__':
    main()
