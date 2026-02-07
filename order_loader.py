#!/usr/bin/env python3
"""
订单链接加载器 - 从文件读取订单链接
"""

import os


def load_orders_from_file(filepath='orders.txt'):
    """
    从文件加载订单链接
    
    文件格式:
    - 每行一个链接
    - 以 # 开头的行是注释
    - 空行会被忽略
    - 只保留以 http 开头的链接
    
    Args:
        filepath: 订单文件路径，默认 orders.txt
        
    Returns:
        list: 订单链接列表
    """
    orders = []
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        print(f"请创建 {filepath} 文件并添加订单链接")
        return orders
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 只保留 http 链接
                if line.startswith('http'):
                    orders.append(line)
                else:
                    print(f"⚠️  第 {line_num} 行被忽略（不是有效链接）: {line[:50]}")
        
        print(f"✅ 从 {filepath} 加载了 {len(orders)} 个订单链接")
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
    
    return orders


def save_orders_to_file(orders, filepath='orders.txt'):
    """
    保存订单链接到文件
    
    Args:
        orders: 订单链接列表
        filepath: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# 苹果订单链接列表\n")
            f.write("# 每行一个链接，以 http 开头\n")
            f.write("# 以 # 开头的行是注释\n\n")
            
            for url in orders:
                f.write(f"{url}\n")
        
        print(f"✅ 已保存 {len(orders)} 个订单到 {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def add_order_to_file(url, filepath='orders.txt'):
    """
    添加单个订单链接到文件
    
    Args:
        url: 订单链接
        filepath: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"{url}\n")
        
        print(f"✅ 已添加订单: {url[:60]}...")
        return True
        
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False


if __name__ == '__main__':
    # 测试
    orders = load_orders_from_file()
    print(f"\n加载的订单:")
    for i, url in enumerate(orders, 1):
        print(f"{i}. {url}")
