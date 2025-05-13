#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
结果表格 - 显示破解结果的表格控件
"""

from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                               QAbstractItemView, QMenu, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor


class ResultsTable(QTableWidget):
    """结果表格控件，用于显示破解成功的哈希和密码"""
    
    # 定义信号
    item_copied = Signal(str)
    
    def __init__(self, parent=None):
        """初始化结果表格"""
        super().__init__(parent)
        
        # 设置表格属性
        self._init_ui()
        
        # 连接信号
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _init_ui(self):
        """初始化UI"""
        # 设置列数和表头
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["哈希值", "密码", "时间", "备注"])
        
        # 设置列宽
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 哈希值列自适应宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 密码列自适应宽度
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 时间列根据内容调整宽度
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 备注列根据内容调整宽度
        
        # 设置表格属性
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 不可编辑
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选择整行
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 单选
        self.setAlternatingRowColors(True)  # 交替行颜色
        self.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用自定义上下文菜单
        self.setSortingEnabled(True)  # 启用排序
        
        # 设置垂直表头不可见
        self.verticalHeader().setVisible(False)
    
    def add_result(self, hash_val, password, time_str="", note=""):
        """
        添加破解结果
        
        Args:
            hash_val (str): 哈希值
            password (str): 破解得到的密码
            time_str (str): 破解时间
            note (str): 备注
        """
        # 检查是否已存在相同的哈希值
        for row in range(self.rowCount()):
            if self.item(row, 0) and self.item(row, 0).text() == hash_val:
                # 更新现有行
                self.item(row, 1).setText(password)
                self.item(row, 2).setText(time_str)
                self.item(row, 3).setText(note)
                
                # 设置行颜色为粉色，表示更新
                for col in range(self.columnCount()):
                    if self.item(row, col):
                        self.item(row, col).setBackground(QColor("#FFCCE5"))
                return
        
        # 添加新行
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        # 创建并设置单元格项
        hash_item = QTableWidgetItem(hash_val)
        password_item = QTableWidgetItem(password)
        time_item = QTableWidgetItem(time_str)
        note_item = QTableWidgetItem(note)
        
        # 设置单元格项
        self.setItem(row_position, 0, hash_item)
        self.setItem(row_position, 1, password_item)
        self.setItem(row_position, 2, time_item)
        self.setItem(row_position, 3, note_item)
        
        # 设置新行的背景颜色为浅蓝色，表示新添加
        for col in range(self.columnCount()):
            if self.item(row_position, col):
                self.item(row_position, col).setBackground(QColor("#D6EEFF"))
        
        # 滚动到新行
        self.scrollToItem(hash_item)
    
    def add_results(self, results):
        """
        批量添加破解结果
        
        Args:
            results (list): 结果列表，每个元素是一个字典，包含hash_val, password, time_str, note
        """
        for result in results:
            self.add_result(
                result.get('hash_val', ''),
                result.get('password', ''),
                result.get('time_str', ''),
                result.get('note', '')
            )
    
    def clear_results(self):
        """清空所有结果"""
        self.setRowCount(0)
    
    def export_results(self, file_path, delimiter=":"):
        """
        导出结果到文件
        
        Args:
            file_path (str): 文件路径
            delimiter (str): 分隔符，默认为冒号
            
        Returns:
            bool: 是否成功导出
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for row in range(self.rowCount()):
                    hash_val = self.item(row, 0).text() if self.item(row, 0) else ''
                    password = self.item(row, 1).text() if self.item(row, 1) else ''
                    f.write(f"{hash_val}{delimiter}{password}\n")
            return True
        except Exception as e:
            print(f"导出结果失败: {str(e)}")
            return False
    
    def _show_context_menu(self, position):
        """
        显示上下文菜单
        
        Args:
            position: 菜单显示位置
        """
        menu = QMenu(self)
        
        # 仅当选择了一行时才显示菜单
        if self.selectedItems():
            # 获取选中行
            row = self.selectedItems()[0].row()
            
            # 添加复制选项
            copy_hash_action = QAction("复制哈希值", self)
            copy_hash_action.triggered.connect(lambda: self._copy_cell_text(row, 0))
            menu.addAction(copy_hash_action)
            
            copy_password_action = QAction("复制密码", self)
            copy_password_action.triggered.connect(lambda: self._copy_cell_text(row, 1))
            menu.addAction(copy_password_action)
            
            copy_line_action = QAction("复制整行", self)
            copy_line_action.triggered.connect(lambda: self._copy_row(row))
            menu.addAction(copy_line_action)
            
            menu.addSeparator()
            
            # 添加删除选项
            delete_action = QAction("删除此行", self)
            delete_action.triggered.connect(lambda: self.removeRow(row))
            menu.addAction(delete_action)
            
            # 显示菜单
            menu.exec_(self.viewport().mapToGlobal(position))
    
    def _copy_cell_text(self, row, col):
        """
        复制单元格文本到剪贴板
        
        Args:
            row (int): 行索引
            col (int): 列索引
        """
        if self.item(row, col):
            text = self.item(row, col).text()
            QApplication.clipboard().setText(text)
            self.item_copied.emit(text)
    
    def _copy_row(self, row):
        """
        复制整行文本到剪贴板
        
        Args:
            row (int): 行索引
        """
        texts = []
        for col in range(self.columnCount()):
            if self.item(row, col):
                texts.append(self.item(row, col).text())
        
        row_text = "\t".join(texts)
        QApplication.clipboard().setText(row_text)
        self.item_copied.emit(row_text)
