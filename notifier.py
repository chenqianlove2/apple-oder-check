#!/usr/bin/env python3
"""
通知模块 - 支持多个 Telegram 机器人
"""

import requests
import json
import os
from datetime import datetime
import uuid


class TelegramNotifier:
    """Telegram 通知器 - 支持多机器人"""
    
    def __init__(self, config_file='telegram_config.json'):
        self.config_file = config_file
        self.bots = []  # 机器人列表
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 兼容旧配置
                    if 'bot_token' in config and 'chat_id' in config:
                        # 迁移旧配置
                        self.bots = [{
                            'id': str(uuid.uuid4()),
                            'name': 'Default Bot',
                            'bot_token': config['bot_token'],
                            'chat_id': config['chat_id'],
                            'enabled': True
                        }]
                        self.save_config()
                    else:
                        self.bots = config.get('bots', [])
            except Exception as e:
                print(f"加载 Telegram 配置失败: {e}")
                self.bots = []
    
    def save_config(self):
        """保存配置"""
        try:
            config = {'bots': self.bots}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def set_config(self, bot_token, chat_id):
        """设置配置（兼容旧接口）"""
        # 如果已有机器人，更新第一个，否则添加新的
        if self.bots:
            self.bots[0]['bot_token'] = bot_token
            self.bots[0]['chat_id'] = chat_id
        else:
            self.bots.append({
                'id': str(uuid.uuid4()),
                'name': 'Default Bot',
                'bot_token': bot_token,
                'chat_id': chat_id,
                'enabled': True
            })
        return self.save_config()
    
    def add_bot(self, name, bot_token, chat_id):
        """添加新机器人"""
        bot = {
            'id': str(uuid.uuid4()),
            'name': name,
            'bot_token': bot_token,
            'chat_id': chat_id,
            'enabled': True
        }
        self.bots.append(bot)
        return self.save_config()
    
    def update_bot(self, bot_id, name=None, bot_token=None, chat_id=None, enabled=None):
        """更新机器人配置"""
        for bot in self.bots:
            if bot['id'] == bot_id:
                if name is not None:
                    bot['name'] = name
                if bot_token is not None:
                    bot['bot_token'] = bot_token
                if chat_id is not None:
                    bot['chat_id'] = chat_id
                if enabled is not None:
                    bot['enabled'] = enabled
                return self.save_config()
        return False
    
    def delete_bot(self, bot_id):
        """删除机器人"""
        self.bots = [b for b in self.bots if b['id'] != bot_id]
        return self.save_config()
    
    def get_bots(self):
        """获取所有机器人列表"""
        return self.bots
    
    def get_enabled_bots(self):
        """获取启用的机器人列表"""
        return [b for b in self.bots if b.get('enabled', True)]
    
    def test_connection(self, bot_token=None, chat_id=None):
        """测试连接"""
        # 如果提供了参数，测试指定的机器人
        if bot_token and chat_id:
            return self._test_bot(bot_token, chat_id)
        
        # 否则测试第一个启用的机器人（兼容旧接口）
        enabled_bots = self.get_enabled_bots()
        if not enabled_bots:
            return False, "没有启用的机器人"
        
        bot = enabled_bots[0]
        return self._test_bot(bot['bot_token'], bot['chat_id'])
    
    def _test_bot(self, bot_token, chat_id):
        """测试单个机器人"""
        if not bot_token or not chat_id:
            return False, "配置不完整"
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data['result']
                return True, f"连接成功！Bot: @{bot_info.get('username')}"
            else:
                return False, f"连接失败: {data.get('description', '未知错误')}"
                
        except Exception as e:
            return False, f"请求失败: {str(e)}"
    
    def send_message(self, text, parse_mode='HTML', bot_token=None, chat_id=None):
        """发送文本消息"""
        # 如果指定了机器人，只发送给该机器人
        if bot_token and chat_id:
            return self._send_to_bot(bot_token, chat_id, text, parse_mode)
        
        # 否则发送给所有启用的机器人
        enabled_bots = self.get_enabled_bots()
        if not enabled_bots:
            return False, "没有启用的机器人"
        
        results = []
        for bot in enabled_bots:
            success, msg = self._send_to_bot(bot['bot_token'], bot['chat_id'], text, parse_mode)
            results.append({
                'bot_name': bot['name'],
                'success': success,
                'message': msg
            })
        
        # 如果至少有一个成功，返回成功
        success_count = sum(1 for r in results if r['success'])
        if success_count > 0:
            return True, f"成功发送到 {success_count}/{len(results)} 个机器人"
        else:
            return False, "所有机器人发送失败"
    
    def _send_to_bot(self, bot_token, chat_id, text, parse_mode='HTML'):
        """发送消息到单个机器人"""
        if not bot_token or not chat_id:
            return False, "配置不完整"
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
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
        
        # 处理旧状态显示
        is_first_check = old_status is None or old_status == '-' or old_status == '' or old_status == '首次查询'
        
        if is_first_check:
            if status == 'CANCELED':
                # 首次查询就是取消状态 - 特殊提示
                old_status_display = '⚠️ 首次查询发现'
            else:
                old_status_display = '新订单'
        else:
            old_status_display = self._format_status(old_status)
        
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
        if is_urgent and is_first_check:
            urgent_header = '🚨🚨 <b>【重要警告：订单已取消】</b> 🚨🚨\n\n'
        elif is_urgent:
            urgent_header = '🚨 <b>【订单已取消】</b>\n\n'
        else:
            urgent_header = ''
        
        # 物流追踪信息
        tracking_number = result.get('trackingNumber', '')
        tracking_info = ''
        if status == 'SHIPPED' and tracking_number and tracking_number != '-':
            tracking_info = f'\n\n📮 <b>物流单号:</b> <code>{tracking_number}</code>'
        
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
            'bots': self.bots
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
