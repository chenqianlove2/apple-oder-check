#!/usr/bin/env python3
"""
修复历史数据中的物流单号
"""

import json
import re
import os

history_file = 'order_history.json'

print("=" * 60)
print("修复历史数据中的物流单号")
print("=" * 60)

if not os.path.exists(history_file):
    print("\n❌ 历史文件不存在")
    exit(1)

# 读取历史数据
with open(history_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('results', {})
fixed_count = 0

for url, result in results.items():
    if result.get('trackingUrl') and result['trackingUrl'] != '-':
        tracking_url = result['trackingUrl']
        
        # 尝试从 URL 提取物流单号
        match = re.search(r'[?&]InquiryNumber\d*=([A-Z0-9]+)', tracking_url)
        if not match:
            match = re.search(r'[?&]trackingNumber=([A-Z0-9]+)', tracking_url)
        
        if match:
            new_tracking_number = match.group(1)
            old_tracking_number = result.get('trackingNumber', '-')
            
            if old_tracking_number != new_tracking_number:
                result['trackingNumber'] = new_tracking_number
                fixed_count += 1
                print(f"\n✅ 修复订单: {result.get('orderNumber', 'N/A')}")
                print(f"   旧单号: {old_tracking_number}")
                print(f"   新单号: {new_tracking_number}")

# 保存修复后的数据
if fixed_count > 0:
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n" + "=" * 60)
    print(f"✅ 成功修复 {fixed_count} 个订单的物流单号")
    print(f"📝 已保存到 {history_file}")
else:
    print("\n✅ 没有需要修复的数据")

print("=" * 60)
