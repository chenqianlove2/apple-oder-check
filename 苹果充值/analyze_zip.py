#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZIP 文件分析工具
用于解压和分析第三方充值软件
"""

import zipfile
import os
import json
from pathlib import Path

def analyze_zip(zip_path):
    """分析 ZIP 文件内容"""
    print(f"🔍 分析文件: {zip_path}\n")
    
    if not os.path.exists(zip_path):
        print(f"❌ 文件不存在: {zip_path}")
        return
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 列出所有文件
            print("📋 ZIP 文件内容:")
            print("-" * 60)
            for info in zip_ref.filelist:
                size = info.file_size / 1024  # KB
                print(f"  📄 {info.filename}")
                print(f"     大小: {size:.2f} KB")
                print(f"     压缩: {info.compress_size / 1024:.2f} KB")
                print(f"     日期: {info.date_time}")
                print()
            
            # 解压到当前目录
            extract_path = os.path.join(os.path.dirname(zip_path), "extracted")
            os.makedirs(extract_path, exist_ok=True)
            
            print(f"\n📦 解压到: {extract_path}")
            zip_ref.extractall(extract_path)
            print("✅ 解压完成！")
            
            # 分析文件类型
            print("\n🔎 文件类型分析:")
            print("-" * 60)
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    rel_path = os.path.relpath(file_path, extract_path)
                    
                    if ext in ['.js', '.html', '.css']:
                        print(f"  🌐 网页文件: {rel_path}")
                    elif ext in ['.py', '.pyw']:
                        print(f"  🐍 Python 文件: {rel_path}")
                    elif ext in ['.json']:
                        print(f"  📊 配置文件: {rel_path}")
                    elif ext in ['.exe', '.app', '.dmg']:
                        print(f"  💻 可执行文件: {rel_path}")
                    elif ext in ['.dll', '.so', '.dylib']:
                        print(f"  🔧 库文件: {rel_path}")
                    else:
                        print(f"  📄 其他文件: {rel_path}")
            
            return extract_path
            
    except zipfile.BadZipFile:
        print("❌ 这不是一个有效的 ZIP 文件")
    except Exception as e:
        print(f"❌ 解压失败: {e}")

def find_interesting_files(extract_path):
    """查找可能包含 API 信息的文件"""
    print("\n\n🎯 查找关键文件:")
    print("-" * 60)
    
    keywords = ['api', 'config', 'settings', 'auth', 'token', 'key', 'apple']
    interesting_files = []
    
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            file_lower = file.lower()
            file_path = os.path.join(root, file)
            
            # 检查文件名是否包含关键词
            if any(keyword in file_lower for keyword in keywords):
                rel_path = os.path.relpath(file_path, extract_path)
                print(f"  ⭐ {rel_path}")
                interesting_files.append(file_path)
            
            # 检查特定文件类型
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.js', '.json', '.py', '.conf', '.ini', '.yaml', '.yml']:
                rel_path = os.path.relpath(file_path, extract_path)
                if file_path not in interesting_files:
                    print(f"  📝 {rel_path}")
                    interesting_files.append(file_path)
    
    return interesting_files

def preview_file_content(file_path, lines=50):
    """预览文件内容"""
    print(f"\n\n📖 预览文件: {os.path.basename(file_path)}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)  # 读取前 10KB
            print(content[:2000])  # 显示前 2000 字符
            if len(content) > 2000:
                print("\n... (内容已截断) ...")
    except Exception as e:
        print(f"无法读取文件: {e}")

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("  🔍 ZIP 文件分析工具")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
    else:
        # 查找当前目录下的 zip 文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        zip_files = list(Path(current_dir).glob("*.zip"))
        
        if not zip_files:
            print("❌ 未找到 ZIP 文件")
            print("\n使用方法:")
            print(f"  python3 {os.path.basename(__file__)} <zip文件路径>")
            print("\n或者将 ZIP 文件放在同一目录下")
            sys.exit(1)
        
        zip_path = str(zip_files[0])
    
    # 分析 ZIP 文件
    extract_path = analyze_zip(zip_path)
    
    if extract_path:
        # 查找关键文件
        interesting_files = find_interesting_files(extract_path)
        
        # 预览前几个关键文件
        if interesting_files:
            print("\n\n" + "=" * 60)
            print("  📄 关键文件预览")
            print("=" * 60)
            for file in interesting_files[:3]:  # 只预览前 3 个
                preview_file_content(file)
        
        print("\n\n✅ 分析完成！")
        print(f"📁 解压文件位置: {extract_path}")
        print("\n💡 接下来你可以:")
        print("  1. 查看 extracted 文件夹中的文件")
        print("  2. 搜索 API 相关的代码")
        print("  3. 分析网络请求逻辑")
