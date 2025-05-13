#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将hashmode.txt转换为JSON格式的脚本
将所有哈希模式转换为结构化的JSON数据
"""

import json
import re
import os
from pathlib import Path

def convert_hashmode_to_json():
    """
    读取hashmode.txt文件，解析其内容，然后转换成JSON格式保存到hash_modes.json
    """
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent

    # 输入和输出文件路径
    input_file = current_dir / "hashmode.txt"
    output_file = current_dir / "hash_modes.json"
    
    # 确保输入文件存在
    if not input_file.exists():
        print(f"错误: 未找到输入文件 {input_file}")
        return False
    
    # 读取hashmode.txt的内容
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # 初始化结果列表
    hash_modes = []
    
    # 正则表达式模式，匹配ID、名称和类别
    pattern = r'^\s*(\d+)\s+\|\s+(.+?)\s+\|\s+(.+?)\s*$'
    
    # 跳过标题行和分隔行
    for line in content[2:]:  # 跳过前两行(标题和分隔线)
        match = re.match(pattern, line)
        if match:
            hash_id = int(match.group(1).strip())
            hash_name = match.group(2).strip()
            hash_category = match.group(3).strip()
            
            # 添加到结果列表
            hash_modes.append({
                "id": hash_id,
                "name": hash_name,
                "category": hash_category
            })
    
    # 按ID排序
    hash_modes.sort(key=lambda x: x["id"])
    
    # 将结果写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hash_modes, f, indent=4, ensure_ascii=False)
    
    print(f"转换完成！共转换了 {len(hash_modes)} 个哈希模式")
    print(f"结果已保存到: {output_file}")
    return True

if __name__ == "__main__":
    convert_hashmode_to_json()
