#!/usr/bin/env python3
"""
苹果订单 Web 监控管理
"""

import re
import requests
import json
import time
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from concurrent.futures import ThreadPoolExecutor
from notifier import get_notifier



class OrderMonitor:
    """订单监控器 - Web 版"""
    
    def __init__(self):
        self.orders_file = 'orders.txt'
        self.config_file = 'monitor_config.json'
        self.history_file = 'order_history.json'
        
        self.running = False
        self.stop_event = threading.Event()
        self.monitor_thread = None
        self.last_check_time = None
        self.check_count = 0
        
        # 默认配置
        self.config = {
            'interval': 300,  # 默认5分钟
            'threads': 10,
            'timeout': 30,
            'auto_start': False,
        }
        
        # 监控结果
        self.results = {}  # {url: last_result}
        self.status_changes = []  # 状态变更记录
        
        self.load_config()
        self.load_history()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                    # 兼容 monitor.py 使用的 monitor_interval 键名
                    if 'monitor_interval' in saved and 'interval' not in saved:
                        saved['interval'] = saved['monitor_interval']
                    self.config.update(saved)
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.results = data.get('results', {})
                    self.status_changes = data.get('changes', [])
            except Exception as e:
                print(f"加载历史失败: {e}")
    
    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump({
                    'results': self.results,
                    'changes': self.status_changes[-100:],  # 只保留最近100条
                    'last_save': datetime.now().isoformat()
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"保存历史失败: {e}")
            return False
    
    def get_orders(self):
        """获取所有订单链接"""
        orders = []
        if os.path.exists(self.orders_file):
            try:
                with open(self.orders_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line.startswith('http'):
                            orders.append(line)
            except Exception as e:
                print(f"读取订单失败: {e}")
        return orders
    
    def add_order(self, url):
        """添加订单"""
        if not url or not url.startswith('http'):
            return False, "无效的链接"
        
        orders = self.get_orders()
        if url in orders:
            return False, "订单已存在"
        
        try:
            with open(self.orders_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")
            
            # 从结果中删除该订单的历史记录（如果有）
            # 这样下次监控时会强制重新查询
            if url in self.results:
                print(f"⚠️ 删除订单 {url} 的历史记录，将在下次监控时重新查询")
                del self.results[url]
                self.save_history()
            
            return True, "添加成功"
        except Exception as e:
            return False, str(e)
    
    def delete_order(self, url):
        """删除订单"""
        orders = self.get_orders()
        if url not in orders:
            return False, "订单不存在"
        
        try:
            # 重写文件
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                f.write("# 苹果订单链接列表\n# 每行一个链接\n\n")
                for order in orders:
                    if order != url:
                        f.write(f"{order}\n")
            
            # 从结果中删除
            if url in self.results:
                del self.results[url]
            
            return True, "删除成功"
        except Exception as e:
            return False, str(e)
    
    def query_order(self, url):
        """查询单个订单"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=self.config['timeout'], allow_redirects=True)
            html = response.text
            
            # 获取之前的查询次数
            previous_query_count = 0
            if url in self.results:
                previous_query_count = self.results[url].get('queryCount', 0)
            
            result = {
                'success': True,
                'url': url,
                'orderNumber': '-',
                'orderDate': '-',
                'productName': '-',
                'status': '-',
                'deliveryDate': '-',
                'trackingUrl': '-',
                'trackingNumber': '-',
                'timestamp': datetime.now().isoformat(),
                'queryCount': previous_query_count + 1  # 查询次数加1
            }
            
            # 提取订单号
            m = re.search(r'"orderNumber"\s*:\s*"([^"]+)"', html)
            if m:
                result['orderNumber'] = m.group(1)
            
            # 提取下单日期
            m = re.search(r'"orderPlacedDate"\s*:\s*"([^"]+)"', html)
            if m:
                result['orderDate'] = m.group(1)
            
            # 提取产品名称
            m = re.search(r'"productName"\s*:\s*"([^"]+)"', html)
            if m:
                result['productName'] = m.group(1)
            
            # 提取状态
            m = re.search(r'"currentStatus"\s*:\s*"([^"]+)"', html)
            if m:
                result['status'] = m.group(1)
            else:
                m = re.search(r'"statusDescription"\s*:\s*"([^"]+)"', html)
                if m:
                    result['status'] = m.group(1)
            
            # 提取配送日期
            m = re.search(r'"deliveryDate"\s*:\s*"([^"]+)"', html)
            if m:
                result['deliveryDate'] = m.group(1)
            
            # 提取物流追踪链接和单号 (UPS tracking)
            m = re.search(r'"trackingUrl"\s*:\s*"([^"]+)"', html)
            if m:
                result['trackingUrl'] = m.group(1)
                # 从 URL 中提取追踪单号 (支持多种 URL 格式)
                # 格式1: InquiryNumber1=单号 或 InquiryNumber=单号
                tracking_match = re.search(r'[?&]InquiryNumber\d*=([A-Z0-9]+)', m.group(1))
                if not tracking_match:
                    # 格式2: trackingNumber=单号
                    tracking_match = re.search(r'[?&]trackingNumber=([A-Z0-9]+)', m.group(1))
                if tracking_match:
                    result['trackingNumber'] = tracking_match.group(1)
            else:
                # 尝试其他可能的字段名
                m = re.search(r'(https?://[^"\s]+ups\.com[^"\s]+)', html)
                if m:
                    result['trackingUrl'] = m.group(1)
                    # 从 URL 中提取追踪单号
                    tracking_match = re.search(r'[?&]InquiryNumber\d*=([A-Z0-9]+)', m.group(1))
                    if not tracking_match:
                        tracking_match = re.search(r'[?&]trackingNumber=([A-Z0-9]+)', m.group(1))
                    if tracking_match:
                        result['trackingNumber'] = tracking_match.group(1)
            
            # 如果没有从 URL 提取到，尝试直接提取追踪单号
            if result['trackingNumber'] == '-':
                m = re.search(r'"trackingNumber"\s*:\s*"([^"]+)"', html)
                if m:
                    result['trackingNumber'] = m.group(1)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_all_orders(self):
        """检查所有订单 - 智能检查，只查询信息不完整的订单"""
        orders = self.get_orders()
        if not orders:
            return []
        
        results = []
        
        # 第一步：识别需要查询的订单
        orders_to_check = []
        for url in orders:
            # 如果从未查询过，需要查询
            if url not in self.results:
                orders_to_check.append(url)
                continue
            
            # 如果之前查询失败，需要重新查询
            prev_result = self.results[url]
            if not prev_result.get('success'):
                orders_to_check.append(url)
                continue
            
            # 如果订单已取消或已送达，跳过查询（终态）
            status = prev_result.get('status', '')
            if status in ['CANCELED', 'DELIVERED']:
                continue
            
            # 其他所有状态都需要持续查询（追踪状态变化）
            # 包括: SHIPPED, PROCESSING, PREPARED_FOR_SHIPMENT, PLACED 等
            orders_to_check.append(url)
        
        print(f"📊 总订单数: {len(orders)}, 需要查询: {len(orders_to_check)}, 已完成: {len(orders) - len(orders_to_check)}")
        
        # 如果没有需要查询的订单，直接返回
        if not orders_to_check:
            print("✅ 所有订单信息已完整，无需查询")
            self.last_check_time = datetime.now().isoformat()
            self.check_count += 1
            self.save_history()
            return []
        
        def check_one(url):
            result = self.query_order(url)
            
            # 检查状态变化
            if url in self.results:
                old_status = self.results[url].get('status')
                new_status = result.get('status')
                
                # 只有在查询成功且新旧状态都是有效状态时，才判断状态变化
                # 过滤掉 '-', None, '' 等无效状态
                valid_statuses = ['PLACED', 'PROCESSING', 'PREPARED_FOR_SHIPMENT', 'SHIPPED', 'DELIVERED', 'CANCELED']
                old_valid = old_status in valid_statuses
                new_valid = new_status in valid_statuses
                
                # 只要状态发生变化就发送通知（但两个状态都必须是有效的）
                if (old_status != new_status and 
                    result.get('success') and 
                    old_valid and 
                    new_valid):
                    # 记录状态变化
                    change = {
                        'url': url,
                        'orderNumber': result.get('orderNumber'),
                        'productName': result.get('productName'),
                        'oldStatus': old_status,
                        'newStatus': new_status,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.status_changes.append(change)

                    # 发送 Telegram 通知
                    try:
                        notifier = get_notifier()
                        if notifier.enabled:
                            status_emoji = {
                                'CANCELED': '🚨',
                                'SHIPPED': '📦',
                                'DELIVERED': '✅',
                                'PROCESSING': '⚙️',
                                'PREPARED_FOR_SHIPMENT': '📋',
                                'PLACED': '📝'
                            }
                            emoji = status_emoji.get(new_status, '📢')
                            print(f"{emoji} 订单 {result.get('orderNumber')} 状态变更: {old_status} → {new_status}，发送通知")
                            notifier.send_order_notification(result, old_status)
                    except Exception as e:
                        print(f"发送通知失败: {e}")
            else:
                # 第一次查询该订单
                # 只有首次查询就是 CANCELED 状态时才发送通知
                if result.get('success') and result.get('status') == 'CANCELED':
                    print(f"🚨 首次查询订单 {result.get('orderNumber')}，状态: CANCELED，发送通知")
                    try:
                        notifier = get_notifier()
                        if notifier.enabled:
                            notifier.send_order_notification(result, None)
                    except Exception as e:
                        print(f"发送通知失败: {e}")
                else:
                    # 其他状态的首次查询不发送通知
                    print(f"📥 首次查询订单 {result.get('orderNumber')}，状态: {result.get('status')}（不发送通知）")
            
            self.results[url] = result
            return result
        
        # 使用线程池查询需要检查的订单
        print(f"🔍 开始查询 {len(orders_to_check)} 个订单...")
        with ThreadPoolExecutor(max_workers=self.config['threads']) as executor:
            results = list(executor.map(check_one, orders_to_check))
        
        self.last_check_time = datetime.now().isoformat()
        self.check_count += 1
        self.save_history()
        
        return results
    
    def start(self):
        """启动监控"""
        if self.running:
            return False
        
        self.running = True
        self.stop_event.clear()
        
        def monitor_loop():
            while not self.stop_event.is_set():
                try:
                    self.check_all_orders()
                except Exception as e:
                    print(f"监控出错: {e}")
                
                # 等待下次检查
                for _ in range(self.config['interval']):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        return True
    
    def stop(self):
        """停止监控"""
        if not self.running:
            return
        
        self.stop_event.set()
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def get_status(self):
        """获取监控状态"""
        # 计算各状态订单数量
        status_counts = {
            'PLACED': 0,
            'PROCESSING': 0,
            'PREPARED_FOR_SHIPMENT': 0,
            'SHIPPED': 0,
            'DELIVERED': 0,
            'CANCELED': 0,
            'unknown': 0
        }
        
        # 计算待检查的订单数量
        orders = self.get_orders()
        pending_orders = 0
        checked_orders = 0
        
        for url in orders:
            # 如果从未查询过,需要查询
            if url not in self.results:
                pending_orders += 1
                continue
            
            prev_result = self.results[url]
            
            # 如果之前查询失败,需要重新查询
            if not prev_result.get('success'):
                pending_orders += 1
                continue
            
            # 如果信息不完整,需要重新查询
            if (prev_result.get('orderNumber') in ['-', None, ''] or
                prev_result.get('productName') in ['-', None, ''] or
                prev_result.get('status') in ['-', None, '']):
                pending_orders += 1
                continue
            
            # 信息完整,计入已完成
            checked_orders += 1
            
            # 统计状态
            status = prev_result.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts['unknown'] += 1
        
        return {
            'running': self.running,
            'interval': self.config['interval'],
            'threads': self.config['threads'],
            'totalOrders': len(orders),
            'lastCheck': self.last_check_time,
            'checkCount': self.check_count,
            'statusCounts': status_counts,
            'pendingOrders': pending_orders,
            'checkedOrders': checked_orders
        }


# 单例
_monitor = None

def get_monitor():
    global _monitor
    if _monitor is None:
        _monitor = OrderMonitor()
    return _monitor
