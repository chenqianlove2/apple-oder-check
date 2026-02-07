#!/usr/bin/env python3
"""
苹果订单监控完整启动器
- 启动后台监控
- 启动 Telegram Bot 监听
"""

import time
import sys
from monitor import get_monitor
from telegram_bot import TelegramOrderBot
from notifier import get_notifier


def main():
    print("=" * 60)
    print("🍎 苹果订单监控系统")
    print("=" * 60)
    
    # 检查 Telegram 配置
    notifier = get_notifier()
    config = notifier.get_config()
    
    print("\n📱 Telegram 配置:")
    print(f"  Token: {config.get('bot_token', '未设置')}")
    print(f"  Chat ID: {config.get('chat_id', '未设置')}")
    print(f"  状态: {'✅ 已启用' if config.get('enabled') else '❌ 未启用'}")
    
    if not config.get('enabled'):
        print("\n❌ Telegram 未配置")
        return 1
    
    # 加载订单并启动监控
    print("\n📋 加载订单...")
    monitor = get_monitor()
    
    from order_loader import load_orders_from_file
    urls = load_orders_from_file('orders.txt')
    
    if urls:
        monitor.start_monitoring(urls)
        print(f"✅ 监控已启动，共 {len(urls)} 个订单")
    else:
        print("⚠️ 暂无订单，请通过 Telegram 添加")
    
    # 启动 Telegram Bot
    print("\n🤖 启动 Telegram Bot...")
    bot = TelegramOrderBot(
        bot_token=notifier.bot_token,
        chat_id=notifier.chat_id
    )
    bot.start_polling()
    print("✅ Bot 已启动\n")
    
    # 发送启动通知
    notifier.send_message(
        f"""🍎 <b>订单监控系统已启动</b>

📦 当前监控订单: {len(urls)} 个
⏱ 检查间隔: {monitor.config['monitor_interval']//60} 分钟
🤖 Telegram Bot: 在线

<b>使用方法:</b>
• 直接发送订单链接即可添加
• 发送 /list 查看当前订单
• 发送 /help 查看帮助

<i>按 Ctrl+C 停止</i>"""
    )
    
    print("=" * 60)
    print("系统运行中...")
    print("• 监控订单状态变化")
    print("• 监听 Telegram 新消息")
    print("• 按 Ctrl+C 停止")
    print("=" * 60 + "\n")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n正在停止系统...")
        
        monitor.stop_monitoring()
        bot.stop()
        
        notifier.send_message(
            "🛑 <b>订单监控系统已停止</b>\n\n"
            "如需再次启动，请运行:\n"
            "<code>python start_all.py</code>"
        )
        
        print("✅ 系统已停止")
        return 0


if __name__ == '__main__':
    sys.exit(main())
