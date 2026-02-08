#!/usr/bin/env python3
"""
苹果订单监控模块 - 自动检测状态变化并发送邮件提醒
"""

import re
import requests
import json
import time
import os
from datetime import datetime
from threading import Thread, Event
from notifier import get_notifier
from order_loader import load_orders_from_file


class OrderMonitor:
    """订单监控器"""
    
    def __init__(self, config_file='monitor_config.json'):
        self.config_file = config_file
        self.data_file = 'order_history.json'
        self.running = False
        self.stop_event = Event()
        self.thread = None
        self.callback = None  # 状态变化回调函数
        
        # 默认配置
        self.config = {
            'monitor_interval': 300,  # 默认5分钟检测一次
            'notify_on_cancel': True,  # 取消时通知
            'notify_on_ship': True,    # 发货时通知
            'notify_on_deliver': True, # 送达时通知
            'notify_all_changes': True, # 任何状态变更都通知
        }
        
        # 订单历史状态 {url: {'status': 'xxx', 'last_check': 'xxx', 'history': []}}
        self.order_history = {}
        
        self.load_config()
        self.load_history()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # 兼容 web_monitor 使用的 interval 键名
                    if 'interval' in saved and 'monitor_interval' not in saved:
                        saved['monitor_interval'] = saved['interval']
                    self.config.update(saved)
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_history(self):
        """加载订单历史（兼容 web_monitor 的数据格式）"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容 web_monitor 的格式 {results: ..., changes: ...}
                    if 'results' in data:
                        self.order_history = data['results']
                    else:
                        self.order_history = data
            except Exception as e:
                print(f"加载历史失败: {e}")

    def save_history(self):
        """保存订单历史（使用与 web_monitor 兼容的格式）"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'results': self.order_history,
                    'changes': [],
                    'last_save': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存历史失败: {e}")
            return False
    
    def update_config(self, **kwargs):
        """更新配置"""
        self.config.update(kwargs)
        return self.save_config()
    
    def query_order(self, url, timeout=30):
        """查询单个订单"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            html = response.text
            
            result = {
                'success': True,
                'url': url,
                'orderNumber': '-',
                'orderDate': '-',
                'productName': '-',
                'status': '-',
                'deliveryDate': '-',
                'timestamp': datetime.now().isoformat()
            }
            
            # 提取订单号
            order_match = re.search(r'"orderNumber"\s*:\s*"([^"]+)"', html)
            if order_match:
                result['orderNumber'] = order_match.group(1)
            
            # 提取下单日期
            order_date_match = re.search(r'"orderPlacedDate"\s*:\s*"([^"]+)"', html)
            if order_date_match:
                result['orderDate'] = order_date_match.group(1)
            
            # 提取产品名称
            product_match = re.search(r'"productName"\s*:\s*"([^"]+)"', html)
            if product_match:
                result['productName'] = product_match.group(1)
            
            # 提取状态 (使用 currentStatus)
            status_match = re.search(r'"currentStatus"\s*:\s*"([^"]+)"', html)
            if status_match:
                result['status'] = status_match.group(1)
            else:
                status_match = re.search(r'"statusDescription"\s*:\s*"([^"]+)"', html)
                if status_match:
                    result['status'] = status_match.group(1)
            
            # 提取配送日期
            delivery_match = re.search(r'"deliveryDate"\s*:\s*"([^"]+)"', html)
            if delivery_match:
                result['deliveryDate'] = delivery_match.group(1)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_status_change(self, url, new_status):
        """检查状态是否变化"""
        if url not in self.order_history:
            return True, None  # 新订单
        
        old_status = self.order_history[url].get('status')
        if old_status != new_status:
            return True, old_status
        return False, old_status
    
    def should_notify(self, status, changed=True):
        """判断是否需要发送通知"""
        # 如果设置为任何变更都通知，且状态确实变更了
        if self.config.get('notify_all_changes', False) and changed:
            return True
        
        # 特定状态通知
        if status == 'CANCELED' and self.config['notify_on_cancel']:
            return True
        if status == 'SHIPPED' and self.config['notify_on_ship']:
            return True
        if status == 'DELIVERED' and self.config['notify_on_deliver']:
            return True
        return False
    
    def format_status_display(self, status):
        """格式化状态显示"""
        status_map = {
            'PLACED': 'Order Placed',
            'PROCESSING': 'Processing',
            'PREPARED_FOR_SHIPMENT': 'Preparing to Ship',
            'SHIPPED': 'Shipped',
            'DELIVERED': 'Delivered',
            'CANCELED': 'Canceled',
            'CANCELLED': 'Canceled',
        }
        return status_map.get(status, status)
    
    def monitor_once(self, urls):
        """执行一次监控检查"""
        results = []
        
        for url in urls:
            if self.stop_event.is_set():
                break
            
            # 查询订单
            result = self.query_order(url)
            results.append(result)
            
            if not result.get('success'):
                continue
            
            new_status = result.get('status')
            changed, old_status = self.check_status_change(url, new_status)
            
            # 判断是否首次查询
            is_first_check = url not in self.order_history
            
            # 更新历史
            self.order_history[url] = {
                'status': new_status,
                'last_check': datetime.now().isoformat(),
                'orderNumber': result.get('orderNumber'),
                'productName': result.get('productName'),
            }
            self.save_history()
            
            # 状态变更或首次查询到取消状态时发送通知
            should_send = False
            
            if changed and not is_first_check:
                # 状态变更（非首次）
                should_send = self.should_notify(new_status, changed=True)
            elif is_first_check and new_status in ['CANCELED', 'CANCELLED']:
                # 首次查询就是取消状态 - 立即通知！
                should_send = True
                print(f"⚠️  首次查询发现订单已取消: {result.get('orderNumber')}")
            
            if should_send:
                # 触发回调
                if self.callback:
                    self.callback(result, old_status)
                
                # 发送通知
                self.send_status_notification(result, old_status if not is_first_check else '首次查询')
            
            time.sleep(1)  # 避免请求过快
        
        return results
    
    def send_status_notification(self, result, old_status):
        """发送状态变更 Telegram 通知"""
        notifier = get_notifier()
        notifier.send_order_notification(result, old_status)
    
    def test_notification(self):
        """测试 Telegram 通知"""
        notifier = get_notifier()
        return notifier.test_connection()
    
    def start_monitoring(self, urls):
        """启动后台监控"""
        if self.running:
            return False
        
        self.running = True
        self.stop_event.clear()
        
        def monitor_loop():
            while not self.stop_event.is_set():
                try:
                    self.monitor_once(urls)
                except Exception as e:
                    print(f"监控出错: {e}")
                
                # 等待下次检查
                for _ in range(self.config['monitor_interval']):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
        
        self.thread = Thread(target=monitor_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.running:
            return
        
        self.stop_event.set()
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def get_monitoring_status(self):
        """获取监控状态"""
        return {
            'running': self.running,
            'interval': self.config['monitor_interval'],
            'monitored_orders': len(self.order_history),
            'config': get_notifier().get_config()
        }
    
    def start_monitoring_from_file(self, filepath='orders.txt'):
        """从文件加载订单并启动监控"""
        urls = load_orders_from_file(filepath)
        if urls:
            self.start_monitoring(urls)
            return True, f"已加载 {len(urls)} 个订单，监控已启动"
        else:
            return False, "没有加载到任何订单链接"


# 单例实例
_monitor_instance = None

def get_monitor():
    """获取监控器单例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = OrderMonitor()
    return _monitor_instance


if __name__ == '__main__':
    # 测试
    monitor = get_monitor()
    
    # 配置邮件 (请替换为你的配置)
    monitor.update_config(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        smtp_ssl=True,
        sender_email='your_email@gmail.com',
        sender_password='your_app_password',
        receiver_email='receiver@example.com',
        monitor_interval=60,  # 1分钟检测一次
    )
    
    # 测试邮件
    monitor.test_email()
