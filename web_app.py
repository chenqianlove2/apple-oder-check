#!/usr/bin/env python3
"""
苹果订单查询工具 - Web 版本 (支持多线程)
"""

import re
import requests
import csv
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 全局线程池
executor = ThreadPoolExecutor(max_workers=10)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>苹果订单查询工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .card-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .input-area {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            resize: vertical;
            font-family: inherit;
        }
        .input-area:focus {
            outline: none;
            border-color: #667eea;
        }
        .settings-row {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .setting-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .setting-item label {
            font-size: 14px;
            color: #666;
        }
        .setting-item input[type="number"] {
            width: 60px;
            padding: 6px 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
        }
        .setting-item input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #218838;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }
        .status {
            color: #666;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .speed-info {
            font-size: 12px;
            color: #999;
        }
        .table-container {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }
        .status-processing {
            background: #fff3cd;
            color: #856404;
        }
        .status-shipped {
            background: #d1ecf1;
            color: #0c5460;
        }
        .status-delivered {
            background: #d4edda;
            color: #155724;
        }
        .status-canceled {
            background: #f8d7da;
            color: #721c24;
        }
        .status-pending {
            background: #e2e3e5;
            color: #383d41;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        .link-cell {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .link-cell a {
            color: #667eea;
            text-decoration: none;
        }
        .link-cell a:hover {
            text-decoration: underline;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        .stats {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .stat-item {
            background: #f8f9fa;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
        }
        .stat-item strong {
            color: #667eea;
            font-size: 1.2em;
        }
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            .btn-group {
                justify-content: center;
            }
            .btn {
                flex: 1;
                min-width: 120px;
            }
            .settings-row {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍎 苹果订单查询工具</h1>
            <p>批量查询苹果官网订单状态（支持多线程）</p>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span>🔗</span> 输入订单链接
            </div>
            <textarea class="input-area" id="urlInput" placeholder="请输入订单链接，每行一个...
例如：https://www.apple.com/xc/us/vieworder/W1356190467/13160170407@163.com"></textarea>
            
            <div class="settings-row">
                <div class="setting-item">
                    <label>并发线程数:</label>
                    <input type="number" id="threadCount" value="10" min="1" max="20">
                </div>
                <div class="setting-item">
                    <label>请求超时(秒):</label>
                    <input type="number" id="timeout" value="30" min="10" max="60">
                </div>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-primary" id="queryBtn" onclick="startQuery()">
                    <span>▶</span> 开始查询
                </button>
                <button class="btn btn-secondary" onclick="clearInput()">
                    <span>🗑</span> 清空输入
                </button>
                <button class="btn btn-secondary" onclick="loadExample()">
                    <span>📋</span> 加载示例
                </button>
                <button class="btn btn-success" onclick="exportCSV()" id="exportBtn" style="display:none;">
                    <span>📥</span> 导出 CSV
                </button>
            </div>
            
            <div class="progress-bar" id="progressBar" style="display:none;">
                <div class="progress-fill" id="progressFill" style="width: 0%"></div>
            </div>
            <div class="status">
                <span id="status">就绪</span>
                <span class="speed-info" id="speedInfo"></span>
            </div>
        </div>
        
        <div class="card" id="resultCard" style="display:none;">
            <div class="card-title">
                <span>📊</span> 查询结果
            </div>
            <div class="stats" id="stats"></div>
            <div class="table-container">
                <table id="resultTable">
                    <thead>
                        <tr>
                            <th>序号</th>
                            <th>链接</th>
                            <th>订单状态</th>
                            <th>订单号</th>
                            <th>下单日期</th>
                            <th>购买设备</th>
                            <th>预计送达</th>
                        </tr>
                    </thead>
                    <tbody id="resultBody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card" id="emptyCard">
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="9" y1="9" x2="15" y2="9"></line>
                    <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
                <p>请输入订单链接开始查询</p>
            </div>
        </div>
    </div>

    <script>
        let queryResults = [];
        let queryStartTime = null;
        
        function loadExample() {
            const examples = `https://www.apple.com/xc/us/vieworder/W1356190467/13160170407@163.com
https://www.apple.com/xc/us/vieworder/W1574786135/13160170407@163.com
https://www.apple.com/xc/us/vieworder/W1588741821/13160170407@163.com
https://www.apple.com/xc/us/vieworder/W1395280106/13160170407@163.com`;
            document.getElementById('urlInput').value = examples;
        }
        
        function clearInput() {
            document.getElementById('urlInput').value = '';
        }
        
        async function startQuery() {
            const input = document.getElementById('urlInput').value.trim();
            if (!input) {
                alert('请输入订单链接');
                return;
            }
            
            const urls = input.split('\\n').map(u => u.trim()).filter(u => u.startsWith('http'));
            if (urls.length === 0) {
                alert('未找到有效的链接');
                return;
            }
            
            const threadCount = parseInt(document.getElementById('threadCount').value) || 10;
            const timeout = parseInt(document.getElementById('timeout').value) || 30;
            
            queryResults = new Array(urls.length);
            queryStartTime = Date.now();
            
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            const status = document.getElementById('status');
            const speedInfo = document.getElementById('speedInfo');
            const exportBtn = document.getElementById('exportBtn');
            const queryBtn = document.getElementById('queryBtn');
            const tbody = document.getElementById('resultBody');
            
            tbody.innerHTML = '';
            progressBar.style.display = 'block';
            exportBtn.style.display = 'none';
            queryBtn.disabled = true;
            document.getElementById('emptyCard').style.display = 'none';
            document.getElementById('resultCard').style.display = 'block';
            
            let completed = 0;
            
            // 创建所有查询任务
            const tasks = urls.map((url, index) => ({ url, index }));
            
            // 分批处理，控制并发数
            const batchSize = threadCount;
            const batches = [];
            for (let i = 0; i < tasks.length; i += batchSize) {
                batches.push(tasks.slice(i, i + batchSize));
            }
            
            for (const batch of batches) {
                const batchPromises = batch.map(({ url, index }) => 
                    fetch('/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url, timeout })
                    })
                    .then(response => response.json())
                    .then(result => {
                        queryResults[index] = result;
                        addResultToTable(result, index + 1);
                        completed++;
                        
                        const progress = (completed / urls.length) * 100;
                        progressFill.style.width = progress + '%';
                        status.textContent = `正在查询 ${completed}/${urls.length}`;
                        
                        // 计算速度
                        const elapsed = (Date.now() - queryStartTime) / 1000;
                        const speed = completed / elapsed;
                        const remaining = (urls.length - completed) / speed;
                        speedInfo.textContent = `速度: ${speed.toFixed(1)} 个/秒 | 预计剩余: ${Math.ceil(remaining)} 秒`;
                    })
                    .catch(error => {
                        const errorResult = { success: false, error: error.message, url };
                        queryResults[index] = errorResult;
                        addResultToTable(errorResult, index + 1);
                        completed++;
                    })
                );
                
                // 等待当前批次完成
                await Promise.all(batchPromises);
            }
            
            const totalTime = ((Date.now() - queryStartTime) / 1000).toFixed(1);
            status.textContent = `查询完成，共 ${urls.length} 条，耗时 ${totalTime} 秒`;
            speedInfo.textContent = `平均速度: ${(urls.length / totalTime).toFixed(1)} 个/秒`;
            exportBtn.style.display = 'inline-flex';
            queryBtn.disabled = false;
            updateStats();
        }
        
        function addResultToTable(result, index) {
            const tbody = document.getElementById('resultBody');
            const row = document.createElement('tr');
            
            if (result.success) {
                const statusClass = getStatusClass(result.status);
                const statusText = formatStatus(result.status);
                row.innerHTML = `
                    <td>${index}</td>
                    <td class="link-cell"><a href="${result.url}" target="_blank">${result.url}</a></td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td>${result.orderNumber}</td>
                    <td>${result.orderDate}</td>
                    <td>${result.productName}</td>
                    <td>${result.deliveryDate}</td>
                `;
            } else {
                row.innerHTML = `
                    <td>${index}</td>
                    <td class="link-cell"><a href="${result.url}" target="_blank">${result.url}</a></td>
                    <td><span class="status-badge status-error">查询失败</span></td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                `;
            }
            
            tbody.appendChild(row);
        }
        
        function getStatusClass(status) {
            if (!status) return 'status-error';
            const s = status.toUpperCase();
            // 已下单/已处理 - 灰色
            if (s === 'PLACED') return 'status-pending';
            // 处理中/准备发货 - 黄色
            if (s === 'PROCESSING' || s === 'PREPARED_FOR_SHIPMENT') return 'status-processing';
            // 已发货 - 蓝色
            if (s === 'SHIPPED') return 'status-shipped';
            // 已送达 - 绿色
            if (s === 'DELIVERED') return 'status-delivered';
            // 已取消 - 红色
            if (s === 'CANCELED' || s === 'CANCELLED') return 'status-canceled';
            return 'status-processing';
        }
        
        function formatStatus(status) {
            if (!status) return '未知';
            // 统一的状态映射 - 与苹果官网一致
            const statusMap = {
                'PLACED': 'Order Placed',
                'PROCESSING': 'Processing',
                'PREPARED_FOR_SHIPMENT': 'Preparing to Ship',
                'SHIPPED': 'Shipped',
                'DELIVERED': 'Delivered',
                'CANCELED': 'Canceled',
                'CANCELLED': 'Canceled',
                // 兼容旧值
                'PROCESSING_LONG': 'Processing'
            };
            return statusMap[status] || status;
        }
        
        function updateStats() {
            const total = queryResults.length;
            const success = queryResults.filter(r => r && r.success).length;
            const placed = queryResults.filter(r => r && r.success && r.status === 'PLACED').length;
            const processing = queryResults.filter(r => r && r.success && (r.status === 'PROCESSING' || r.status === 'PREPARED_FOR_SHIPMENT')).length;
            const shipped = queryResults.filter(r => r && r.success && r.status === 'SHIPPED').length;
            const delivered = queryResults.filter(r => r && r.success && r.status === 'DELIVERED').length;
            const canceled = queryResults.filter(r => r && r.success && (r.status === 'CANCELED' || r.status === 'CANCELLED')).length;
            
            let statsHtml = `<div class="stat-item">总计: <strong>${total}</strong></div>`;
            statsHtml += `<div class="stat-item">成功: <strong style="color: #28a745;">${success}</strong></div>`;
            if (placed > 0) statsHtml += `<div class="stat-item">已下单: <strong style="color: #6c757d;">${placed}</strong></div>`;
            if (processing > 0) statsHtml += `<div class="stat-item">处理中: <strong style="color: #856404;">${processing}</strong></div>`;
            if (shipped > 0) statsHtml += `<div class="stat-item">已发货: <strong style="color: #0c5460;">${shipped}</strong></div>`;
            if (delivered > 0) statsHtml += `<div class="stat-item">已送达: <strong style="color: #155724;">${delivered}</strong></div>`;
            if (canceled > 0) statsHtml += `<div class="stat-item">已取消: <strong style="color: #721c24;">${canceled}</strong></div>`;
            
            document.getElementById('stats').innerHTML = statsHtml;
        }
        
        function exportCSV() {
            if (queryResults.length === 0) {
                alert('没有数据可导出');
                return;
            }
            
            let csv = '序号,链接,订单状态,订单号,下单日期,购买设备,预计送达,查询结果\\n';
            
            queryResults.forEach((r, i) => {
                if (r && r.success) {
                    csv += `${i+1},"${r.url}","${r.status}","${r.orderNumber}","${r.orderDate}","${r.productName}","${r.deliveryDate}",成功\\n`;
                } else {
                    csv += `${i+1},"${r.url || ''}","-","-","-","-","-",失败\\n`;
                }
            });
            
            const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `订单查询结果_${new Date().toISOString().slice(0,10)}.csv`;
            link.click();
        }
    </script>
</body>
</html>
'''


def parse_url(url):
    """解析URL，提取订单号和邮箱"""
    pattern = r'/vieworder/([A-Z0-9]+)/([^/]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def query_order(url, timeout=30):
    """查询单个订单"""
    order_no, email = parse_url(url)
    if not order_no:
        return {'success': False, 'error': '链接格式错误', 'url': url}
    
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
            'orderNumber': order_no,
            'orderDate': '-',
            'productName': '-',
            'status': '-',
            'deliveryDate': '-',
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
        
        # 提取状态 (使用 currentStatus，更标准)
        status_match = re.search(r'"currentStatus"\s*:\s*"([^"]+)"', html)
        if status_match:
            result['status'] = status_match.group(1)
        else:
            # 备用：使用 statusDescription
            status_match = re.search(r'"statusDescription"\s*:\s*"([^"]+)"', html)
            if status_match:
                result['status'] = status_match.group(1)
        
        # 提取配送日期
        delivery_match = re.search(r'"deliveryDate"\s*:\s*"([^"]+)"', html)
        if delivery_match:
            result['deliveryDate'] = delivery_match.group(1)
        
        # 如果没找到关键数据
        if result['productName'] == '-' and result['status'] == '-':
            if 'signin' in response.url.lower():
                result['status'] = '需要登录'
            else:
                result['status'] = '无法获取数据'
        
        return result
        
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '请求超时', 'url': url}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'网络错误: {str(e)}', 'url': url}
    except Exception as e:
        return {'success': False, 'error': str(e), 'url': url}


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/query':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            url = data.get('url', '')
            timeout = data.get('timeout', 30)
            result = query_order(url, timeout)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


def main():
    port = 8080
    server = HTTPServer(('127.0.0.1', port), RequestHandler)
    print(f"\n🍎 苹果订单查询工具已启动（支持多线程）")
    print(f"📱 请在浏览器中访问: http://127.0.0.1:{port}\n")
    
    webbrowser.open(f'http://127.0.0.1:{port}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        executor.shutdown(wait=False)


if __name__ == '__main__':
    main()
