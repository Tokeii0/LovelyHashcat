#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
join2hashcat - 将各种格式的文件转换为hashcat可识别的哈希格式
"""

import sys
import os
import re
import json
import argparse

def usage():
    print("用法: join2hashcat <文件路径>")
    print("支持的文件格式:")
    print("  - KeePass (.kdbx)")
    print("  - 7-Zip (.7z)")
    print("  - Zip (.zip)")
    print("  - PDF (.pdf)")
    print("  - MS Office (.docx, .xlsx, .pptx)")
    print("  - RAR (.rar)")
    sys.exit(1)

def convert_keepass(file_path):
    """转换KeePass数据库文件为hashcat格式"""
    # 简单方式是提取前16字节作为签名
    try:
        with open(file_path, 'rb') as f:
            signature = f.read(16).hex()
        return f"$keepass$*2*1*6000*{signature}*"
    except Exception as e:
        print(f"处理KeePass文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_7zip(file_path):
    """转换7-Zip文件为hashcat格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)  # 读取前1024字节用于提取签名
        
        if data[:6] != b"7z\xbc\xaf\x27\x1c":
            print("无效的7z文件格式", file=sys.stderr)
            return None
            
        # 简化处理，实际应用中应当进行更复杂的提取
        signature = data[:32].hex()
        return f"$7z$0${signature}$16$0$0$0"
    except Exception as e:
        print(f"处理7z文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_zip(file_path):
    """转换Zip文件为hashcat格式"""
    try:
        import zipfile
        import binascii
        
        # 检查文件是否为有效的ZIP文件
        if not zipfile.is_zipfile(file_path):
            print("无效的ZIP文件格式", file=sys.stderr)
            return None
        
        # 尝试打开ZIP文件检查是否加密
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            if not file_list:
                print("ZIP文件中没有文件", file=sys.stderr)
                return None
            
            # 获取第一个文件进行哈希提取
            target_file = file_list[0]
            zip_info = zip_ref.getinfo(target_file)
            
            # 检查是否加密
            is_encrypted = (zip_info.flag_bits & 0x1) != 0
            if not is_encrypted:
                print("ZIP文件未加密", file=sys.stderr)
                return None
            
            # 提取加密数据
            # 读取文件头和加密数据
            with open(file_path, 'rb') as f:
                f.seek(zip_info.header_offset)
                header = f.read(30)  # Local file header
                
                if header[:4] != b'PK\x03\x04':
                    print("无效的ZIP文件头", file=sys.stderr)
                    return None
                
                name_len = int.from_bytes(header[26:28], byteorder='little')
                extra_len = int.from_bytes(header[28:30], byteorder='little')
                
                # 跳过文件名和额外字段
                f.seek(zip_info.header_offset + 30 + name_len + extra_len)
                
                # 读取加密数据头 (12字节)
                enc_header = f.read(12)
                
                # 转换为十六进制
                enc_header_hex = binascii.hexlify(enc_header).decode('ascii')
            
            method = zip_info.compress_type
            crc = zip_info.CRC
            
            # 构建hashcat格式的哈希字符串
            # $zip2$*模式*是否验证*分区数量*文件名长度*文件名*方法*CRC*压缩大小*解压大小*数据头*...
            zip_hash = f"$zip2$*0*1*0*{len(target_file)}*{target_file}*{method}*{crc:08x}*{zip_info.compress_size}*{zip_info.file_size}*{enc_header_hex}*$/zip2$"
            return zip_hash
            
    except Exception as e:
        print(f"处理ZIP文件时出错: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None

def convert_pdf(file_path):
    """转换PDF文件为hashcat格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        
        if not data.startswith(b"%PDF"):
            print("无效的PDF文件格式", file=sys.stderr)
            return None
            
        # 简化处理
        return f"$pdf$1*2*40*-1*0*16*{os.path.basename(file_path)}*0*0*0*0*0*0*0*0*0*0*0*0*0*"
    except Exception as e:
        print(f"处理PDF文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_office(file_path):
    """转换Office文件为hashcat格式"""
    try:
        # 简化处理，实际需要更复杂的解析
        return f"$office$*2013*100000*16*{os.path.basename(file_path)}*"
    except Exception as e:
        print(f"处理Office文件时出错: {str(e)}", file=sys.stderr)
        return None

def convert_rar(file_path):
    """转换RAR文件为hashcat格式"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024)
        
        if data[:7] != b"Rar!\x1a\x07\x00" and data[:8] != b"Rar!\x1a\x07\x01\x00":
            print("无效的RAR文件格式", file=sys.stderr)
            return None
            
        # 简化处理
        return f"$RAR3$*0*{os.path.basename(file_path)}*0*0*0*0*0*0*0*"
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
