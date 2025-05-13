#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
关于对话框 - 显示应用程序相关信息
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                               QHBoxLayout, QTextBrowser)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

import hashcat_gui


class AboutDialog(QDialog):
    """关于对话框，显示应用程序信息"""
    
    def __init__(self, parent=None):
        """
        初始化关于对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置对话框属性
        self.setWindowTitle("关于 LovelyHashcat")
        self.setFixedSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 创建布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("LovelyHashcat")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # 版本
        version_label = QLabel(f"版本 {hashcat_gui.__version__}")
        version_label.setAlignment(Qt.AlignCenter)
        
        # 描述
        description = QTextBrowser()
        description.setOpenExternalLinks(True)
        description.setHtml("""
            <p align='center'>LovelyHashcat是一个用户友好的Hashcat图形界面，
            旨在简化Hashcat的使用过程，让密码破解工作更加高效和便捷。</p>
            <p align='center'>项目主页: 
            <a href='https://github.com/yourusername/lovelyhashcat'>GitHub</a></p>
            <p align='center'>Copyright &copy; 2025</p>
            <h3>功能特点</h3>
            <ul>
            <li>提供直观的图形界面来配置和运行Hashcat</li>
            <li>支持常用的Hashcat功能和参数</li>
            <li>实时显示破解进度和结果</li>
            <li>管理破解会话和结果</li>
            <li>支持多种攻击模式：字典攻击、掩码攻击、组合攻击等</li>
            </ul>
            <h3>使用说明</h3>
            <ol>
            <li>首次运行时，请在设置中配置Hashcat可执行文件的路径</li>
            <li>选择要破解的Hash文件</li>
            <li>选择Hash类型和攻击模式</li>
            <li>根据选择的攻击模式配置相应参数（如字典文件、规则、掩码等）</li>
            <li>点击"开始破解"按钮启动破解过程</li>
            <li>实时查看输出和结果</li>
            </ol>
            <p>LovelyHashcat仅供安全研究和学习之用。</p>
            """)
        
        # 关闭按钮
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        # 添加控件到布局
        layout.addSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addLayout(button_layout)
        
        # 设置布局边距
        layout.setContentsMargins(15, 15, 15, 15)
