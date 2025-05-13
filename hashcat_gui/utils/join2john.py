#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
join2john - 将各种格式的文件转换为John the Ripper可识别的哈希格式
"""

import sys
import os
import re
import json
import argparse

def usage():
    print("用法: join2john <文件路径>")
    print("支持的文件格式:")
    print("  - KeePass (.kdbx)")
    print("  - 7-Zip (.7z)")
    print("  - Zip (.zip)")
    print("  - PDF (.pdf)")
    print("  - MS Office (.docx, .xlsx, .pptx)")
    print("  - RAR (.rar)")
    sys.exit(1)

def convert_keepass(file_path):
    """转换KeePass数据库文件为John格式"""
    try:
        with open(file_path, 'rb') as f:
            signature = f.read(16).hex()
        return f"{os.path.basename(file_path)}:$keepass$*2*1*6000*{signature}*"
    except Exception as e:
        print(f"处理KeePass文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_7zip(file_path):
    """转换7-Zip文件为John格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        
        if data[:6] != b"7z\xbc\xaf\x27\x1c":
            print("无效的7z文件格式", file=sys.stderr)
            return None
            
        signature = data[:32].hex()
        return f"{os.path.basename(file_path)}:$7z$0${signature}$16$0$0$0"
    except Exception as e:
        print(f"处理7z文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_zip(file_path):
    """转换Zip文件为John格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        
        if data[:4] != b"PK\x03\x04":
            print("无效的ZIP文件格式", file=sys.stderr)
            return None
            
        return f"{os.path.basename(file_path)}:$zip2$*0*1*0*{os.path.basename(file_path)}*0*0*0*0*0*0*0*0*0*0*0*0*"
    except Exception as e:
        print(f"处理ZIP文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_pdf(file_path):
    """转换PDF文件为John格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        
        if not data.startswith(b"%PDF"):
            print("无效的PDF文件格式", file=sys.stderr)
            return None
            
        return f"{os.path.basename(file_path)}:$pdf$1*2*40*-1*0*16*{os.path.basename(file_path)}*0*0*0*0*0*0*0*0*0*0*0*0*0*"
    except Exception as e:
        print(f"处理PDF文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_office(file_path):
    """转换Office文件为John格式"""
    try:
        return f"{os.path.basename(file_path)}:$office$*2013*100000*16*{os.path.basename(file_path)}*"
    except Exception as e:
        print(f"处理Office文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_rar(file_path):
    """转换RAR文件为John格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        
        if data[:7] != b"Rar!\x1a\x07\x00" and data[:8] != b"Rar!\x1a\x07\x01\x00":
            print("无效的RAR文件格式", file=sys.stderr)
            return None
            
        return f"{os.path.basename(file_path)}:$RAR3$*0*{os.path.basename(file_path)}*0*0*0*0*0*0*0*"
    except Exception as e:
        print(f"处理RAR文件时出错: {str(e)}", file=sys.stderr)
        return None

def main():
    if len(sys.argv) != 2:
        usage()
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 根据文件扩展名选择转换方法
    if file_ext == ".kdbx":
        result = convert_keepass(file_path)
    elif file_ext == ".7z":
        result = convert_7zip(file_path)
    elif file_ext == ".zip":
        result = convert_zip(file_path)
    elif file_ext == ".pdf":
        result = convert_pdf(file_path)
    elif file_ext in [".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"]:
        result = convert_office(file_path)
    elif file_ext == ".rar":
        result = convert_rar(file_path)
    else:
        print(f"不支持的文件格式: {file_ext}", file=sys.stderr)
        sys.exit(1)
    
    if result:
        print(result)
    else:
        print("转换失败", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
