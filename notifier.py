#!/usr/bin/env python3
"""
通知模块 - 支持 Telegram
"""

import requests
import json
import os
from datetime import datetime


class TelegramNotifier:
    """Telegram 通知器"""
    
    def __init__(self, config_file='telegram_config.json'):
        self.config_file = config_file
        self.bot_token = ''
        self.chat_id = ''
        self.enabled = False
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.bot_token = config.get('bot_token', '')
                    self.chat_id = config.get('chat_id', '')
                    self.enabled = bool(self.bot_token and self.chat_id)
            except Exception as e:
                print(f"加载 Telegram 配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'bot_token': self.bot_token,
                'chat_id': self.chat_id
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def set_config(self, bot_token, chat_id):
        """设置配置"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        return self.save_config()
    
    def test_connection(self):
        """测试连接"""
        if not self.enabled:
            return False, "配置不完整"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data['result']
                return True, f"连接成功！Bot: @{bot_info.get('username')}"
            else:
                return False, f"连接失败: {data.get('description', '未知错误')}"
                
        except Exception as e:
            return False, f"请求失败: {str(e)}"
    
    def send_message(self, text, parse_mode='HTML'):
        """发送文本消息"""
        if not self.enabled:
            return False, "通知未启用"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                return True, "发送成功"
            else:
                return False, data.get('description', '发送失败')
                
        except Exception as e:
            return False, f"请求失败: {str(e)}"
    
    def send_order_notification(self, result, old_status=None):
        """发送订单状态变更通知"""
        status = result.get('status', 'Unknown')
        status_display = self._format_status(status)
        old_status_display = self._format_status(old_status) if old_status else '新订单'
        
        # 状态表情
        emoji_map = {
            'PLACED': '📝',
            'PROCESSING': '⏳',
            'PREPARED_FOR_SHIPMENT': '📦',
            'SHIPPED': '🚚',
            'DELIVERED': '✅',
            'CANCELED': '❌',
        }
        emoji = emoji_map.get(status, '📋')
        
        # 特别关注取消状态
        is_urgent = status == 'CANCELED'
        urgent_header = '🚨 <b>【订单已取消】</b>\n\n' if is_urgent else ''
        
        # 物流追踪信息
        tracking_number = result.get('trackingNumber', '')
        tracking_info = ''
        if status == 'SHIPPED' and tracking_number and tracking_number != '-':
            tracking_info = f'\n\n� <b>物流单号:</b> <code>{tracking_number}</code>'
        
        text = f"""{urgent_header}{emoji} <b>苹果订单状态变更</b>

<b>订单号:</b> <code>{result.get('orderNumber', 'N/A')}</code>
<b>产品:</b> {result.get('productName', 'N/A')}
<b>下单日期:</b> {result.get('orderDate', 'N/A')}

<b>状态变更:</b>
{old_status_display} → <b>{status_display}</b>

<b>预计送达:</b> {result.get('deliveryDate', 'N/A')}{tracking_info}

<b>检测时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<a href="{result.get('url')}">🔗 查看订单详情</a>"""

        return self.send_message(text)
    
    def _format_status(self, status):
        """格式化状态"""
        if not status:
            return 'Unknown'
        status_map = {
            'PLACED': '📝 Order Placed',
            'PROCESSING': '⏳ Processing',
            'PREPARED_FOR_SHIPMENT': '📦 Preparing to Ship',
            'SHIPPED': '🚚 Shipped',
            'DELIVERED': '✅ Delivered',
            'CANCELED': '❌ Canceled',
            'CANCELLED': '❌ Canceled',
        }
        return status_map.get(status, status)
    
    def get_config(self):
        """获取配置"""
        return {
            'bot_token': self.bot_token,
            'chat_id': self.chat_id,
            'enabled': self.enabled
        }


# 使用说明
HELP_TEXT = """
🤖 Telegram 通知设置说明

1️⃣ 创建 Telegram Bot:
   • 在 Telegram 中搜索 @BotFather
   • 发送 /newbot 创建新 Bot
   • 按提示设置名称和用户名
   • <b>保存好 Token</b> (格式: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)

2️⃣ 获取 Chat ID:
   • 在 Telegram 中搜索 @userinfobot
   • 点击 Start，即可看到你的 Chat ID
   • 或者使用你的 Bot，发送任意消息
   • 访问: https://api.telegram.org/bot<你的Token>/getUpdates
   • 在返回的 JSON 中找到 chat.id

3️⃣ 配置方法:
   • 在设置面板中填入 Token 和 Chat ID
   • 点击"测试连接"验证
   • 开启自动监控即可接收通知

💡 提示:
   • 取消订单会收到 ❌ 红色紧急提醒
   • 发货会收到 🚚 通知
   • 送达会收到 ✅ 通知
"""


# 单例
_notifier_instance = None

def get_notifier():
    """获取通知器单例"""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    return _notifier_instance


if __name__ == '__main__':
    # 测试
    notifier = get_notifier()
    
    # 配置 (替换为你的)
    notifier.set_config(
        bot_token='YOUR_BOT_TOKEN',
        chat_id='YOUR_CHAT_ID'
    )
    
    # 测试连接
    success, msg = notifier.test_connection()
    print(f"测试连接: {msg}")
    
    if success:
        # 测试发送
        notifier.send_message("<b>测试消息</b>\n\nHello from 苹果订单监控工具! 🍎")
