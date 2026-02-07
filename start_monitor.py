#!/usr/bin/env python3
"""
苹果订单监控启动器
从 orders.txt 文件读取订单链接并启动监控
"""

import sys
import time
from monitor import get_monitor
from notifier import get_notifier


def main():
    print("=" * 60)
    print("🍎 苹果订单监控工具")
    print("=" * 60)
    
    # 检查 Telegram 配置
    notifier = get_notifier()
    config = notifier.get_config()
    
    print("\n📱 Telegram 配置:")
    print(f"  Bot Token: {config.get('bot_token', '未设置')}")
    print(f"  Chat ID: {config.get('chat_id', '未设置')}")
    print(f"  状态: {'✅ 已启用' if config.get('enabled') else '❌ 未启用'}")
    
    if not config.get('enabled'):
        print("\n❌ Telegram 未配置，无法发送通知")
        print("请先配置 Bot Token 和 Chat ID")
        return
    
    # 加载订单
    print("\n📋 加载订单链接...")
    
    monitor = get_monitor()
    success, msg = monitor.start_monitoring_from_file('orders.txt')
    
    if not success:
        print(f"\n❌ {msg}")
        print("\n请创建 orders.txt 文件，格式如下:")
        print("  https://www.apple.com/xc/us/vieworder/订单号/邮箱")
        print("  https://www.apple.com/xc/us/vieworder/订单号2/邮箱2")
        return
    
    print(f"✅ {msg}")
    
    # 显示配置
    print("\n⚙️ 监控配置:")
    print(f"  检查间隔: {monitor.config['monitor_interval']} 秒 ({monitor.config['monitor_interval']//60}分钟)")
    print(f"  通知规则:")
    print(f"    - 任何状态变更: {'✅' if monitor.config.get('notify_all_changes') else '❌'}")
    print(f"    - 订单取消: {'✅' if monitor.config.get('notify_on_cancel') else '❌'}")
    print(f"    - 发货通知: {'✅' if monitor.config.get('notify_on_ship') else '❌'}")
    print(f"    - 送达通知: {'✅' if monitor.config.get('notify_on_deliver') else '❌'}")
    
    # 发送启动通知
    notifier.send_message("""🍎 <b>苹果订单监控已启动</b>

✅ 监控运行中
📦 正在监控订单状态变化
🔔 状态变更时将发送通知

<i>按 Ctrl+C 停止监控</i>""")
    
    print("\n" + "=" * 60)
    print("监控运行中... 按 Ctrl+C 停止")
    print("=" * 60 + "\n")
    
    # 保持运行
    try:
        while monitor.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n正在停止监控...")
        monitor.stop_monitoring()
        
        notifier.send_message("""🛑 <b>苹果订单监控已停止</b>

监控程序已手动停止
如需再次启动，请运行 start_monitor.py""")
        
        print("✅ 监控已停止")


if __name__ == '__main__':
    main()
