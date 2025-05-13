#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
样式加载器 - 用于管理和加载应用程序样式
"""

import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream


class StyleLoader:
    """样式加载器类，用于加载和应用QSS样式"""
    
    @staticmethod
    def load_style(style_name="style.qss"):
        """
        加载指定的QSS样式文件
        
        Args:
            style_name (str): 样式文件名称，默认为style.qss
            
        Returns:
            str: 样式表内容
        """
        # 获取样式文件的绝对路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        style_path = os.path.join(base_dir, "assets", style_name)
        
        # 如果文件不存在，返回空字符串
        if not os.path.exists(style_path):
            print(f"警告: 样式文件 {style_path} 不存在")
            return ""
        
        # 读取样式表内容
        qss_file = QFile(style_path)
        if qss_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(qss_file)
            style = stream.readAll()
            qss_file.close()
            return style
        
        return ""
    
    @staticmethod
    def apply_style(style_name="style.qss"):
        """
        应用指定的QSS样式到整个应用程序
        
        Args:
            style_name (str): 样式文件名称，默认为style.qss
            
        Returns:
            bool: 是否成功应用样式
        """
        style = StyleLoader.load_style(style_name)
        if style:
            QApplication.instance().setStyleSheet(style)
            return True
        return False
