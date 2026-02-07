#!/usr/bin/env python3
"""
Telegram Bot 消息监听 - 自动接收订单链接并更新文件
"""

import requests
import re
import time
import threading
from datetime import datetime
from order_loader import add_order_to_file, load_orders_from_file


class TelegramOrderBot:
    """Telegram 订单 Bot - 自动接收链接"""
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = str(chat_id)  # 只允许特定用户
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.offset = 0  # 消息偏移量，用于获取新消息
        self.running = False
        self.thread = None
        self.last_check = None
    
    def get_updates(self):
        """获取新消息"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.offset,
                'limit': 10,
            }
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data.get('ok'):
                return data.get('result', [])
            else:
                print(f"获取消息失败: {data.get('description')}")
                return []
                
        except Exception as e:
            print(f"请求失败: {e}")
            return []
    
    def send_message(self, text, reply_to_message_id=None):
        """发送消息"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            }
            if reply_to_message_id:
                payload['reply_to_message_id'] = reply_to_message_id
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            return data.get('ok', False)
            
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def extract_order_urls(self, text):
        """从文本中提取订单链接"""
        if not text:
            return []
        
        # 匹配苹果订单链接
        pattern = r'https?://[^\s]+apple\.com[^\s]*vieworder[^\s]*'
        urls = re.findall(pattern, text, re.IGNORECASE)
        
        # 清理 URL（去掉标点符号）
        cleaned_urls = []
        for url in urls:
            # 去除末尾的标点
            url = url.rstrip('.,;:!?)\'\"')
            if url.startswith('http'):
                cleaned_urls.append(url)
        
        return cleaned_urls
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = str(chat_id)  # 只允许特定用户
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.offset = 0  # 消息偏移量，用于获取新消息
        self.running = False
        self.thread = None
        self.last_check = None
        self.clear_pending = False  # 等待确认清空
        self.pending_urls = []  # 等待添加的链接（清空后）
    
    def process_message(self, message):
        """处理单条消息"""
        message_id = message.get('message_id')
        chat_id = str(message.get('chat', {}).get('id'))
        text = message.get('text', '')
        
        # 只处理指定用户的消息
        if chat_id != self.chat_id:
            return
        
        print(f"\n收到消息: {text[:100]}...")
        
        # 检查是否是确认清空
        if self.clear_pending:
            if text.lower() in ['/yes', 'yes', '是', '确认', 'confirm']:
                self.do_clear_and_add(message_id)
                return
            elif text.lower() in ['/no', 'no', '否', '取消', 'cancel']:
                self.clear_pending = False
                self.pending_urls = []
                self.send_message("✅ 已取消清空操作", message_id)
                return
        
        # 提取订单链接
        urls = self.extract_order_urls(text)
        
        if not urls:
            # 不是订单链接，可能是命令或普通消息
            if text.startswith('/'):
                self.handle_command(text, message_id)
            return
        
        # 加载现有订单
        existing_urls = load_orders_from_file('orders.txt')
        
        # 如果有现有订单，询问是否清空
        if existing_urls and len(existing_urls) > 0:
            self.pending_urls = urls
            self.clear_pending = True
            
            reply = f"""⚠️ <b>发现 {len(existing_urls)} 个现有订单</b>

你发送了 {len(urls)} 个新订单链接。

请选择：
• 发送 <b>/yes</b> - 清空现有订单，只保留新订单
• 发送 <b>/no</b> - 保留现有订单，追加新订单
• 发送 <b>/cancel</b> - 取消操作

<i>现有订单将{len(existing_urls)}个会被保留或删除</i>"""
            
            self.send_message(reply, message_id)
            return
        
        # 没有现有订单，直接添加
        self.add_urls(urls, message_id)
    
    def do_clear_and_add(self, message_id):
        """执行清空并添加新订单"""
        # 清空文件
        with open('orders.txt', 'w', encoding='utf-8') as f:
            f.write("# 苹果订单链接列表\n# 每行一个链接\n\n")
        
        # 添加新订单
        self.add_urls(self.pending_urls, message_id, prefix="✅ <b>已清空原有订单</b>\n\n")
        
        # 重置状态
        self.clear_pending = False
        self.pending_urls = []
    
    def add_urls(self, urls, message_id, prefix=""):
        """添加 URL 到文件"""
        added = []
        existed = []
        invalid = []
        
        existing_urls = load_orders_from_file('orders.txt')
        existing_set = set(existing_urls)
        
        for url in urls:
            if 'vieworder' not in url:
                invalid.append(url)
                continue
            
            if url in existing_set:
                existed.append(url)
                continue
            
            if add_order_to_file(url, 'orders.txt'):
                added.append(url)
                existing_set.add(url)
        
        reply = prefix + self.format_reply(added, existed, invalid)
        self.send_message(reply, message_id)
    
    def format_reply(self, added, existed, invalid):
        """格式化回复消息"""
        lines = []
        
        if added:
            lines.append(f"✅ <b>成功添加 {len(added)} 个订单</b>")
            for url in added:
                order_no = self.extract_order_no(url)
                lines.append(f"  • {order_no}")
            lines.append("")
        
        if existed:
            lines.append(f"⚠️ <b>已存在 {len(existed)} 个订单</b>（已跳过）")
            for url in existed:
                order_no = self.extract_order_no(url)
                lines.append(f"  • {order_no}")
            lines.append("")
        
        if invalid:
            lines.append(f"❌ <b>无效链接 {len(invalid)} 个</b>")
            lines.append("")
        
        # 显示当前总数
        total = len(load_orders_from_file('orders.txt'))
        lines.append(f"📦 <b>当前监控订单总数: {total}</b>")
        lines.append(f"<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>")
        
        return '\n'.join(lines)
    
    def extract_order_no(self, url):
        """提取订单号"""
        match = re.search(r'/vieworder/([A-Z0-9]+)', url)
        if match:
            return match.group(1)
        return url[:30] + '...'
    
    def handle_command(self, text, message_id):
        """处理命令"""
        cmd = text.lower().split()[0]
        
        if cmd == '/list' or cmd == '/orders':
            # 列出所有订单
            urls = load_orders_from_file('orders.txt')
            if not urls:
                self.send_message("📭 <b>暂无监控订单</b>\n\n发送订单链接即可添加", message_id)
                return
            
            lines = [f"📋 <b>当前共 {len(urls)} 个监控订单</b>\n"]
            for i, url in enumerate(urls[:20], 1):  # 最多显示20个
                order_no = self.extract_order_no(url)
                lines.append(f"{i}. {order_no}")
            
            if len(urls) > 20:
                lines.append(f"\n... 还有 {len(urls)-20} 个订单")
            
            self.send_message('\n'.join(lines), message_id)
        
        elif cmd == '/clear':
            # 清空订单（需要确认）
            self.send_message(
                "⚠️ <b>确认清空所有订单?</b>\n\n"
                "这将会删除 orders.txt 中的所有链接。\n"
                "如需清空，请发送 <code>/confirm_clear</code>",
                message_id
            )
        
        elif cmd == '/confirm_clear':
            # 确认清空
            with open('orders.txt', 'w', encoding='utf-8') as f:
                f.write("# 苹果订单链接列表\n# 每行一个链接\n\n")
            self.send_message("✅ <b>已清空所有订单</b>", message_id)
        
        elif cmd == '/help':
            help_text = """<b>🤖 命令列表</b>

/list 或 /orders - 查看当前监控订单
/clear - 清空所有订单
/help - 显示帮助

<b>使用方法:</b>
直接发送订单链接即可自动添加
支持一次发送多个链接"""
            self.send_message(help_text, message_id)
        
        elif cmd == '/start':
            welcome = """🍎 <b>苹果订单监控 Bot</b>

你好！我是你的订单监控助手。

<b>使用方法:</b>
直接发送订单链接，我会自动添加到你的监控列表。

例如:
<code>https://www.apple.com/xc/us/vieworder/W1234567890/your@email.com</code>

<b>命令:</b>
/list - 查看当前订单
/clear - 清空所有订单
/help - 显示帮助

<b>提示:</b>
• 支持一次发送多个链接
• 重复链接会自动跳过
• 发送新链接时可选择清空旧订单
• 状态变更时会自动通知你"""
            self.send_message(welcome, message_id)
        
        elif cmd in ['/yes', '/no', '/cancel']:
            # 这些命令在 process_message 中处理
            pass
    
    def check_messages(self):
        """检查一次消息"""
        updates = self.get_updates()
        
        for update in updates:
            # 更新偏移量
            self.offset = update['update_id'] + 1
            
            # 处理消息
            if 'message' in update:
                self.process_message(update['message'])
    
    def run_once(self):
        """运行一次检查"""
        try:
            self.check_messages()
        except Exception as e:
            print(f"处理消息出错: {e}")
    
    def start_polling(self):
        """启动轮询"""
        if self.running:
            return False
        
        self.running = True
        print(f"\n🤖 Telegram Bot 启动")
        print(f"   Bot Token: {self.bot_token[:15]}...")
        print(f"   Chat ID: {self.chat_id}")
        print(f"   正在监听消息...\n")
        
        # 发送启动消息
        self.send_message(
            "🍎 <b>订单监控 Bot 已启动</b>\n\n"
            "直接发送订单链接即可添加监控。\n"
            "发送 /help 查看帮助"
        )
        
        def polling_loop():
            while self.running:
                self.run_once()
                time.sleep(2)  # 每2秒检查一次
        
        self.thread = threading.Thread(target=polling_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """停止轮询"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Bot 已停止")


# 便捷函数
def start_telegram_bot():
    """启动 Telegram Bot"""
    from notifier import get_notifier
    
    notifier = get_notifier()
    config = notifier.get_config()
    
    if not config.get('enabled'):
        print("❌ Telegram 未配置，无法启动 Bot")
        return None
    
    bot = TelegramOrderBot(
        bot_token=notifier.bot_token,
        chat_id=notifier.chat_id
    )
    bot.start_polling()
    return bot


if __name__ == '__main__':
    bot = start_telegram_bot()
    
    if bot:
        print("按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            bot.stop()
