#!/usr/bin/env python3
"""清理不在 orders.txt 中的历史记录"""

import json

# 读取 orders.txt 中的所有订单 URL
with open('orders.txt', 'r') as f:
    valid_urls = set()
    for line in f:
        line = line.strip()
        if line.startswith('https://'):
            valid_urls.add(line)

print(f'orders.txt 中的订单数: {len(valid_urls)}')

# 读取历史记录
with open('order_history.json', 'r') as f:
    data = json.load(f)

results = data.get('results', {})
print(f'历史记录中的订单数: {len(results)}')

# 找出不在 orders.txt 中的订单
invalid_urls = []
for url in list(results.keys()):
    if url not in valid_urls:
        invalid_urls.append(url)
        order_num = results[url].get('orderNumber', 'Unknown')
        product = results[url].get('productName', 'Unknown')[:50]
        print(f'将删除: {order_num} - {product}')

if invalid_urls:
    print(f'\n总共将删除 {len(invalid_urls)} 个不在 orders.txt 中的订单')
    for url in invalid_urls:
        del results[url]
    
    data['results'] = results
    with open('order_history.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f'✅ 已删除 {len(invalid_urls)} 个无效订单')
    print(f'剩余订单数: {len(results)}')
else:
    print('\n✅ 所有历史记录都有效')
