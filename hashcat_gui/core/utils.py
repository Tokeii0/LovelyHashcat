#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实用工具函数 - 提供通用的工具函数
"""

import os
import json
import hashlib
import datetime
from PySide6.QtWidgets import QMessageBox


def show_message(parent, title, message, icon=QMessageBox.Information):
    """
    显示消息对话框
    
    Args:
        parent: 父窗口
        title (str): 标题
        message (str): 消息内容
        icon (QMessageBox.Icon): 图标类型
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.exec()


def show_error(parent, title, message):
    """
    显示错误消息
    
    Args:
        parent: 父窗口
        title (str): 标题
        message (str): 错误消息
    """
    show_message(parent, title, message, QMessageBox.Critical)


def show_warning(parent, title, message):
    """
    显示警告消息
    
    Args:
        parent: 父窗口
        title (str): 标题
        message (str): 警告消息
    """
    show_message(parent, title, message, QMessageBox.Warning)


def confirm(parent, title, message):
    """
    显示确认对话框
    
    Args:
        parent: 父窗口
        title (str): 标题
        message (str): 确认消息
        
    Returns:
        bool: 用户是否确认
    """
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes


def calculate_file_hash(file_path, algorithm='md5'):
    """
    计算文件哈希值
    
    Args:
        file_path (str): 文件路径
        algorithm (str): 哈希算法
        
    Returns:
        str: 哈希值，如果文件不存在则返回空字符串
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return ""
    
    hash_algorithm = None
    if algorithm.lower() == 'md5':
        hash_algorithm = hashlib.md5()
    elif algorithm.lower() == 'sha1':
        hash_algorithm = hashlib.sha1()
    elif algorithm.lower() == 'sha256':
        hash_algorithm = hashlib.sha256()
    else:
        return ""
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_algorithm.update(chunk)
        return hash_algorithm.hexdigest()
    except Exception:
        return ""


def load_hash_modes(file_path):
    """
    加载哈希模式列表
    
    Args:
        file_path (str): 哈希模式文件路径
        
    Returns:
        list: 哈希模式列表
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            hash_modes = json.load(f)
        return hash_modes
    except Exception:
        return []


def get_current_timestamp():
    """
    获取当前时间戳字符串
    
    Returns:
        str: 时间戳字符串，格式为 yyyy-mm-dd HH:MM:SS
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def ensure_dir_exists(directory):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory (str): 目录路径
        
    Returns:
        bool: 目录是否存在或成功创建
    """
    if not directory:
        return False
    
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception:
            return False
    
    return os.path.isdir(directory)
