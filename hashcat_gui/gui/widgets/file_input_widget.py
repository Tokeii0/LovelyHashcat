#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件输入控件 - 带浏览按钮的文件路径输入控件
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Signal


class FileInputWidget(QWidget):
    """文件输入控件，包含一个输入框和一个浏览按钮"""
    
    # 定义信号
    path_changed = Signal(str)
    
    def __init__(self, parent=None, dialog_title="选择文件", file_filter="所有文件 (*.*)", 
                 is_save=False, is_dir=False, placeholder=""):
        """
        初始化文件输入控件
        
        Args:
            parent: 父窗口
            dialog_title (str): 文件对话框标题
            file_filter (str): 文件过滤器
            is_save (bool): 是否为保存对话框
            is_dir (bool): 是否选择目录
            placeholder (str): 输入框占位符文本
        """
        super().__init__(parent)
        
        self.dialog_title = dialog_title
        self.file_filter = file_filter
        self.is_save = is_save
        self.is_dir = is_dir
        
        # 创建布局
        self._init_ui()
        
        # 设置占位符
        if placeholder:
            self.path_edit.setPlaceholderText(placeholder)
    
    def _init_ui(self):
        """初始化UI"""
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建路径输入框
        self.path_edit = QLineEdit()
        self.path_edit.setMinimumWidth(250)
        
        # 创建浏览按钮
        self.browse_button = QPushButton("浏览...")
        self.browse_button.setMinimumWidth(60)
        
        # 添加控件到布局
        layout.addWidget(self.path_edit, 1)  # 路径输入框占据大部分空间
        layout.addWidget(self.browse_button, 0)  # 浏览按钮占据较少空间
        
        # 连接信号
        self.browse_button.clicked.connect(self._browse)
        self.path_edit.textChanged.connect(self._on_path_changed)
    
    def _browse(self):
        """打开文件对话框"""
        path = ""
        
        if self.is_dir:
            # 打开目录选择对话框
            path = QFileDialog.getExistingDirectory(
                self,
                self.dialog_title,
                self.get_path()
            )
        elif self.is_save:
            # 打开保存文件对话框
            path, _ = QFileDialog.getSaveFileName(
                self,
                self.dialog_title,
                self.get_path(),
                self.file_filter
            )
        else:
            # 打开打开文件对话框
            path, _ = QFileDialog.getOpenFileName(
                self,
                self.dialog_title,
                self.get_path(),
                self.file_filter
            )
        
        # 如果选择了文件/目录，更新路径
        if path:
            self.set_path(path)
    
    def _on_path_changed(self, path):
        """
        路径变更处理函数
        
        Args:
            path (str): 新路径
        """
        self.path_changed.emit(path)
    
    def get_path(self):
        """
        获取当前路径
        
        Returns:
            str: 当前路径
        """
        return self.path_edit.text()
    
    def set_path(self, path):
        """
        设置路径
        
        Args:
            path (str): 新路径
        """
        self.path_edit.setText(path)
    
    def clear(self):
        """清空路径"""
        self.path_edit.clear()
    
    def setEnabled(self, enabled):
        """
        设置控件是否启用
        
        Args:
            enabled (bool): 是否启用
        """
        super().setEnabled(enabled)
        self.path_edit.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
    
    def setPlaceholderText(self, text):
        """
        设置占位符文本
        
        Args:
            text (str): 占位符文本
        """
        self.path_edit.setPlaceholderText(text)
