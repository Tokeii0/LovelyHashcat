#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置对话框 - 用于配置应用程序设置
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QFormLayout, QSpinBox, QCheckBox, QComboBox)
from PySide6.QtCore import Qt

from hashcat_gui.gui.widgets.file_input_widget import FileInputWidget


class SettingsDialog(QDialog):
    """设置对话框，用于配置应用程序设置"""
    
    def __init__(self, config_manager, parent=None):
        """
        初始化设置对话框
        
        Args:
            config_manager: 配置管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        
        # 设置对话框属性
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # 创建布局
        self._init_ui()
        
        # 加载当前设置
        self._load_settings()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建Hashcat配置组
        hashcat_group = QGroupBox("Hashcat 配置")
        hashcat_layout = QFormLayout()
        
        # Hashcat路径
        self.hashcat_path_input = FileInputWidget(
            self,
            dialog_title="选择Hashcat可执行文件",
            file_filter="可执行文件 (*.exe);;所有文件 (*.*)",
            placeholder="Hashcat可执行文件路径"
        )
        hashcat_layout.addRow("Hashcat路径:", self.hashcat_path_input)
        
        # 默认工作目录
        self.work_dir_input = FileInputWidget(
            self,
            dialog_title="选择默认工作目录",
            is_dir=True,
            placeholder="默认工作目录"
        )
        hashcat_layout.addRow("工作目录:", self.work_dir_input)
        
        # Potfile路径
        self.potfile_path_input = FileInputWidget(
            self,
            dialog_title="选择Potfile文件",
            file_filter="Potfile (*.pot);;所有文件 (*.*)",
            placeholder="Potfile文件路径（可选）"
        )
        hashcat_layout.addRow("Potfile路径:", self.potfile_path_input)
        
        # 设置组的布局
        hashcat_group.setLayout(hashcat_layout)
        
        # 创建John the Ripper配置组
        john_group = QGroupBox("John the Ripper 配置")
        john_layout = QFormLayout()
        
        # John路径
        self.john_path_input = FileInputWidget(
            self,
            dialog_title="选择John the Ripper可执行文件",
            file_filter="可执行文件 (*.exe);;All Files (*.*)",
            placeholder="John the Ripper可执行文件路径"
        )
        john_layout.addRow("John路径:", self.john_path_input)
        
        # John配置文件路径
        self.john_config_path_input = FileInputWidget(
            self,
            dialog_title="选择John配置文件",
            file_filter="配置文件 (*.conf);;All Files (*.*)",
            placeholder="John配置文件路径（可选）"
        )
        john_layout.addRow("John配置文件:", self.john_config_path_input)
        
        # John pot文件路径
        self.john_pot_path_input = FileInputWidget(
            self,
            dialog_title="选择John pot文件",
            file_filter="Pot文件 (*.pot);;All Files (*.*)",
            placeholder="John pot文件路径（可选）"
        )
        john_layout.addRow("John pot文件:", self.john_pot_path_input)
        
        # John字典路径
        self.john_wordlist_path_input = FileInputWidget(
            self,
            dialog_title="选择John默认字典",
            file_filter="文本文件 (*.txt *.lst *.dict);;All Files (*.*)",
            placeholder="John默认字典路径（可选）"
        )
        john_layout.addRow("John字典:", self.john_wordlist_path_input)
        
        # John规则文件路径
        self.john_rules_path_input = FileInputWidget(
            self,
            dialog_title="选择John规则文件",
            file_filter="规则文件 (*.rules *.rule);;All Files (*.*)",
            placeholder="John规则文件路径（可选）"
        )
        john_layout.addRow("John规则文件:", self.john_rules_path_input)
        
        # 设置John组的布局
        john_group.setLayout(john_layout)
        
        # 创建界面配置组
        ui_group = QGroupBox("界面配置")
        ui_layout = QFormLayout()
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("默认主题", "default")
        self.theme_combo.addItem("少女粉主题", "pink")
        self.theme_combo.addItem("深色主题", "dark")
        ui_layout.addRow("界面主题:", self.theme_combo)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 18)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" pt")
        ui_layout.addRow("字体大小:", self.font_size_spin)
        
        # 保存输出
        self.save_output_check = QCheckBox("保存输出到文件")
        ui_layout.addRow("", self.save_output_check)
        
        # 输出保存目录
        self.output_dir_input = FileInputWidget(
            self,
            dialog_title="选择输出保存目录",
            is_dir=True,
            placeholder="输出保存目录"
        )
        ui_layout.addRow("输出保存目录:", self.output_dir_input)
        
        # 设置组的布局
        ui_group.setLayout(ui_layout)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 添加按钮
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        self.reset_button = QPushButton("重置为默认")
        
        # 添加按钮到布局
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加组到主布局
        main_layout.addWidget(hashcat_group)
        main_layout.addWidget(john_group)
        main_layout.addWidget(ui_group)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 连接信号
        self.save_button.clicked.connect(self._save_settings)
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button.clicked.connect(self._reset_settings)
        self.save_output_check.toggled.connect(self._toggle_output_dir)
    
    def _toggle_output_dir(self, checked):
        """启用或禁用输出目录选择"""
        self.output_dir_input.setEnabled(checked)
    
    def _load_settings(self):
        """加载当前设置"""
        # 加载Hashcat配置
        self.hashcat_path_input.set_path(self.config_manager.get_hashcat_path())
        self.work_dir_input.set_path(self.config_manager.get_work_dir())
        self.potfile_path_input.set_path(self.config_manager.get_potfile_path())
        
        # 加载John the Ripper配置
        self.john_path_input.set_path(self.config_manager.get_john_path())
        self.john_config_path_input.set_path(self.config_manager.get_john_config_path())
        self.john_pot_path_input.set_path(self.config_manager.get_john_pot_path())
        self.john_wordlist_path_input.set_path(self.config_manager.get_john_wordlist_path())
        self.john_rules_path_input.set_path(self.config_manager.get_john_rules_path())
        
        # 加载界面配置
        theme = self.config_manager.get_theme()
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.font_size_spin.setValue(self.config_manager.get_font_size())
        
        save_output = self.config_manager.get_save_output()
        self.save_output_check.setChecked(save_output)
        
        self.output_dir_input.set_path(self.config_manager.get_output_dir())
        self.output_dir_input.setEnabled(save_output)
    
    def _save_settings(self):
        """保存设置"""
        # 保存Hashcat配置
        self.config_manager.set_hashcat_path(self.hashcat_path_input.get_path())
        self.config_manager.set_work_dir(self.work_dir_input.get_path())
        self.config_manager.set_potfile_path(self.potfile_path_input.get_path())
        
        # 保存John the Ripper配置
        self.config_manager.set_john_path(self.john_path_input.get_path())
        self.config_manager.set_john_config_path(self.john_config_path_input.get_path())
        self.config_manager.set_john_pot_path(self.john_pot_path_input.get_path())
        self.config_manager.set_john_wordlist_path(self.john_wordlist_path_input.get_path())
        self.config_manager.set_john_rules_path(self.john_rules_path_input.get_path())
        
        # 保存界面配置
        self.config_manager.set_theme(self.theme_combo.currentData())
        self.config_manager.set_font_size(self.font_size_spin.value())
        self.config_manager.set_save_output(self.save_output_check.isChecked())
        self.config_manager.set_output_dir(self.output_dir_input.get_path())
        
        # 接受对话框
        self.accept()
    
    def _reset_settings(self):
        """重置为默认设置"""
        # 重置配置
        self.config_manager.reset_to_default()
        
        # 重新加载设置
        self._load_settings()
