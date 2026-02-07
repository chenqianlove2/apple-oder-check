#!/usr/bin/env python3
"""
测试物流单号提取正则表达式
"""

import re

# 测试 URL
test_urls = [
    'http://wwwapps.ups.com/etracking/tracking.cgi?TypeOfInquiryNumber=T&InquiryNumber1=1ZA828Y90268769346',
    'http://wwwapps.ups.com/etracking/tracking.cgi?InquiryNumber=1ZA828Y90268769346',
    'https://www.ups.com/track?trackingNumber=1ZA828Y90268769346',
]

print("=" * 60)
print("测试物流单号提取")
print("=" * 60)

for url in test_urls:
    print(f"\n测试 URL: {url}")
    
    # 测试新的正则表达式（\d* 表示0个或多个数字）
    match = re.search(r'[?&]InquiryNumber\d*=([A-Z0-9]+)', url)
    if match:
        print(f"✅ 提取成功: {match.group(1)}")
    else:
        # 尝试备用方案
        match2 = re.search(r'[?&]trackingNumber=([A-Z0-9]+)', url)
        if match2:
            print(f"✅ 备用方案提取: {match2.group(1)}")
        else:
            print(f"❌ 提取失败")

print("\n" + "=" * 60)
