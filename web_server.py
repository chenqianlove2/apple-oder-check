#!/usr/bin/env python3
"""
苹果订单监控 Web 服务器
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import webbrowser
from datetime import datetime
from web_monitor import get_monitor
from notifier import get_notifier


# HTML 模板 - 批量查询页面
QUERY_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量查询 - 苹果订单监控</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav-btn { padding: 10px 20px; background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; font-size: 14px; }
        .nav-btn:hover { background: rgba(255,255,255,0.3); }
        .nav-btn.active { background: white; color: #667eea; }
        .card { background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .card-title { font-size: 1.2em; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
        .input-area { width: 100%; min-height: 120px; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; resize: vertical; }
        .input-area:focus { outline: none; border-color: #667eea; }
        .settings-row { display: flex; gap: 20px; margin-top: 15px; align-items: center; flex-wrap: wrap; }
        .setting-item { display: flex; align-items: center; gap: 8px; }
        .setting-item label { font-size: 14px; color: #666; }
        .setting-item input { width: 60px; padding: 6px 10px; border: 2px solid #e0e0e0; border-radius: 6px; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-success { background: #28a745; color: white; }
        .progress-bar { width: 100%; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; margin: 15px 0; }
        .progress-fill { height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); transition: width 0.3s; }
        .status { color: #666; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }
        .speed-info { font-size: 12px; color: #999; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; position: sticky; top: 0; }
        tr:hover { background: #f8f9fa; }
        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .status-PLACED { background: #e2e3e5; color: #383d41; }
        .status-PROCESSING { background: #fff3cd; color: #856404; }
        .status-PREPARED_FOR_SHIPMENT { background: #fff3cd; color: #856404; }
        .status-SHIPPED { background: #d1ecf1; color: #0c5460; }
        .status-DELIVERED { background: #d4edda; color: #155724; }
        .status-CANCELED { background: #f8d7da; color: #721c24; }
        .status-error { background: #f8d7da; color: #721c24; }
        .link-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .link-cell a { color: #667eea; text-decoration: none; }
        .link-cell a:hover { text-decoration: underline; }
        .stats { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
        .stat-item { background: #f8f9fa; padding: 10px 20px; border-radius: 8px; font-size: 14px; }
        .stat-item strong { color: #667eea; font-size: 1.2em; }
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8em; }
            .btn-group { justify-content: center; }
            .btn { flex: 1; min-width: 120px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 批量查询订单</h1>
            <p>一次性查询多个订单状态</p>
        </div>
        
        <div class="nav">
            <a href="/" class="nav-btn">📊 监控面板</a>
            <a href="/query" class="nav-btn active">🔍 批量查询</a>
            <a href="/settings" class="nav-btn">⚙️ 设置</a>
        </div>
        
        <div class="card">
            <div class="card-title">🔗 输入订单链接</div>
            <textarea class="input-area" id="urlInput" placeholder="请输入订单链接，每行一个...
例如：https://www.apple.com/xc/us/vieworder/W1356190467/13160170407@163.com"></textarea>
            
            <div class="settings-row">
                <div class="setting-item">
                    <label>并发线程:</label>
                    <input type="number" id="threadCount" value="10" min="1" max="20">
                </div>
                <div class="setting-item">
                    <label>超时(秒):</label>
                    <input type="number" id="timeout" value="30" min="10" max="60">
                </div>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-primary" id="queryBtn" onclick="startQuery()">▶ 开始查询</button>
                <button class="btn btn-secondary" onclick="clearInput()">🗑 清空</button>
                <button class="btn btn-success" onclick="exportCSV()" id="exportBtn" style="display:none;">📥 导出 CSV</button>
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
            <div class="card-title">📊 查询结果</div>
            <div class="stats" id="stats"></div>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>序号</th>
                            <th>链接</th>
                            <th>订单状态</th>
                            <th>订单号</th>
                            <th>下单日期</th>
                            <th>购买设备</th>
                            <th>预计送达</th>
                            <th>物流单号</th>
                            <th>查询次数</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="resultBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let queryResults = [];
        let queryStartTime = null;
        
        function clearInput() {
            document.getElementById('urlInput').value = '';
        }
        
        // 查询单个订单，支持重试
        async function queryOrderWithRetry(url, timeout, maxRetries = 2) {
            let lastError = null;
            
            for (let attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url, timeout})
                    });
                    const result = await response.json();
                    
                    // 如果查询成功，直接返回
                    if (result.success) {
                        return result;
                    }
                    
                    // 如果查询失败且还有重试次数
                    lastError = result;
                    if (attempt < maxRetries) {
                        console.log(`订单 ${url.split('/').slice(-2,-1)[0]} 查询失败，重试 ${attempt + 1}/${maxRetries}...`);
                        await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
                    }
                } catch (error) {
                    lastError = {success: false, url, error: error.message};
                    if (attempt < maxRetries) {
                        console.log(`订单查询出错，重试 ${attempt + 1}/${maxRetries}...`);
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                }
            }
            
            // 所有重试都失败，返回最后的错误
            return lastError;
        }

        async function startQuery() {
            const input = document.getElementById('urlInput').value.trim();
            if (!input) { alert('请输入订单链接'); return; }
            
            const urls = input.split('\\n').map(u => u.trim()).filter(u => u.startsWith('http'));
            if (urls.length === 0) { alert('未找到有效链接'); return; }
            
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
            document.getElementById('resultCard').style.display = 'block';
            
            let completed = 0;
            const batchSize = threadCount;
            
            // 第一轮查询（带重试）
            for (let i = 0; i < urls.length; i += batchSize) {
                const batch = urls.slice(i, i + batchSize);
                const batchPromises = batch.map(async (url, idx) => {
                    const index = i + idx;
                    const result = await queryOrderWithRetry(url, timeout, 2);
                    queryResults[index] = result;
                    addResultToTable(result, index + 1);
                    completed++;
                    progressFill.style.width = (completed / urls.length * 100) + '%';
                    status.textContent = `正在查询订单状态 ${completed}/${urls.length}`;
                    const elapsed = (Date.now() - queryStartTime) / 1000;
                    speedInfo.textContent = `速度: ${(completed/elapsed).toFixed(1)} 个/秒`;
                });
                await Promise.all(batchPromises);
            }
            
            // 统计已发货但缺少物流单号的订单
            const shippedWithoutTrackingIndices = [];
            queryResults.forEach((result, index) => {
                if (result && result.success && result.status === 'SHIPPED') {
                    if (!result.trackingNumber || result.trackingNumber === '-') {
                        shippedWithoutTrackingIndices.push(index);
                    }
                }
            });
            
            // 如果有已发货但缺少物流单号的订单，显示提示
            if (shippedWithoutTrackingIndices.length > 0) {
                status.textContent = `检测到 ${shippedWithoutTrackingIndices.length} 个已发货订单缺少物流单号，正在查询...`;
                console.log(`发现 ${shippedWithoutTrackingIndices.length} 个 SHIPPED 订单需要查询物流单号`);
                
                // 注：物流单号实际上在第一次查询时就已经提取了
                // 这里只是更新显示状态
                for (const index of shippedWithoutTrackingIndices) {
                    const result = queryResults[index];
                    console.log(`订单 ${result.orderNumber}: 物流单号 ${result.trackingNumber || '未找到'}`);
                }
            }
            
            // 统计失败的订单
            const failedIndices = [];
            queryResults.forEach((result, index) => {
                if (!result || !result.success) {
                    failedIndices.push(index);
                }
            });
            
            // 如果有失败的订单，进行第二轮完整重试
            if (failedIndices.length > 0) {
                status.textContent = `第一轮完成，重试 ${failedIndices.length} 个失败的订单...`;
                
                for (let i = 0; i < failedIndices.length; i += batchSize) {
                    const batch = failedIndices.slice(i, i + batchSize);
                    const retryPromises = batch.map(async (index) => {
                        const url = urls[index];
                        status.textContent = `重试失败订单 ${i + 1}/${failedIndices.length}...`;
                        const result = await queryOrderWithRetry(url, timeout, 2);
                        queryResults[index] = result;
                        
                        // 更新表格中的这一行
                        const tbody = document.getElementById('resultBody');
                        const rows = tbody.getElementsByTagName('tr');
                        if (rows[index]) {
                            rows[index].remove();
                        }
                        addResultToTable(result, index + 1);
                    });
                    await Promise.all(retryPromises);
                }
            }
            
            const totalTime = ((Date.now() - queryStartTime) / 1000).toFixed(1);
            const finalFailedCount = queryResults.filter(r => !r || !r.success).length;
            const shippedCount = queryResults.filter(r => r && r.success && r.status === 'SHIPPED').length;
            const shippedWithTracking = queryResults.filter(r => r && r.success && r.status === 'SHIPPED' && r.trackingNumber && r.trackingNumber !== '-').length;
            
            let statusMsg = `查询完成，共 ${urls.length} 条，成功 ${urls.length - finalFailedCount} 条，失败 ${finalFailedCount} 条`;
            if (shippedCount > 0) {
                statusMsg += `，已发货 ${shippedCount} 条（含物流单号 ${shippedWithTracking} 条）`;
            }
            statusMsg += `，耗时 ${totalTime} 秒`;
            
            status.textContent = statusMsg;
            exportBtn.style.display = 'inline-block';
            queryBtn.disabled = false;
            updateStats();
        }
        
        function addResultToTable(result, index) {
            const tbody = document.getElementById('resultBody');
            const row = document.createElement('tr');
            row.id = `row-${index}`;
            const statusMap = {'PLACED':'Order Placed','PROCESSING':'Processing','PREPARED_FOR_SHIPMENT':'Preparing to Ship','SHIPPED':'Shipped','DELIVERED':'Delivered','CANCELED':'Canceled'};
            
            if (result.success) {
                const status = result.status || 'unknown';
                const trackingNumber = result.trackingNumber || '-';
                
                // 显示物流查询提示
                let trackingCell = trackingNumber;
                if (status === 'SHIPPED') {
                    if (trackingNumber && trackingNumber !== '-') {
                        trackingCell = `<span style="color:#28a745;">${trackingNumber}</span>`;
                    } else {
                        trackingCell = `<span style="color:#999;">查询中...</span>`;
                    }
                }
                
                // 查询次数显示
                const queryCount = result.queryCount || 0;
                const queryCountCell = queryCount > 0 ? `<span style="color:#666;">🔍 ${queryCount}</span>` : `<span style="color:#999;">0</span>`;
                
                row.innerHTML = `
                    <td>${index}</td>
                    <td class="link-cell"><a href="${result.url}" target="_blank">${result.url}</a></td>
                    <td><span class="status-badge status-${status}">${statusMap[status] || status}</span></td>
                    <td>${result.orderNumber}</td>
                    <td>${result.orderDate}</td>
                    <td>${result.productName}</td>
                    <td>${result.deliveryDate}</td>
                    <td>${trackingCell}</td>
                    <td>${queryCountCell}</td>
                    <td><button class="btn btn-primary" onclick="recheckOrder(${index - 1}, '${result.url}')" style="padding:6px 12px;font-size:12px;">🔄 检查</button></td>
                `;
            } else {
                row.innerHTML = `
                    <td>${index}</td>
                    <td class="link-cell"><a href="${result.url}" target="_blank">${result.url}</a></td>
                    <td><span class="status-badge status-error">查询失败</span></td>
                    <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                    <td><button class="btn btn-primary" onclick="recheckOrder(${index - 1}, '${result.url}')" style="padding:6px 12px;font-size:12px;">🔄 检查</button></td>
                `;
            }
            tbody.appendChild(row);
        }
        
        // 重新检查单个订单
        async function recheckOrder(index, url) {
            const row = document.getElementById(`row-${index + 1}`);
            if (!row) {
                alert('无法找到该订单');
                return;
            }
            
            // 显示检查中状态
            const cells = row.getElementsByTagName('td');
            cells[2].innerHTML = '<span class="status-badge" style="background:#ffc107;color:#000;">🔄 检查中...</span>';
            
            // 禁用按钮
            const btn = row.querySelector('button');
            if (btn) {
                btn.disabled = true;
                btn.textContent = '⏳ 检查中';
            }
            
            try {
                const timeout = parseInt(document.getElementById('timeout').value) || 30;
                const result = await queryOrderWithRetry(url, timeout, 2);
                
                // 更新结果
                queryResults[index] = result;
                
                // 移除旧行
                row.remove();
                
                // 添加新行
                addResultToTable(result, index + 1);
                
                // 更新统计
                updateStats();
                
                if (result.success) {
                    console.log(`✅ 订单 ${result.orderNumber} 重新检查成功`);
                } else {
                    console.log(`❌ 订单重新检查失败: ${result.error}`);
                }
            } catch (error) {
                console.error('检查出错:', error);
                alert('检查失败: ' + error.message);
                
                // 恢复按钮
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '🔄 检查';
                }
            }
        }
        
        function updateStats() {
            const total = queryResults.length;
            const success = queryResults.filter(r => r && r.success).length;
            const processing = queryResults.filter(r => r && r.success && r.status === 'PROCESSING').length;
            const shipped = queryResults.filter(r => r && r.success && r.status === 'SHIPPED').length;
            const delivered = queryResults.filter(r => r && r.success && r.status === 'DELIVERED').length;
            
            let html = `<div class="stat-item">总计: <strong>${total}</strong></div>`;
            html += `<div class="stat-item">成功: <strong style="color:#28a745;">${success}</strong></div>`;
            if (processing) html += `<div class="stat-item">处理中: <strong style="color:#856404;">${processing}</strong></div>`;
            if (shipped) html += `<div class="stat-item">已发货: <strong style="color:#0c5460;">${shipped}</strong></div>`;
            if (delivered) html += `<div class="stat-item">已送达: <strong style="color:#155724;">${delivered}</strong></div>`;
            document.getElementById('stats').innerHTML = html;
        }
        
        function exportCSV() {
            if (!queryResults.length) { alert('没有数据'); return; }
            let csv = '序号,链接,状态,订单号,下单日期,产品,预计送达,物流单号\\n';
            queryResults.forEach((r, i) => {
                if (r && r.success) {
                    const trackingNumber = r.trackingNumber || '-';
                    csv += `${i+1},"${r.url}","${r.status}","${r.orderNumber}","${r.orderDate}","${r.productName}","${r.deliveryDate}","${trackingNumber}"\\n`;
                } else {
                    csv += `${i+1},"${r.url}","-","-","-","-","-","-"\\n`;
                }
            });
            const blob = new Blob(['\\ufeff'+csv], {type:'text/csv'});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `订单查询_${new Date().toISOString().slice(0,10)}.csv`;
            link.click();
        }
    </script>
</body>
</html>
'''

# HTML 模板 - 监控管理页面
MONITOR_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>苹果订单监控管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .nav-btn {
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
        }
        .nav-btn:hover { background: rgba(255,255,255,0.3); }
        .nav-btn.active { background: white; color: #667eea; }
        
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
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* 状态面板 */
        .status-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .status-item .value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .status-item .label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .status-item.running .value { color: #28a745; }
        .status-item.stopped .value { color: #dc3545; }
        .countdown-item .value { 
            color: #667eea; 
            font-family: 'Courier New', monospace;
            font-size: 1.6em;
        }
        
        /* 状态统计筛选 */
        .status-stats {
            border-top: 2px solid #f0f0f0;
            padding-top: 15px;
        }
        .stats-filter {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .filter-btn {
            padding: 8px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s;
        }
        .filter-btn:hover {
            border-color: #667eea;
            color: #667eea;
        }
        .filter-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
        }
        
        /* 控制按钮 */
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
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
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-danger { background: #dc3545; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        
        /* 设置表单 */
        .form-row {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .form-group {
            flex: 1;
            min-width: 200px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-size: 14px;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        /* 订单列表 */
        .order-list {
            max-height: 500px;
            overflow-y: auto;
        }
        .order-item {
            display: flex;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
            gap: 15px;
        }
        .order-item:hover { background: #f8f9fa; }
        .order-info { flex: 1; }
        .order-number {
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }
        .order-product {
            color: #666;
            font-size: 13px;
            margin-top: 3px;
        }
        .order-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-PLACED { background: #e2e3e5; color: #383d41; }
        .status-PROCESSING { background: #fff3cd; color: #856404; }
        .status-PREPARED_FOR_SHIPMENT { background: #fff3cd; color: #856404; }
        .status-SHIPPED { background: #d1ecf1; color: #0c5460; }
        .status-DELIVERED { background: #d4edda; color: #155724; }
        .status-CANCELED { background: #f8d7da; color: #721c24; }
        .status-unknown { background: #f8f9fa; color: #666; }
        
        .order-actions { display: flex; gap: 8px; }
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
        }
        .btn-check { background: #17a2b8; color: white; }
        .btn-delete { background: #dc3545; color: white; }
        .btn-check:disabled { opacity: 0.5; }
        
        /* 添加订单 */
        .add-order-form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .add-order-form input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }
        
        /* 状态变更记录 */
        .change-log {
            max-height: 300px;
            overflow-y: auto;
        }
        .change-item {
            padding: 12px 15px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }
        .change-time {
            font-size: 12px;
            color: #999;
        }
        .change-content {
            margin-top: 5px;
            font-size: 14px;
        }
        
        /* 刷新动画 */
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .refreshing {
            animation: spin 1s linear infinite;
        }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8em; }
            .order-item { flex-wrap: wrap; }
            .order-actions { width: 100%; margin-top: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍎 苹果订单监控管理</h1>
            <p>可视化监控你的所有订单</p>
        </div>
        
        <div class="nav">
            <a href="/" class="nav-btn">📊 监控面板</a>
            <a href="/query" class="nav-btn">🔍 批量查询</a>
            <a href="/settings" class="nav-btn">⚙️ 设置</a>
        </div>
        
        <div class="card">
            <div class="card-title">📈 监控状态</div>
            <div class="status-panel">
                <div class="status-item" id="monitorStatus">
                    <div class="value" id="statusText">--</div>
                    <div class="label">监控状态</div>
                </div>
                <div class="status-item">
                    <div class="value" id="orderCount">--</div>
                    <div class="label">监控订单</div>
                </div>
                <div class="status-item">
                    <div class="value" id="checkCount">--</div>
                    <div class="label">检查次数</div>
                </div>
                <div class="status-item">
                    <div class="value" id="lastCheck">--</div>
                    <div class="label">上次检查</div>
                </div>
                <div class="status-item countdown-item" id="countdownItem" style="display:none;">
                    <div class="value" id="countdown">--:--</div>
                    <div class="label">下次检查倒计时</div>
                </div>
            </div>
            
            <!-- 状态统计 -->
            <div class="status-stats" id="statusStats" style="margin-top: 20px; display: none;">
                <div class="card-title">📊 订单状态统计</div>
                <div class="stats-filter">
                    <button class="filter-btn active" data-filter="all" onclick="filterOrders('all')">
                        全部 (<span id="count-all">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="PLACED" onclick="filterOrders('PLACED')">
                        📋 已下单 (<span id="count-placed">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="PROCESSING" onclick="filterOrders('PROCESSING')">
                        ⏳ 处理中 (<span id="count-processing">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="PREPARED_FOR_SHIPMENT" onclick="filterOrders('PREPARED_FOR_SHIPMENT')">
                        📦 准备发货 (<span id="count-prepared">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="SHIPPED" onclick="filterOrders('SHIPPED')">
                        🚚 已发货 (<span id="count-shipped">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="DELIVERED" onclick="filterOrders('DELIVERED')">
                        ✅ 已送达 (<span id="count-delivered">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="CANCELED" onclick="filterOrders('CANCELED')">
                        ❌ 已取消 (<span id="count-canceled">0</span>)
                    </button>
                    <button class="filter-btn" data-filter="unknown" onclick="filterOrders('unknown')">
                        ❓ 未知 (<span id="count-unknown">0</span>)
                    </button>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn btn-success" id="startBtn" onclick="startMonitor()">▶ 启动监控</button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopMonitor()">⏹ 停止监控</button>
                <button class="btn btn-primary" id="checkBtn" onclick="checkNow()">🔄 立即检查</button>
                <button class="btn btn-secondary" onclick="refreshData()">📥 刷新数据</button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">➕ 添加订单（支持批量添加，每行一个链接）</div>
            <div class="add-order-form" style="flex-direction:column;align-items:stretch;">
                <textarea id="newOrderUrl" placeholder="https://www.apple.com/xc/us/vieworder/订单号1/邮箱1&#10;https://www.apple.com/xc/us/vieworder/订单号2/邮箱2&#10;https://www.apple.com/xc/us/vieworder/订单号3/邮箱3" style="min-height:100px;margin-bottom:10px;font-family:inherit;"></textarea>
                <div style="display:flex;gap:10px;">
                    <button class="btn btn-primary" onclick="addOrder()" id="addOrderBtn" style="flex:1;">📥 添加订单</button>
                    <button class="btn btn-secondary" onclick="document.getElementById('newOrderUrl').value=''">🗑️ 清空</button>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title" style="display:flex;justify-content:space-between;align-items:center;">
                <span>📋 监控订单列表</span>
                <button class="btn btn-danger" onclick="deleteAllOrders(event)" style="font-size:12px;padding:6px 12px;">🗑️ 全部删除</button>
            </div>
            <div class="order-list" id="orderList">
                <p style="text-align:center;color:#999;padding:40px;">加载中...</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title" style="display:flex;justify-content:space-between;align-items:center;">
                <span>📜 查询历史记录</span>
                <button class="btn btn-danger" onclick="clearAllHistory()" style="font-size:12px;padding:6px 12px;">🗑️ 清空历史</button>
            </div>
            <div class="history-list" id="historyList">
                <p style="text-align:center;color:#999;padding:20px;">加载中...</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">📜 状态变更记录</div>
            <div class="change-log" id="changeLog">
                <p style="text-align:center;color:#999;padding:20px;">暂无记录</p>
            </div>
        </div>
    </div>

    <script>
        let autoRefresh = null;
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', () => {
            refreshData();
            // 每10秒自动刷新
            autoRefresh = setInterval(refreshData, 10000);
        });
        
        // 全局状态
        let currentFilter = 'all';
        let orderStats = {};
        let allOrdersData = null;
        
        // 倒计时相关变量
        let countdownInterval = null;
        let nextCheckTime = null;
        let monitorInterval = 300;
        
        // 刷新数据
        async function refreshData() {
            try {
                // 获取监控状态
                const statusRes = await fetch('/api/monitor/status');
                const status = await statusRes.json();
                updateStatusPanel(status);
                
                // 更新倒计时配置
                monitorInterval = status.interval || 300;
                
                // 获取订单列表
                const ordersRes = await fetch('/api/monitor/orders');
                const orders = await ordersRes.json();
                allOrdersData = orders;
                
                // 计算并显示状态统计
                calculateStats(orders);
                updateOrderList(orders, currentFilter);
                
                // 获取变更记录
                const changesRes = await fetch('/api/monitor/changes');
                const changes = await changesRes.json();
                updateChangeLog(changes);
                
                // 获取历史记录
                const historyRes = await fetch('/api/monitor/history');
                const history = await historyRes.json();
                updateHistoryList(history);
                
            } catch (e) {
                console.error('刷新失败:', e);
            }
        }
        
        // 计算状态统计
        function calculateStats(data) {
            const stats = {
                all: data.orders.length,
                PLACED: 0,
                PROCESSING: 0,
                PREPARED_FOR_SHIPMENT: 0,
                SHIPPED: 0,
                DELIVERED: 0,
                CANCELED: 0,
                unknown: 0
            };
            
            data.orders.forEach(order => {
                const result = data.results[order.url] || {};
                const status = result.status || 'unknown';
                if (stats.hasOwnProperty(status)) {
                    stats[status]++;
                } else {
                    stats.unknown++;
                }
            });
            
            orderStats = stats;
            
            // 更新统计显示
            document.getElementById('count-all').textContent = stats.all;
            document.getElementById('count-placed').textContent = stats.PLACED;
            document.getElementById('count-processing').textContent = stats.PROCESSING;
            document.getElementById('count-prepared').textContent = stats.PREPARED_FOR_SHIPMENT;
            document.getElementById('count-shipped').textContent = stats.SHIPPED;
            document.getElementById('count-delivered').textContent = stats.DELIVERED;
            document.getElementById('count-canceled').textContent = stats.CANCELED;
            document.getElementById('count-unknown').textContent = stats.unknown;
            
            // 显示统计区域
            document.getElementById('statusStats').style.display = stats.all > 0 ? 'block' : 'none';
        }
        
        // 筛选订单
        function filterOrders(status) {
            currentFilter = status;
            
            // 更新按钮状态
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.filter === status) {
                    btn.classList.add('active');
                }
            });
            
            // 更新列表
            if (allOrdersData) {
                updateOrderList(allOrdersData, status);
            }
        }
        
        // 更新状态面板
        function updateStatusPanel(status) {
            const statusEl = document.getElementById('statusText');
            const statusItem = document.getElementById('monitorStatus');
            
            if (status.running) {
                // 显示智能检查状态
                if (status.pendingOrders && status.pendingOrders > 0) {
                    statusEl.textContent = `智能检查中 (${status.checkedOrders || 0}/${status.pendingOrders})`;
                } else {
                    statusEl.textContent = '监控轮询中';
                }
                statusItem.classList.add('running');
                statusItem.classList.remove('stopped');
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                
                // 显示并启动倒计时
                document.getElementById('countdownItem').style.display = 'block';
                startCountdown(status.interval, status.lastCheck);
            } else {
                statusEl.textContent = '已停止';
                statusItem.classList.add('stopped');
                statusItem.classList.remove('running');
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                
                // 隐藏倒计时
                document.getElementById('countdownItem').style.display = 'none';
                stopCountdown();
            }
            
            document.getElementById('orderCount').textContent = status.totalOrders;
            document.getElementById('checkCount').textContent = status.checkCount;
            
            if (status.lastCheck) {
                const date = new Date(status.lastCheck);
                document.getElementById('lastCheck').textContent = 
                    date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
            } else {
                document.getElementById('lastCheck').textContent = '--';
            }
        }
        
        // 根据服务端 lastCheck 计算倒计时
        function startCountdown(interval, lastCheck) {
            stopCountdown();
            if (lastCheck) {
                const lastCheckMs = new Date(lastCheck).getTime();
                nextCheckTime = lastCheckMs + interval * 1000;
                // 如果计算出的时间已经过去，说明正在检查或即将检查
                if (nextCheckTime < Date.now()) {
                    nextCheckTime = Date.now() + 5000;
                }
            } else {
                nextCheckTime = Date.now() + interval * 1000;
            }
            updateCountdown();
            countdownInterval = setInterval(updateCountdown, 1000);
        }

        // 停止倒计时
        function stopCountdown() {
            if (countdownInterval) {
                clearInterval(countdownInterval);
                countdownInterval = null;
            }
        }

        // 更新倒计时显示
        function updateCountdown() {
            if (!nextCheckTime) return;

            const remaining = Math.max(0, nextCheckTime - Date.now());
            const minutes = Math.floor(remaining / 60000);
            const seconds = Math.floor((remaining % 60000) / 1000);

            document.getElementById('countdown').textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // 更新订单列表
        function updateOrderList(data, filter = 'all') {
            const list = document.getElementById('orderList');
            
            if (data.orders.length === 0) {
                list.innerHTML = '<p style="text-align:center;color:#999;padding:40px;">暂无订单，请添加</p>';
                return;
            }
            
            const statusNames = {
                'PLACED': 'Order Placed',
                'PROCESSING': 'Processing',
                'PREPARED_FOR_SHIPMENT': 'Preparing to Ship',
                'SHIPPED': 'Shipped',
                'DELIVERED': 'Delivered',
                'CANCELED': 'Canceled'
            };
            
            // 筛选订单
            let filteredOrders = data.orders;
            if (filter !== 'all') {
                filteredOrders = data.orders.filter(order => {
                    const result = data.results[order.url] || {};
                    const status = result.status || 'unknown';
                    return status === filter;
                });
            }
            
            if (filteredOrders.length === 0) {
                list.innerHTML = `<p style="text-align:center;color:#999;padding:40px;">该状态暂无订单</p>`;
                return;
            }
            
            list.innerHTML = filteredOrders.map(order => {
                const url = order.url;
                const result = data.results[url] || {};
                const status = result.status || 'unknown';
                const orderNo = result.orderNumber || url.split('/').slice(-2, -1)[0];
                const product = result.productName || '未知产品';
                const trackingNumber = result.trackingNumber || '';
                const queryCount = result.queryCount || 0;
                
                // 如果状态是 SHIPPED 且有物流单号，显示在产品名称下方
                let trackingInfo = '';
                if (status === 'SHIPPED' && trackingNumber && trackingNumber !== '-') {
                    trackingInfo = `<div style="font-size:12px;color:#007bff;margin-top:4px;">� 物流单号: ${trackingNumber}</div>`;
                }
                
                // 查询次数显示
                const queryCountBadge = queryCount > 0 
                    ? `<span style="font-size:11px;background:#f0f0f0;color:#666;padding:2px 8px;border-radius:10px;margin-left:8px;">🔍 ${queryCount}次</span>`
                    : '';
                
                return `
                    <div class="order-item">
                        <div class="order-info">
                            <div class="order-number">${orderNo}${queryCountBadge}</div>
                            <div class="order-product">${product}${trackingInfo}</div>
                        </div>
                        <div class="order-status status-${status}">${statusNames[status] || status}</div>
                        <div class="order-actions">
                            <button class="btn-small btn-check" onclick="checkOrder('${url}')">检查</button>
                            <button class="btn-small btn-delete" onclick="deleteOrder('${url}')">删除</button>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        // 更新变更记录
        function updateChangeLog(changes) {
            const log = document.getElementById('changeLog');
            
            if (changes.length === 0) {
                log.innerHTML = '<p style="text-align:center;color:#999;padding:20px;">暂无记录</p>';
                return;
            }
            
            const statusNames = {
                'PLACED': 'Order Placed',
                'PROCESSING': 'Processing',
                'PREPARED_FOR_SHIPMENT': 'Preparing to Ship',
                'SHIPPED': 'Shipped',
                'DELIVERED': 'Delivered',
                'CANCELED': 'Canceled'
            };
            
            log.innerHTML = changes.slice().reverse().map(change => {
                const time = new Date(change.timestamp).toLocaleString('zh-CN');
                return `
                    <div class="change-item">
                        <div class="change-time">${time}</div>
                        <div class="change-content">
                            <b>${change.orderNumber}</b> - ${change.productName}<br>
                            ${statusNames[change.oldStatus] || change.oldStatus} → 
                            <b>${statusNames[change.newStatus] || change.newStatus}</b>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        // 更新历史记录列表
        function updateHistoryList(history) {
            const list = document.getElementById('historyList');
            
            if (!history || history.length === 0) {
                list.innerHTML = '<p style="text-align:center;color:#999;padding:20px;">暂无历史记录</p>';
                return;
            }
            
            const statusEmoji = {
                'PLACED': '📝',
                'PROCESSING': '⚙️',
                'PREPARED_FOR_SHIPMENT': '📋',
                'SHIPPED': '📦',
                'DELIVERED': '✅',
                'CANCELED': '🚨'
            };
            
            const statusNames = {
                'PLACED': 'Order Placed',
                'PROCESSING': 'Processing',
                'PREPARED_FOR_SHIPMENT': 'Preparing to Ship',
                'SHIPPED': 'Shipped',
                'DELIVERED': 'Delivered',
                'CANCELED': 'Canceled'
            };
            
            list.innerHTML = `
                <table style="width:100%;border-collapse:collapse;">
                    <thead>
                        <tr style="background:#f5f5f5;text-align:left;">
                            <th style="padding:8px;">订单号</th>
                            <th style="padding:8px;">产品</th>
                            <th style="padding:8px;">状态</th>
                            <th style="padding:8px;">查询时间</th>
                            <th style="padding:8px;text-align:center;">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${history.map(item => {
                            const time = new Date(item.timestamp).toLocaleString('zh-CN');
                            const emoji = statusEmoji[item.status] || '📄';
                            const statusName = statusNames[item.status] || item.status;
                            const statusColor = item.status === 'CANCELED' ? 'red' : 
                                               item.status === 'SHIPPED' ? 'green' : 
                                               item.status === 'DELIVERED' ? 'blue' : '#666';
                            
                            return `
                                <tr style="border-bottom:1px solid #eee;">
                                    <td style="padding:8px;"><b>${item.orderNumber}</b></td>
                                    <td style="padding:8px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item.productName}">${item.productName}</td>
                                    <td style="padding:8px;color:${statusColor};">${emoji} ${statusName}</td>
                                    <td style="padding:8px;font-size:12px;color:#999;">${time}</td>
                                    <td style="padding:8px;text-align:center;">
                                        <button class="btn btn-secondary" onclick="deleteHistory('${item.url.replace(/'/g, "\\'")}', '${item.orderNumber}')" style="font-size:11px;padding:4px 8px;">删除</button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            `;
        }
        
        // 删除单个历史记录
        async function deleteHistory(url, orderNumber) {
            if (!confirm(`确定要删除订单 ${orderNumber} 的历史记录吗？\\n\\n删除后，下次监控时会重新查询该订单。`)) {
                return;
            }
            
            try {
                const res = await fetch('/api/monitor/history', {
                    method: 'DELETE',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                
                const result = await res.json();
                if (result.success) {
                    alert(`✅ 已删除订单 ${orderNumber} 的历史记录`);
                    refreshData();
                } else {
                    alert('删除失败: ' + result.message);
                }
            } catch (e) {
                alert('删除失败: ' + e);
            }
        }
        
        // 清空所有历史记录
        async function clearAllHistory() {
            const historyRes = await fetch('/api/monitor/history');
            const history = await historyRes.json();
            
            if (!history || history.length === 0) {
                alert('没有历史记录可清空');
                return;
            }
            
            if (!confirm(`确定要清空所有 ${history.length} 条历史记录吗？\\n\\n此操作不可恢复！\\n清空后，下次监控时会重新查询所有订单。`)) {
                return;
            }
            
            try {
                const clearBtn = event.target;
                clearBtn.disabled = true;
                clearBtn.textContent = '清空中...';
                
                const res = await fetch('/api/monitor/history/clear', {
                    method: 'POST'
                });
                
                const result = await res.json();
                
                clearBtn.textContent = '🗑️ 清空历史';
                clearBtn.disabled = false;
                
                if (result.success) {
                    alert(`✅ 已清空 ${result.count} 条历史记录`);
                    refreshData();
                } else {
                    alert('清空失败: ' + result.message);
                }
            } catch (e) {
                const clearBtn = event.target;
                clearBtn.textContent = '🗑️ 清空历史';
                clearBtn.disabled = false;
                alert('清空失败: ' + e);
            }
        }
        
        // 启动监控
        async function startMonitor() {
            document.getElementById('startBtn').disabled = true;
            try {
                await fetch('/api/monitor/start', {method: 'POST'});
                setTimeout(refreshData, 500);
            } catch (e) {
                alert('启动失败: ' + e);
            }
        }
        
        // 停止监控
        async function stopMonitor() {
            document.getElementById('stopBtn').disabled = true;
            try {
                await fetch('/api/monitor/stop', {method: 'POST'});
                setTimeout(refreshData, 500);
            } catch (e) {
                alert('停止失败: ' + e);
            }
        }
        
        // 立即检查
        async function checkNow() {
            const btn = document.getElementById('checkBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="refreshing">🔄</span> 检查中...';
            
            try {
                await fetch('/api/monitor/check', {method: 'POST'});
                setTimeout(() => {
                    refreshData();
                    btn.disabled = false;
                    btn.innerHTML = '🔄 立即检查';
                }, 2000);
            } catch (e) {
                alert('检查失败: ' + e);
                btn.disabled = false;
                btn.innerHTML = '🔄 立即检查';
            }
        }
        
        // 添加订单（支持批量）
        async function addOrder() {
            console.log('addOrder 被调用');
            const input = document.getElementById('newOrderUrl');
            if (!input) {
                console.error('找不到 newOrderUrl 元素');
                alert('页面错误: 找不到输入框');
                return;
            }
            
            const textarea = input.value.trim();
            console.log('输入内容:', textarea);
            
            if (!textarea) {
                alert('请输入订单链接');
                return;
            }
            
            // 解析多行链接
            const urls = textarea.split(String.fromCharCode(10))
                .map(u => u.trim())
                .filter(u => u && u.startsWith('http'));
            
            console.log('解析到的 URLs:', urls);
            
            if (urls.length === 0) {
                alert('未找到有效的订单链接');
                return;
            }
            
            const btn = document.getElementById('addOrderBtn');
            if (!btn) {
                console.error('找不到 addOrderBtn 按钮');
            }
            
            const originalText = btn ? btn.innerHTML : '添加订单';
            if (btn) btn.disabled = true;
            if (btn) btn.innerHTML = `📥 正在添加 ${urls.length} 个订单...`;
            
            try {
                console.log('发送请求...');
                const res = await fetch('/api/monitor/orders', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({urls: urls})
                });
                console.log('收到响应:', res.status);
                const data = await res.json();
                console.log('响应数据:', data);
                
                if (data.success) {
                    input.value = '';
                    refreshData();
                    
                    // 显示详细结果
                    let msg = data.message || '添加成功';
                    const details = data.details;
                    if (details && details.failed && details.failed.length > 0) {
                        msg += '\\n\\n失败的订单:';
                        details.failed.slice(0, 5).forEach(f => {
                            msg += `\\n- ${f.url.split('/').slice(-2, -1)[0]}: ${f.reason}`;
                        });
                        if (details.failed.length > 5) {
                            msg += `\\n... 还有 ${details.failed.length - 5} 个`;
                        }
                    }
                    alert(msg);
                } else {
                    alert(data.message || '添加失败');
                }
            } catch (e) {
                console.error('请求失败:', e);
                alert('请求失败: ' + e);
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                }
            }
        }
        
        // 删除订单
        async function deleteOrder(url) {
            if (!confirm('确定要删除这个订单吗？')) return;
            
            try {
                const res = await fetch('/api/monitor/orders', {
                    method: 'DELETE',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await res.json();
                
                if (data.success) {
                    refreshData();
                } else {
                    alert(data.message || '删除失败');
                }
            } catch (e) {
                alert('请求失败: ' + e);
            }
        }
        
        // 全部删除
        async function deleteAllOrders() {
            if (!allOrdersData || allOrdersData.orders.length === 0) {
                alert('没有订单可删除');
                return;
            }
            
            const count = allOrdersData.orders.length;
            if (!confirm(`确定要删除所有 ${count} 个订单吗？\\n\\n此操作不可恢复！`)) {
                return;
            }
            
            try {
                const deleteBtn = event.target;
                deleteBtn.disabled = true;
                deleteBtn.textContent = '删除中...';
                
                let successCount = 0;
                let failCount = 0;
                
                // 逐个删除订单（避免并发问题）
                for (const order of allOrdersData.orders) {
                    try {
                        const res = await fetch('/api/monitor/orders', {
                            method: 'DELETE',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({url: order.url})
                        });
                        const result = await res.json();
                        if (result.success) {
                            successCount++;
                        } else {
                            failCount++;
                            console.error('删除失败:', order.url, result.message);
                        }
                    } catch (err) {
                        failCount++;
                        console.error('删除出错:', order.url, err);
                    }
                    
                    // 更新进度
                    deleteBtn.textContent = `删除中 ${successCount + failCount}/${count}`;
                }
                
                deleteBtn.textContent = '🗑️ 全部删除';
                deleteBtn.disabled = false;
                
                await refreshData();
                
                if (failCount > 0) {
                    alert(`✅ 成功删除 ${successCount} 个订单\\n❌ 失败 ${failCount} 个订单`);
                } else {
                    alert(`✅ 已删除所有 ${successCount} 个订单`);
                }
            } catch (e) {
                const deleteBtn = event.target;
                deleteBtn.textContent = '🗑️ 全部删除';
                deleteBtn.disabled = false;
                alert('删除失败: ' + e);
                await refreshData();
            }
        }
        
        // 检查单个订单
        async function checkOrder(url) {
            const orderNo = url.split('/').slice(-2, -1)[0];
            const btns = document.querySelectorAll('.btn-check');
            btns.forEach(b => { if (b.onclick && b.onclick.toString().includes(url)) b.disabled = true; });

            try {
                const res = await fetch('/api/monitor/check_one', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const result = await res.json();

                if (result.success) {
                    const statusNames = {'PLACED':'Order Placed','PROCESSING':'Processing','PREPARED_FOR_SHIPMENT':'Preparing to Ship','SHIPPED':'Shipped','DELIVERED':'Delivered','CANCELED':'Canceled'};
                    alert(`${orderNo}: ${statusNames[result.status] || result.status}\\n${result.productName}\\n${result.deliveryDate}`);
                } else {
                    alert(`${orderNo}: 查询失败`);
                }
                refreshData();
            } catch (e) {
                alert('查询失败: ' + e);
            } finally {
                btns.forEach(b => b.disabled = false);
            }
        }
        
        // 页面关闭时清理
        window.addEventListener('beforeunload', () => {
            if (autoRefresh) clearInterval(autoRefresh);
        });
    </script>
</body>
</html>
'''


# 设置页面 HTML
SETTINGS_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>监控设置 - 苹果订单监控</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .nav-btn {
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
        }
        .nav-btn:hover { background: rgba(255,255,255,0.3); }
        .nav-btn.active { background: white; color: #667eea; }
        
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
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-hint {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .success-msg {
            background: #d4edda;
            color: #155724;
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚙️ 监控设置</h1>
            <p>配置监控参数</p>
        </div>
        
        <div class="nav">
            <a href="/" class="nav-btn">📊 监控面板</a>
            <a href="/query" class="nav-btn">🔍 批量查询</a>
            <a href="/settings" class="nav-btn active">⚙️ 设置</a>
        </div>
        
        <div class="card">
            <div class="success-msg" id="successMsg">✅ 设置已保存</div>
            
            <div class="card-title">⏱ 监控参数</div>
            
            <div class="current-config" id="currentConfig" style="background:#f8f9fa;padding:15px;border-radius:8px;margin-bottom:20px;font-size:14px;color:#666;">
                加载中...
            </div>
            
            <div class="form-group">
                <label>循环延时 / 检查间隔（秒）</label>
                <input type="number" id="interval" min="60" max="3600" value="300">
                <div class="form-hint">设置每隔多少秒检查一次订单状态，建议 300 秒（5分钟），太短可能被苹果限制</div>
            </div>
            
            <div class="form-group">
                <label>监测线程数</label>
                <input type="number" id="threads" min="1" max="20" value="10">
                <div class="form-hint">同时查询的订单数（并发数），建议 5-10，根据网络情况调整</div>
            </div>
            
            <div class="form-group">
                <label>请求超时（秒）</label>
                <input type="number" id="timeout" min="10" max="60" value="30">
                <div class="form-hint">单个订单查询的最大等待时间</div>
            </div>
            
            <button class="btn btn-primary" onclick="saveSettings()">💾 保存设置</button>
        </div>
        
        <div class="card">
            <div class="card-title">📱 Telegram 通知设置</div>
            
            <div class="form-group">
                <label>Bot Token</label>
                <input type="text" id="botToken" placeholder="123456789:ABCdefGHI...">
                <div class="form-hint">从 @BotFather 获取</div>
            </div>
            
            <div class="form-group">
                <label>Chat ID</label>
                <input type="text" id="chatId" placeholder="12345678">
                <div class="form-hint">从 @userinfobot 获取</div>
            </div>
            
            <button class="btn btn-primary" onclick="saveTelegram()">💾 保存 Telegram 设置</button>
            <button class="btn btn-primary" onclick="testTelegram()" style="margin-left:10px;background:#17a2b8;">🧪 测试连接</button>
        </div>
    </div>

    <script>
        // 加载当前设置
        async function loadSettings() {
            try {
                const res = await fetch('/api/monitor/config');
                const config = await res.json();
                
                document.getElementById('interval').value = config.interval || 300;
                document.getElementById('threads').value = config.threads || 10;
                document.getElementById('timeout').value = config.timeout || 30;
                
                // 更新当前配置显示
                const intervalMin = Math.round((config.interval || 300) / 60 * 10) / 10;
                document.getElementById('currentConfig').innerHTML = `
                    <b>当前配置：</b>循环延时 ${config.interval || 300}秒（约${intervalMin}分钟） | 
                    监测线程 ${config.threads || 10}个 | 
                    超时 ${config.timeout || 30}秒
                `;
            } catch (e) {
                console.error('加载设置失败:', e);
                document.getElementById('currentConfig').innerHTML = '<span style="color:#dc3545;">加载配置失败</span>';
            }
            
            // 加载 Telegram 配置
            try {
                const res = await fetch('/api/telegram/config');
                const config = await res.json();
                
                document.getElementById('botToken').value = config.bot_token || '';
                document.getElementById('chatId').value = config.chat_id || '';
            } catch (e) {
                console.error('加载 Telegram 配置失败:', e);
            }
        }
        
        // 保存监控设置
        async function saveSettings() {
            const data = {
                interval: parseInt(document.getElementById('interval').value),
                threads: parseInt(document.getElementById('threads').value),
                timeout: parseInt(document.getElementById('timeout').value)
            };
            
            try {
                await fetch('/api/monitor/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                showSuccess('✅ 监控设置已保存');
            } catch (e) {
                alert('保存失败: ' + e);
            }
        }
        
        // 保存 Telegram 设置
        async function saveTelegram() {
            const data = {
                bot_token: document.getElementById('botToken').value,
                chat_id: document.getElementById('chatId').value
            };
            
            try {
                await fetch('/api/telegram/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                showSuccess('✅ Telegram 设置已保存');
            } catch (e) {
                alert('保存失败: ' + e);
            }
        }
        
        // 测试 Telegram
        async function testTelegram() {
            try {
                const res = await fetch('/api/telegram/test', {method: 'POST'});
                const data = await res.json();
                alert(data.success ? '✅ ' + data.message : '❌ ' + data.message);
            } catch (e) {
                alert('测试失败: ' + e);
            }
        }
        
        function showSuccess(msg) {
            const el = document.getElementById('successMsg');
            el.textContent = msg;
            el.style.display = 'block';
            setTimeout(() => el.style.display = 'none', 3000);
        }
        
        // 页面加载时
        loadSettings();
    </script>
</body>
</html>
'''


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        path = self.path.split('?')[0]
        
        if path == '/' or path == '/monitor':
            self.send_html(MONITOR_HTML)
        elif path == '/settings':
            self.send_html(SETTINGS_HTML)
        elif path == '/query':
            self.send_html(QUERY_HTML)
        elif path == '/api/monitor/status':
            self.send_json(get_monitor().get_status())
        elif path == '/api/monitor/orders':
            monitor = get_monitor()
            self.send_json({
                'orders': [{'url': url} for url in monitor.get_orders()],
                'results': monitor.results
            })
        elif path == '/api/monitor/changes':
            self.send_json(get_monitor().status_changes)
        elif path == '/api/monitor/history':
            # 获取历史记录列表
            monitor = get_monitor()
            history = []
            for url, result in monitor.results.items():
                if result.get('success'):
                    history.append({
                        'url': url,
                        'orderNumber': result.get('orderNumber', '-'),
                        'productName': result.get('productName', '-'),
                        'status': result.get('status', '-'),
                        'timestamp': result.get('timestamp', '-')
                    })
            # 按时间倒序排序
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            self.send_json(history)
        elif path == '/api/monitor/config':
            self.send_json(get_monitor().config)
        elif path == '/api/telegram/config':
            self.send_json(get_notifier().get_config())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        path = self.path.split('?')[0]
        data = self.read_body()
        
        if path == '/api/monitor/start':
            result = get_monitor().start()
            self.send_json({'success': result})
        elif path == '/api/monitor/stop':
            get_monitor().stop()
            self.send_json({'success': True})
        elif path == '/api/monitor/check':
            # 后台执行检查
            import threading
            threading.Thread(target=get_monitor().check_all_orders, daemon=True).start()
            self.send_json({'success': True})
        elif path == '/api/monitor/check_one':
            # 检查单个订单
            url = data.get('url', '')
            if url:
                result = get_monitor().query_order(url)
                if result.get('success'):
                    # 更新结果
                    old_result = get_monitor().results.get(url, {})
                    old_status = old_result.get('status')
                    new_status = result.get('status')
                    if old_status and old_status != new_status:
                        change = {
                            'url': url,
                            'orderNumber': result.get('orderNumber'),
                            'productName': result.get('productName'),
                            'oldStatus': old_status,
                            'newStatus': new_status,
                            'timestamp': datetime.now().isoformat()
                        }
                        get_monitor().status_changes.append(change)
                    get_monitor().results[url] = result
                    get_monitor().save_history()
                self.send_json(result)
            else:
                self.send_json({'success': False, 'error': '缺少 url 参数'})
        elif path == '/api/monitor/orders':
            # 添加订单（支持单个或批量）
            monitor = get_monitor()
            urls = data.get('urls', [])
            
            # 兼容单个 url 参数
            if not urls and data.get('url'):
                urls = [data.get('url')]
            
            if not urls:
                self.send_json({'success': False, 'message': '没有提供订单链接'})
                return
            
            results = {'success': [], 'failed': [], 'skipped': []}
            
            for url in urls:
                url = url.strip()
                if not url:
                    continue
                if not url.startswith('http'):
                    results['failed'].append({'url': url, 'reason': '无效的链接格式'})
                    continue
                    
                success, msg = monitor.add_order(url)
                if success:
                    results['success'].append(url)
                elif '已存在' in msg:
                    results['skipped'].append({'url': url, 'reason': msg})
                else:
                    results['failed'].append({'url': url, 'reason': msg})
            
            # 保存历史
            monitor.save_history()

            # 后台自动查询新添加的订单
            new_urls = results['success']
            if new_urls:
                import threading
                def query_new_orders():
                    from notifier import get_notifier
                    notifier = get_notifier()
                    
                    for url in new_urls:
                        try:
                            # 记录查询前是否在历史中
                            is_new = url not in monitor.results
                            
                            result = monitor.query_order(url)
                            if result.get('success'):
                                # 检查是否是首次查询且状态为 CANCELED
                                if is_new and result.get('status') == 'CANCELED':
                                    print(f"🚨 新订单 {result.get('orderNumber')} 首次查询即为 CANCELED，发送通知", flush=True)
                                    if notifier.enabled:
                                        try:
                                            notifier.send_order_notification(result, None)
                                            print(f"✅ 通知已发送", flush=True)
                                        except Exception as e:
                                            print(f"❌ 发送通知失败: {e}", flush=True)
                                
                                monitor.results[url] = result
                        except Exception as e:
                            print(f"查询订单失败: {e}", flush=True)
                    monitor.save_history()
                threading.Thread(target=query_new_orders, daemon=True).start()

            total = len(results['success']) + len(results['failed']) + len(results['skipped'])
            if len(results['success']) == total:
                msg = f'成功添加 {len(results["success"])} 个订单'
            elif len(results['failed']) == 0:
                msg = f'添加 {len(results["success"])} 个，跳过 {len(results["skipped"])} 个已存在的订单'
            else:
                msg = f'添加 {len(results["success"])} 个，失败 {len(results["failed"])} 个，跳过 {len(results["skipped"])} 个'

            self.send_json({
                'success': len(results['failed']) == 0 or len(results['success']) > 0,
                'message': msg,
                'details': results
            })
        elif path == '/api/monitor/config':
            # 更新配置
            monitor = get_monitor()
            for key in ['interval', 'threads', 'timeout']:
                if key in data:
                    monitor.config[key] = data[key]
            monitor.save_config()
            self.send_json({'success': True})
        elif path == '/api/telegram/config':
            notifier = get_notifier()
            notifier.set_config(data.get('bot_token'), data.get('chat_id'))
            self.send_json({'success': True})
        elif path == '/api/telegram/test':
            success, msg = get_notifier().test_connection()
            self.send_json({'success': success, 'message': msg})
        elif path == '/api/monitor/history/clear':
            # 清空所有历史记录
            monitor = get_monitor()
            count = len(monitor.results)
            monitor.results.clear()
            monitor.save_history()
            self.send_json({'success': True, 'count': count, 'message': f'已清空 {count} 条历史记录'})
        elif path == '/api/query':
            # 批量查询单个订单
            try:
                url = data.get('url', '')
                timeout = data.get('timeout', 30)
                
                # 打印日志
                print(f"[查询] URL: {url.split('/')[-2] if '/' in url else url}")
                
                result = get_monitor().query_order(url)
                
                # 打印结果
                if result.get('success'):
                    print(f"[成功] 订单号: {result.get('orderNumber', '-')}")
                else:
                    print(f"[失败] 错误: {result.get('error', '未知')}")
                
                self.send_json(result)
            except Exception as e:
                print(f"[异常] {str(e)}")
                self.send_json({
                    'success': False,
                    'url': url,
                    'error': f'服务器错误: {str(e)}'
                })
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_DELETE(self):
        path = self.path.split('?')[0]
        data = self.read_body()
        
        if path == '/api/monitor/orders':
            url = data.get('url', '')
            success, msg = get_monitor().delete_order(url)
            self.send_json({'success': success, 'message': msg})
        elif path == '/api/monitor/history':
            # 删除单条历史记录
            url = data.get('url', '')
            monitor = get_monitor()
            if url and url in monitor.results:
                del monitor.results[url]
                monitor.save_history()
                self.send_json({'success': True, 'message': '历史记录已删除'})
            else:
                self.send_json({'success': False, 'message': '未找到该历史记录'})
        else:
            self.send_response(404)
            self.end_headers()
    
    def read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"解析请求体失败: {e}")
                return {}
        return {}
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass


def main():
    port = 8080  # 使用 8080 端口
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    
    # 获取本机 IP
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
    
    print(f"\n🍎 苹果订单监控管理已启动")
    print(f"📊 本地访问: http://127.0.0.1:{port}")
    print(f"🌐 局域网访问: http://{local_ip}:{port}")
    print(f"🔍 批量查询: http://{local_ip}:{port}/query")
    print(f"⚙️  设置页面: http://{local_ip}:{port}/settings\n")
    
    # webbrowser.open(f'http://127.0.0.1:{port}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")


if __name__ == '__main__':
    main()
