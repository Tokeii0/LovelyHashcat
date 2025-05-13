#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
输出控制台 - 显示Hashcat输出的文本区域
"""

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor, QColor


class OutputConsole(QPlainTextEdit):
    """输出控制台控件，用于显示Hashcat的实时输出"""
    
    def __init__(self, parent=None, max_lines=5000):
        """
        初始化输出控制台
        
        Args:
            parent: 父窗口
            max_lines (int): 最大行数，超过后会清除旧的行
        """
        super().__init__(parent)
        self.max_lines = max_lines
        self.line_count = 0
        
        # 设置控件属性
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setMaximumBlockCount(max_lines)
        
        # 自定义颜色
        self.normal_color = QColor("#7D6B7D")  # 正常文本颜色
        self.error_color = QColor("#FF5C8A")   # 错误文本颜色
        self.success_color = QColor("#6CBAD9") # 成功文本颜色
        
        # 定时清理旧的文本，避免性能问题
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup_old_lines)
        self.cleanup_timer.start(30000)  # 每30秒检查一次
    
    def append_text(self, text, error=False, success=False):
        """
        添加文本到控制台
        
        Args:
            text (str): 要添加的文本
            error (bool): 是否为错误信息
            success (bool): 是否为成功信息
        """
        # 选择颜色
        if error:
            color = self.error_color
        elif success:
            color = self.success_color
        else:
            color = self.normal_color
        
        # 将光标移到末尾
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        
        # 格式化文本并插入
        html_text = f'<span style="color: {color.name()};">{text}</span>'
        self.appendHtml(html_text)
        
        # 滚动到最后
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
        # 更新行数
        self.line_count += text.count('\n')
        
        # 如果超过最大行数的80%，触发清理
        if self.line_count > self.max_lines * 0.8:
            self.cleanup_old_lines()
    
    def cleanup_old_lines(self):
        """清理旧行，保持在最大行数以内"""
        if self.line_count > self.max_lines:
            # 获取文档
            doc = self.document()
            
            # 如果文档块数超过最大行数的80%，清除旧的文本
            if doc.blockCount() > self.max_lines * 0.8:
                cursor = QTextCursor(doc)
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 
                                    doc.blockCount() - self.max_lines // 2)
                cursor.removeSelectedText()
                
                # 更新行数
                self.line_count = doc.blockCount()
    
    def clear_console(self):
        """清空控制台"""
        self.clear()
        self.line_count = 0
    
    def save_output(self, file_path):
        """
        将输出保存到文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            return True
        except Exception as e:
            print(f"保存输出失败: {str(e)}")
            return False
