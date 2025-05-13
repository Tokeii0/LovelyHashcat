#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Potfile解析器 - 处理potfile的读取和解析
"""

import os
import re


def parse_potfile(potfile_path, hash_list=None):
    """
    解析potfile文件，提取哈希和对应的密码

    Args:
        potfile_path (str): potfile的路径
        hash_list (list, optional): 要筛选的哈希列表，如果提供，只返回列表中存在的哈希

    Returns:
        dict: 哈希与密码的映射字典 {hash_val: password}
    """
    if not potfile_path or not os.path.exists(potfile_path):
        return {}

    results = {}
    hash_set = set(hash_list) if hash_list else None

    try:
        with open(potfile_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 处理不同格式的potfile条目
                if ':' in line:
                    # 标准格式: hash:password
                    parts = line.split(':', 1)
                    if len(parts) >= 2:
                        hash_val = parts[0].strip()
                        password = parts[1].strip()
                        
                        # 如果有指定哈希列表，则只保留列表中的哈希
                        if not hash_set or hash_val in hash_set:
                            results[hash_val] = password
                else:
                    # 尝试其他可能的格式
                    continue
    except Exception as e:
        print(f"解析potfile时出错: {str(e)}")

    return results


def read_hash_file(hash_file_path):
    """
    读取哈希文件，获取所有哈希值

    Args:
        hash_file_path (str): 哈希文件路径

    Returns:
        list: 哈希值列表
    """
    if not hash_file_path or not os.path.exists(hash_file_path):
        return []

    hash_list = []
    try:
        with open(hash_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 简单处理，假设每行就是一个哈希值
                hash_list.append(line)
    except Exception as e:
        print(f"读取哈希文件时出错: {str(e)}")

    return hash_list


def load_already_cracked(hash_file_path, potfile_path):
    """
    加载已经破解的哈希结果

    Args:
        hash_file_path (str): 哈希文件路径
        potfile_path (str): potfile路径

    Returns:
        list: 破解结果列表，每个元素是一个字典 {'hash_val': hash, 'password': pwd, 'time_str': '', 'note': '从potfile中加载'}
    """
    if not hash_file_path or not potfile_path:
        return []

    # 读取哈希文件中的所有哈希
    hash_list = read_hash_file(hash_file_path)
    if not hash_list:
        return []

    # 解析potfile，获取哈希和密码的映射
    cracked_dict = parse_potfile(potfile_path, hash_list)
    if not cracked_dict:
        return []

    # 转换为结果列表
    results = []
    for hash_val, password in cracked_dict.items():
        results.append({
            'hash_val': hash_val,
            'password': password,
            'time_str': '',
            'note': '从potfile中加载'
        })

    return results
