#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可搜索的结果表格组件
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QLabel, QPushButton, QTableWidget, QHeaderView,
                              QAbstractItemView, QTableWidgetItem)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon

from hashcat_gui.gui.widgets.results_table import ResultsTable


class SearchableResultsTable(QWidget):
    """可搜索的结果表格组件，包含搜索框和结果表格"""
    
    def __init__(self, parent=None):
        """初始化可搜索的结果表格组件"""
        super().__init__(parent)
        
        # 创建布局
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建搜索区域
        search_layout = QHBoxLayout()
        
        # 创建搜索标签
        search_label = QLabel("搜索:")
        search_layout.addWidget(search_label)
        
        # 创建搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索哈希值或密码...")
        self.search_input.setClearButtonEnabled(True)  # 添加清除按钮
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #FFC0CB;
                border-radius: 6px;
                padding: 3px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #FF69B4;
            }
        """)
        search_layout.addWidget(self.search_input, 1)  # 搜索框占据大部分空间
        
        # 添加搜索区域到主布局
        main_layout.addLayout(search_layout)
        
        # 创建结果表格
        self.results_table = ResultsTable(self)
        main_layout.addWidget(self.results_table, 1)  # 表格占据剩余所有空间
    
    def _connect_signals(self):
        """连接信号"""
        # 搜索框文本变化时触发搜索
        self.search_input.textChanged.connect(self._filter_results)
    
    def _filter_results(self, search_text):
        """
        根据搜索文本过滤结果
        
        Args:
            search_text (str): 搜索文本
        """
        search_text = search_text.lower()
        
        # 遍历所有行
        for row in range(self.results_table.rowCount()):
            # 默认隐藏行
            self.results_table.setRowHidden(row, True)
            
            # 如果搜索文本为空，显示所有行
            if not search_text:
                self.results_table.setRowHidden(row, False)
                continue
            
            # 获取当前行的哈希值和密码
            hash_item = self.results_table.item(row, 0)
            pwd_item = self.results_table.item(row, 1)
            note_item = self.results_table.item(row, 3)
            
            # 如果哈希值或密码或备注中包含搜索文本，显示该行
            if hash_item and search_text in hash_item.text().lower():
                self.results_table.setRowHidden(row, False)
            elif pwd_item and search_text in pwd_item.text().lower():
                self.results_table.setRowHidden(row, False)
            elif note_item and search_text in note_item.text().lower():
                self.results_table.setRowHidden(row, False)
    
    def add_result(self, hash_val, password, time_str="", note=""):
        """
        添加破解结果
        
        Args:
            hash_val (str): 哈希值
            password (str): 破解得到的密码
            time_str (str): 破解时间
            note (str): 备注
        """
        self.results_table.add_result(hash_val, password, time_str, note)
        
        # 如果有搜索文本，重新过滤结果
        if self.search_input.text():
            self._filter_results(self.search_input.text())
    
    def add_results(self, results):
        """
        批量添加破解结果
        
        Args:
            results (list): 结果列表，每个元素是一个字典，包含hash_val, password, time_str, note
        """
        self.results_table.add_results(results)
        
        # 如果有搜索文本，重新过滤结果
        if self.search_input.text():
            self._filter_results(self.search_input.text())
    
    def clear_results(self):
        """清空所有结果"""
        self.results_table.clear_results()
        
        # 清空搜索框
        self.search_input.clear()
    
    def export_results(self, file_path, delimiter=":"):
        """
        导出结果到文件
        
        Args:
            file_path (str): 文件路径
            delimiter (str): 分隔符，默认为冒号
            
        Returns:
            bool: 是否成功导出
        """
        return self.results_table.export_results(file_path, delimiter)
