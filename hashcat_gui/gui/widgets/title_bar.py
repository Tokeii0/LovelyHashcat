#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定义标题栏 - 少女风格的自定义标题栏
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, 
                             QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, Signal, QPoint, QRectF
from PySide6.QtGui import QFont, QColor, QPainter, QPainterPath, QMouseEvent, QPixmap


class TitleBar(QWidget):
    """自定义标题栏控件，包含标题和最小化、关闭按钮"""
    
    # 定义信号
    minimized = Signal()
    closed = Signal()
    
    def __init__(self, parent=None, title=""):
        """
        初始化自定义标题栏
        
        Args:
            parent: 父窗口
            title (str): 窗口标题
        """
        super().__init__(parent)
        
        # 设置标题
        self.title = title
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 鼠标按下位置
        self.mouse_pressed = False
        self.mouse_pressed_pos = None
        
        # 按钮区域
        self.close_btn_rect = QRectF()
        self.min_btn_rect = QRectF()
        
        # 鼠标悬停状态
        self.close_btn_hover = False
        self.min_btn_hover = False
        
        # 创建UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 设置固定高度
        self.setFixedHeight(28)
        
        # 设置透明背景
        self.setStyleSheet("background-color: transparent;")
        
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)  # 增加空间以使图标和文字分开
        
        # 添加应用图标
        self.app_icon = QLabel()
        pixmap = QPixmap("D:/AI/lovelyhashcat/hashcat_gui/assets/icons/app_24.png")
        self.app_icon.setPixmap(pixmap)
        self.app_icon.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.app_icon)
        
        # 创建标题标签 - 简约样式
        self.title_label = QLabel(self.title)
        font = QFont()
        font.setPointSize(9)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("color: #666666;")
        
        # 添加控件到主布局
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        # 确保可以接收鼠标事件
        self.setMouseTracking(True)
        
        # 设置最小宽度
        self.setMinimumWidth(100)
    
    def set_title(self, title):
        """
        设置标题
        
        Args:
            title (str): 新标题
        """
        self.title = title
        self.title_label.setText(title)
    
    def mousePressEvent(self, event: QMouseEvent):
        """
        鼠标按下事件，用于支持拖动窗口和按钮点击
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            # 检查是否点击了关闭按钮
            if self.close_btn_rect.contains(event.position()):
                self.closed.emit()
                event.accept()
                return
            
            # 检查是否点击了最小化按钮
            if self.min_btn_rect.contains(event.position()):
                self.minimized.emit()
                event.accept()
                return
            
            # 否则是拖动窗口
            self.mouse_pressed = True
            self.mouse_pressed_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
        
        event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        self.mouse_pressed = False
        event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        鼠标移动事件，用于支持拖动窗口和按钮悬停效果
        
        Args:
            event: 鼠标事件
        """
        # 更新按钮悬停状态
        old_close_hover = self.close_btn_hover
        old_min_hover = self.min_btn_hover
        
        self.close_btn_hover = self.close_btn_rect.contains(event.position())
        self.min_btn_hover = self.min_btn_rect.contains(event.position())
        
        # 如果悬停状态改变，重绘
        if old_close_hover != self.close_btn_hover or old_min_hover != self.min_btn_hover:
            self.update()
        
        # 处理拖动
        if self.mouse_pressed and event.buttons() == Qt.LeftButton:
            # 移动整个窗口
            self.window().move(event.globalPosition().toPoint() - self.mouse_pressed_pos)
            
        event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """
        鼠标双击事件，用于最大化/还原窗口
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            # 如果父窗口支持最大化，则切换最大化状态
            if self.parent().isMaximized():
                self.parent().showNormal()
            else:
                self.parent().showMaximized()
            event.accept()
    
    def resizeEvent(self, event):
        """
        大小改变事件，用于更新按钮位置
        
        Args:
            event: 大小改变事件
        """
        super().resizeEvent(event)
        # 更新按钮位置
        self._updateButtonGeometry()
    
    def _updateButtonGeometry(self):
        """
        更新按钮几何位置
        """
        # 按钮尺寸
        btn_size = 12
        btn_margin = 8
        btn_top = (self.height() - btn_size) // 2
        
        # 红色关闭按钮位置在最右边
        close_left = self.width() - btn_size - 10  # 10是右边距
        self.close_btn_rect = QRectF(close_left, btn_top, btn_size, btn_size)
        
        # 黄色最小化按钮位置在关闭按钮左侧
        min_left = close_left - btn_size - btn_margin
        self.min_btn_rect = QRectF(min_left, btn_top, btn_size, btn_size)
    
    def paintEvent(self, event):
        """
        绘制事件，用于绘制自定义外观
        
        Args:
            event: 绘制事件
        """
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 绘制最小化按钮（黄色圆形）
        if self.min_btn_hover:
            painter.setBrush(QColor('#FFD700'))  # 悬停时更亮的黄色
        else:
            painter.setBrush(QColor('#FFCC00'))  # 默认黄色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.min_btn_rect)
        
        # 绘制关闭按钮（红色圆形）
        if self.close_btn_hover:
            painter.setBrush(QColor('#FF3B30'))  # 悬停时更深的红色
        else:
            painter.setBrush(QColor('#FF5F57'))  # 默认红色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.close_btn_rect)
