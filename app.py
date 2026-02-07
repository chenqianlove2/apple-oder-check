#!/usr/bin/env python3
"""
苹果订单查询工具 - 简化版
只保留查询超链接功能
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
import requests
import json
import threading
import csv
from urllib.parse import urlparse
from datetime import datetime


class AppleOrderQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("苹果订单查询工具")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # 数据存储
        self.order_data = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # 顶部输入区域
        input_frame = ttk.LabelFrame(self.root, text="输入订单链接", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.url_text = scrolledtext.ScrolledText(input_frame, height=6, wrap=tk.WORD)
        self.url_text.pack(fill=tk.BOTH, expand=True)
        self.url_text.insert(tk.END, "https://www.apple.com/xc/us/vieworder/W1356190467/13160170407@163.com\n")
        
        # 按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="开始查询", command=self.start_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空输入", command=self.clear_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="导出Excel(CSV)", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空结果", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(self.root, text="就绪")
        self.status_label.pack(anchor=tk.W, padx=10)
        
        # 结果表格区域
        result_frame = ttk.LabelFrame(self.root, text="查询结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ('no', 'url', 'status', 'order_no', 'order_date', 'product', 'delivery', 'address', 'tracking')
        self.tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=15)
        
        # 设置列
        self.tree.heading('no', text='序号')
        self.tree.heading('url', text='链接')
        self.tree.heading('status', text='订单状态')
        self.tree.heading('order_no', text='订单号')
        self.tree.heading('order_date', text='下单日期')
        self.tree.heading('product', text='购买设备')
        self.tree.heading('delivery', text='交货日期')
        self.tree.heading('address', text='地址信息')
        self.tree.heading('tracking', text='物流单号')
        
        self.tree.column('no', width=50, anchor='center')
        self.tree.column('url', width=200)
        self.tree.column('status', width=120)
        self.tree.column('order_no', width=100)
        self.tree.column('order_date', width=100)
        self.tree.column('product', width=150)
        self.tree.column('delivery', width=120)
        self.tree.column('address', width=150)
        self.tree.column('tracking', width=120)
        
        # 滚动条
        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
    def parse_url(self, url):
        """解析URL，提取订单号和邮箱"""
        pattern = r'/vieworder/([A-Z0-9]+)/([^/]+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def query_order(self, url):
        """查询单个订单"""
        order_no, email = self.parse_url(url)
        if not order_no:
            return {'success': False, 'error': '链接格式错误'}
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            # 访问订单页面
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            
            result = {
                'success': True,
                'order_no': order_no,
                'email': email,
                'url': url,
                'status': '查询失败',
                'order_date': '-',
                'product': '-',
                'delivery': '-',
                'address': '-',
                'tracking': '-'
            }
            
            # 解析页面内容
            html = response.text
            
            # 检查是否需要登录
            if 'signin' in response.url or '登录' in html or 'Sign In' in html:
                result['status'] = '需要登录'
                return result
            
            # 尝试解析订单状态
            # 不同地区的苹果网站可能有不同的页面结构
            # 这里使用一些通用的匹配模式
            
            # 订单状态
            status_patterns = [
                r'Processing',
                r'正在处理',
                r'Shipped',
                r'已发货',
                r'Delivered',
                r'已送达',
                r'Canceled',
                r'已取消',
                r'Order Received',
                r'订单已收到'
            ]
            
            for pattern in status_patterns:
                if pattern in html:
                    result['status'] = pattern
                    break
            else:
                if 'order' in html.lower() and 'apple' in html.lower():
                    result['status'] = '页面可访问'
            
            # 尝试提取产品名称
            product_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
            if product_match:
                product = re.sub(r'<[^>]+>', '', product_match.group(1)).strip()
                if product and len(product) < 100:
                    result['product'] = product
            
            # 尝试提取日期
            date_pattern = r'(\w+ \d{1,2}, \d{4}|\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}/\d{4})'
            dates = re.findall(date_pattern, html)
            if dates:
                result['order_date'] = dates[0]
            
            return result
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': '请求超时'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'网络错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'错误: {str(e)}'}
    
    def start_query(self):
        """开始批量查询"""
        urls_text = self.url_text.get('1.0', tk.END).strip()
        if not urls_text:
            messagebox.showwarning("提示", "请输入订单链接")
            return
        
        # 提取所有URL
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        urls = [url for url in urls if url.startswith('http')]
        
        if not urls:
            messagebox.showwarning("提示", "未找到有效的链接")
            return
        
        # 在后台线程中执行查询
        thread = threading.Thread(target=self.query_worker, args=(urls,))
        thread.daemon = True
        thread.start()
    
    def query_worker(self, urls):
        """查询工作线程"""
        self.order_data = []
        total = len(urls)
        
        self.root.after(0, lambda: self.status_label.config(text=f"正在查询 0/{total}"))
        self.root.after(0, lambda: self.progress.config(maximum=total, value=0))
        
        for i, url in enumerate(urls, 1):
            self.root.after(0, lambda v=i: self.progress.config(value=v))
            self.root.after(0, lambda v=i, t=total: self.status_label.config(text=f"正在查询 {v}/{t}"))
            
            result = self.query_order(url)
            self.order_data.append(result)
            
            # 更新表格
            self.root.after(0, lambda r=result, idx=i: self.add_result_to_table(r, idx))
            
        self.root.after(0, lambda: self.status_label.config(text=f"查询完成，共 {total} 条"))
        self.root.after(0, lambda: self.progress.config(value=total))
    
    def add_result_to_table(self, result, index):
        """添加结果到表格"""
        if result.get('success'):
            values = (
                index,
                result.get('url', '')[:50] + '...' if len(result.get('url', '')) > 50 else result.get('url', ''),
                result.get('status', '-'),
                result.get('order_no', '-'),
                result.get('order_date', '-'),
                result.get('product', '-'),
                result.get('delivery', '-'),
                result.get('address', '-'),
                result.get('tracking', '-')
            )
        else:
            values = (
                index,
                result.get('url', '')[:50] + '...' if len(result.get('url', '')) > 50 else result.get('url', ''),
                f"错误: {result.get('error', '未知错误')}",
                '-', '-', '-', '-', '-', '-'
            )
        
        self.tree.insert('', tk.END, values=values)
        self.tree.see(self.tree.get_children()[-1] if self.tree.get_children() else '')
    
    def clear_input(self):
        """清空输入"""
        self.url_text.delete('1.0', tk.END)
    
    def clear_results(self):
        """清空结果"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.order_data = []
        self.status_label.config(text="已清空")
    
    def export_csv(self):
        """导出CSV文件"""
        if not self.order_data:
            messagebox.showwarning("提示", "没有数据可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"订单查询结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['序号', '链接', '订单状态', '订单号', '下单日期', '购买设备', '交货日期', '地址信息', '物流单号', '查询结果'])
                
                for i, data in enumerate(self.order_data, 1):
                    if data.get('success'):
                        writer.writerow([
                            i,
                            data.get('url', ''),
                            data.get('status', '-'),
                            data.get('order_no', '-'),
                            data.get('order_date', '-'),
                            data.get('product', '-'),
                            data.get('delivery', '-'),
                            data.get('address', '-'),
                            data.get('tracking', '-'),
                            '成功'
                        ])
                    else:
                        writer.writerow([i, data.get('url', ''), '-', '-', '-', '-', '-', '-', '-', f"失败: {data.get('error', '')}"])
            
            messagebox.showinfo("成功", f"已导出到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def on_item_double_click(self, event):
        """双击打开链接"""
        item = self.tree.selection()[0]
        values = self.tree.item(item, 'values')
        if values and len(values) > 1:
            url = values[1]
            if url.startswith('http'):
                import webbrowser
                webbrowser.open(url)


def main():
    root = tk.Tk()
    app = AppleOrderQueryApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
