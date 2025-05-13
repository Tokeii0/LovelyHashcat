#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
攻击模式面板 - 根据攻击模式动态显示不同的输入字段
"""

from PySide6.QtWidgets import (QWidget, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QGroupBox, QLineEdit, QPushButton)
from PySide6.QtCore import Signal

from hashcat_gui.gui.widgets.file_input_widget import FileInputWidget


class AttackModePanel(QWidget):
    """攻击模式面板，根据选择的攻击模式动态显示不同的输入字段"""
    
    # 定义信号
    config_changed = Signal()
    
    def __init__(self, parent=None):
        """初始化攻击模式面板"""
        super().__init__(parent)
        
        # 创建堆叠部件，用于切换不同的攻击模式面板
        self.stacked_widget = QStackedWidget()
        
        # 创建各种攻击模式的面板
        self.dict_panel = DictionaryAttackPanel()
        self.dict_panel.config_changed.connect(self.config_changed)
        
        self.combo_panel = CombinationAttackPanel()
        self.combo_panel.config_changed.connect(self.config_changed)
        
        self.mask_panel = MaskAttackPanel()
        self.mask_panel.config_changed.connect(self.config_changed)
        
        self.hybrid_dict_mask_panel = HybridDictMaskPanel()
        self.hybrid_dict_mask_panel.config_changed.connect(self.config_changed)
        
        self.hybrid_mask_dict_panel = HybridMaskDictPanel()
        self.hybrid_mask_dict_panel.config_changed.connect(self.config_changed)
        
        # 将面板添加到堆叠部件
        self.stacked_widget.addWidget(self.dict_panel)      # 索引 0: 字典攻击
        self.stacked_widget.addWidget(self.combo_panel)     # 索引 1: 组合攻击
        self.stacked_widget.addWidget(self.mask_panel)      # 索引 2: 掩码攻击
        self.stacked_widget.addWidget(self.hybrid_dict_mask_panel)  # 索引 3: 混合攻击(字典+掩码)
        self.stacked_widget.addWidget(self.hybrid_mask_dict_panel)  # 索引 4: 混合攻击(掩码+字典)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(0, 0, 0, 0)
    
    def set_attack_mode(self, mode):
        """
        设置当前攻击模式
        
        Args:
            mode (int): 攻击模式索引
                0: 字典攻击
                1: 组合攻击
                3: 掩码攻击
                6: 混合攻击(字典+掩码)
                7: 混合攻击(掩码+字典)
        """
        mode_map = {
            0: 0,  # 字典攻击
            1: 1,  # 组合攻击
            3: 2,  # 掩码攻击
            6: 3,  # 混合攻击(字典+掩码)
            7: 4   # 混合攻击(掩码+字典)
        }
        
        if mode in mode_map:
            self.stacked_widget.setCurrentIndex(mode_map[mode])
    
    def get_params(self):
        """
        获取当前攻击模式的参数
        
        Returns:
            dict: 参数字典
        """
        index = self.stacked_widget.currentIndex()
        panel = self.stacked_widget.widget(index)
        return panel.get_params()
    
    def clear(self):
        """清空所有面板的输入"""
        self.dict_panel.clear()
        self.combo_panel.clear()
        self.mask_panel.clear()
        self.hybrid_dict_mask_panel.clear()
        self.hybrid_mask_dict_panel.clear()


class DictionaryAttackPanel(QWidget):
    """字典攻击面板"""
    
    # 定义信号
    config_changed = Signal()
    
    def __init__(self, parent=None):
        """初始化字典攻击面板"""
        super().__init__(parent)
        
        # 创建布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建字典文件输入控件
        self.dict_file_input = FileInputWidget(
            self,
            dialog_title="选择字典文件",
            file_filter="字典文件 (*.txt *.dict *.lst);;所有文件 (*.*)",
            placeholder="选择字典文件"
        )
        
        # 创建规则文件输入控件
        self.rule_file_input = FileInputWidget(
            self,
            dialog_title="选择规则文件",
            file_filter="规则文件 (*.rule);;所有文件 (*.*)",
            placeholder="选择规则文件（可选）"
        )
        
        # 创建分组框
        group_box = QGroupBox("字典攻击配置")
        group_layout = QGridLayout()
        
        # 添加控件到布局
        group_layout.addWidget(QLabel("字典文件:"), 0, 0)
        group_layout.addWidget(self.dict_file_input, 0, 1)
        group_layout.addWidget(QLabel("规则文件:"), 1, 0)
        group_layout.addWidget(self.rule_file_input, 1, 1)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        
        # 添加分组框到主布局
        layout.addWidget(group_box)
        layout.addStretch(1)  # 添加弹性空间
        
        # 连接信号
        self.dict_file_input.path_changed.connect(self._on_config_changed)
        self.rule_file_input.path_changed.connect(self._on_config_changed)
    
    def _on_config_changed(self):
        """配置变化处理函数"""
        self.config_changed.emit()
    
    def get_params(self):
        """
        获取字典攻击参数
        
        Returns:
            dict: 参数字典
        """
        params = {
            'dict_file': self.dict_file_input.get_path(),
            'rule_file': self.rule_file_input.get_path()
        }
        return params
    
    def clear(self):
        """清空输入"""
        self.dict_file_input.clear()
        self.rule_file_input.clear()


class CombinationAttackPanel(QWidget):
    """组合攻击面板"""
    
    # 定义信号
    config_changed = Signal()
    
    def __init__(self, parent=None):
        """初始化组合攻击面板"""
        super().__init__(parent)
        
        # 创建布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建左字典文件输入控件
        self.dict_file1_input = FileInputWidget(
            self,
            dialog_title="选择左侧字典文件",
            file_filter="字典文件 (*.txt *.dict *.lst);;所有文件 (*.*)",
            placeholder="选择左侧字典文件"
        )
        
        # 创建右字典文件输入控件
        self.dict_file2_input = FileInputWidget(
            self,
            dialog_title="选择右侧字典文件",
            file_filter="字典文件 (*.txt *.dict *.lst);;所有文件 (*.*)",
            placeholder="选择右侧字典文件"
        )
        
        # 创建分组框
        group_box = QGroupBox("组合攻击配置")
        group_layout = QGridLayout()
        
        # 添加控件到布局
        group_layout.addWidget(QLabel("左侧字典:"), 0, 0)
        group_layout.addWidget(self.dict_file1_input, 0, 1)
        group_layout.addWidget(QLabel("右侧字典:"), 1, 0)
        group_layout.addWidget(self.dict_file2_input, 1, 1)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        
        # 添加分组框到主布局
        layout.addWidget(group_box)
        layout.addStretch(1)  # 添加弹性空间
        
        # 连接信号
        self.dict_file1_input.path_changed.connect(self._on_config_changed)
        self.dict_file2_input.path_changed.connect(self._on_config_changed)
    
    def _on_config_changed(self):
        """配置变化处理函数"""
        self.config_changed.emit()
    
    def get_params(self):
        """
        获取组合攻击参数
        
        Returns:
            dict: 参数字典
        """
        params = {
            'dict_file1': self.dict_file1_input.get_path(),
            'dict_file2': self.dict_file2_input.get_path()
        }
        return params
    
    def clear(self):
        """清空输入"""
        self.dict_file1_input.clear()
        self.dict_file2_input.clear()


class MaskAttackPanel(QWidget):
    """掩码攻击面板"""
    
    # 定义信号
    config_changed = Signal()
    
    def __init__(self, parent=None):
        """初始化掩码攻击面板"""
        super().__init__(parent)
        
        # 创建布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建分组框
        group_box = QGroupBox("掩码攻击配置")
        group_layout = QGridLayout()
        
        # 创建掩码输入框
        self.mask_edit = QLineEdit()
        self.mask_edit.setPlaceholderText("输入掩码，例如: ?l?l?l?l?l?l?l?l")
        
        # 添加掩码示例和说明
        self.mask_examples = QLabel(
            "常用字符集:\n"
            "?l = abcdefghijklmnopqrstuvwxyz\n"
            "?u = ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "?d = 0123456789\n"
            "?s = 特殊字符\n"
            "?a = ?l?u?d?s\n"
            "例如: ?d?d?d?d = 4位数字"
        )
        
        # 创建自定义字符集输入框
        self.charset1_edit = QLineEdit()
        self.charset1_edit.setPlaceholderText("自定义字符集1 (可选)")
        
        self.charset2_edit = QLineEdit()
        self.charset2_edit.setPlaceholderText("自定义字符集2 (可选)")
        
        self.charset3_edit = QLineEdit()
        self.charset3_edit.setPlaceholderText("自定义字符集3 (可选)")
        
        self.charset4_edit = QLineEdit()
        self.charset4_edit.setPlaceholderText("自定义字符集4 (可选)")
        
        # 添加控件到布局
        group_layout.addWidget(QLabel("掩码:"), 0, 0)
        group_layout.addWidget(self.mask_edit, 0, 1)
        group_layout.addWidget(QLabel("字符集1:"), 1, 0)
        group_layout.addWidget(self.charset1_edit, 1, 1)
        group_layout.addWidget(QLabel("字符集2:"), 2, 0)
        group_layout.addWidget(self.charset2_edit, 2, 1)
        group_layout.addWidget(QLabel("字符集3:"), 3, 0)
        group_layout.addWidget(self.charset3_edit, 3, 1)
        group_layout.addWidget(QLabel("字符集4:"), 4, 0)
        group_layout.addWidget(self.charset4_edit, 4, 1)
        group_layout.addWidget(self.mask_examples, 5, 0, 1, 2)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        
        # 添加分组框到主布局
        layout.addWidget(group_box)
        layout.addStretch(1)  # 添加弹性空间
        
        # 连接信号
        self.mask_edit.textChanged.connect(self._on_config_changed)
        self.charset1_edit.textChanged.connect(self._on_config_changed)
        self.charset2_edit.textChanged.connect(self._on_config_changed)
        self.charset3_edit.textChanged.connect(self._on_config_changed)
        self.charset4_edit.textChanged.connect(self._on_config_changed)
    
    def _on_config_changed(self):
        """配置变化处理函数"""
        self.config_changed.emit()
    
    def get_params(self):
        """
        获取掩码攻击参数
        
        Returns:
            dict: 参数字典
        """
        params = {
            'mask': self.mask_edit.text()
        }
        
        # 添加自定义字符集
        if self.charset1_edit.text():
            params['custom_charset1'] = self.charset1_edit.text()
        
        if self.charset2_edit.text():
            params['custom_charset2'] = self.charset2_edit.text()
        
        if self.charset3_edit.text():
            params['custom_charset3'] = self.charset3_edit.text()
        
        if self.charset4_edit.text():
            params['custom_charset4'] = self.charset4_edit.text()
        
        return params
    
    def clear(self):
        """清空输入"""
        self.mask_edit.clear()
        self.charset1_edit.clear()
        self.charset2_edit.clear()
        self.charset3_edit.clear()
        self.charset4_edit.clear()


class HybridDictMaskPanel(QWidget):
    """混合攻击面板(字典+掩码)"""
    
    # 定义信号
    config_changed = Signal()
    
    def __init__(self, parent=None):
        """初始化混合攻击面板(字典+掩码)"""
        super().__init__(parent)
        
        # 创建布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建分组框
        group_box = QGroupBox("混合攻击配置 (字典+掩码)")
        group_layout = QGridLayout()
        
        # 创建字典文件输入控件
        self.dict_file_input = FileInputWidget(
            self,
            dialog_title="选择字典文件",
            file_filter="字典文件 (*.txt *.dict *.lst);;所有文件 (*.*)",
            placeholder="选择字典文件"
        )
        
        # 创建掩码输入框
        self.mask_edit = QLineEdit()
        self.mask_edit.setPlaceholderText("输入掩码，例如: ?l?l?l?l")
        
        # 添加控件到布局
        group_layout.addWidget(QLabel("字典文件:"), 0, 0)
        group_layout.addWidget(self.dict_file_input, 0, 1)
        group_layout.addWidget(QLabel("掩码:"), 1, 0)
        group_layout.addWidget(self.mask_edit, 1, 1)
        
        # 添加说明
        explanation = QLabel("说明: 这种攻击模式将字典中的每个单词与掩码组合")
        group_layout.addWidget(explanation, 2, 0, 1, 2)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        
        # 添加分组框到主布局
        layout.addWidget(group_box)
        layout.addStretch(1)  # 添加弹性空间
        
        # 连接信号
        self.dict_file_input.path_changed.connect(self._on_config_changed)
        self.mask_edit.textChanged.connect(self._on_config_changed)
    
    def _on_config_changed(self):
        """配置变化处理函数"""
        self.config_changed.emit()
    
    def get_params(self):
        """
        获取混合攻击(字典+掩码)参数
        
        Returns:
            dict: 参数字典
        """
        params = {
            'dict_file': self.dict_file_input.get_path(),
            'mask': self.mask_edit.text()
        }
        return params
    
    def clear(self):
        """清空输入"""
        self.dict_file_input.clear()
        self.mask_edit.clear()


class HybridMaskDictPanel(QWidget):
    """混合攻击面板(掩码+字典)"""
    
    # 定义信号
    config_changed = Signal()
    
    def __init__(self, parent=None):
        """初始化混合攻击面板(掩码+字典)"""
        super().__init__(parent)
        
        # 创建布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建分组框
        group_box = QGroupBox("混合攻击配置 (掩码+字典)")
        group_layout = QGridLayout()
        
        # 创建掩码输入框
        self.mask_edit = QLineEdit()
        self.mask_edit.setPlaceholderText("输入掩码，例如: ?l?l?l?l")
        
        # 创建字典文件输入控件
        self.dict_file_input = FileInputWidget(
            self,
            dialog_title="选择字典文件",
            file_filter="字典文件 (*.txt *.dict *.lst);;所有文件 (*.*)",
            placeholder="选择字典文件"
        )
        
        # 添加控件到布局
        group_layout.addWidget(QLabel("掩码:"), 0, 0)
        group_layout.addWidget(self.mask_edit, 0, 1)
        group_layout.addWidget(QLabel("字典文件:"), 1, 0)
        group_layout.addWidget(self.dict_file_input, 1, 1)
        
        # 添加说明
        explanation = QLabel("说明: 这种攻击模式将掩码与字典中的每个单词组合")
        group_layout.addWidget(explanation, 2, 0, 1, 2)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        
        # 添加分组框到主布局
        layout.addWidget(group_box)
        layout.addStretch(1)  # 添加弹性空间
        
        # 连接信号
        self.mask_edit.textChanged.connect(self._on_config_changed)
        self.dict_file_input.path_changed.connect(self._on_config_changed)
    
    def _on_config_changed(self):
        """配置变化处理函数"""
        self.config_changed.emit()
    
    def get_params(self):
        """
        获取混合攻击(掩码+字典)参数
        
        Returns:
            dict: 参数字典
        """
        params = {
            'mask': self.mask_edit.text(),
            'dict_file': self.dict_file_input.get_path()
        }
        return params
    
    def clear(self):
        """清空输入"""
        self.mask_edit.clear()
        self.dict_file_input.clear()
