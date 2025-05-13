#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口 - 应用程序的主界面
"""

import os
import json
from PySide6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, 
                              QWidget, QLabel, QComboBox, QPushButton, QGroupBox, 
                              QFormLayout, QGridLayout, QTabWidget, QMenuBar, QMenu, 
                              QStatusBar, QMessageBox, QFileDialog, QSpacerItem,
                              QSizePolicy, QFrame)
from PySide6.QtCore import Qt, QSize, QTimer, QDateTime, Slot, Signal, QPoint
from PySide6.QtGui import QIcon, QAction, QFont, QColor, QPalette

from hashcat_gui.gui.widgets.title_bar import TitleBar

from hashcat_gui.gui.style_loader import StyleLoader
from hashcat_gui.core.config_manager import ConfigManager
from hashcat_gui.core.hashcat_runner import HashcatRunner
from hashcat_gui.core.utils import (show_message, show_error, show_warning, 
                                   confirm, load_hash_modes, get_current_timestamp)
from hashcat_gui.gui.dialogs.settings_dialog import SettingsDialog
from hashcat_gui.gui.dialogs.about_dialog import AboutDialog
from hashcat_gui.gui.ui_components import UIComponents


class MainWindow(QMainWindow):
    """主窗口类，应用程序的主界面"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化Hashcat运行器
        self.hashcat_runner = HashcatRunner(self.config_manager)
        
        # 创建UI组件管理器
        self.ui_components = UIComponents(self)
        
        # 设置窗口属性 - 移除标题栏
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1000, 700)
        
        # 设置应用图标
        app_icon = QIcon(r"hashcat_gui\assets\icons\app.ico")
        self.setWindowIcon(app_icon)
        QApplication.setWindowIcon(app_icon)
        
        # 应用样式
        StyleLoader.apply_style()
        
        # 初始化UI
        self.init_ui()
        
        # 连接信号与槽
        self.connect_signals()
        
        # 加载哈希模式
        self.load_hash_modes()
        
        # 检查Hashcat路径
        self.check_hashcat_path()
    
    def init_ui(self):
        """初始化UI"""
        # 创建中心部件和主布局
        central_widget = QWidget()
        # 设置中心部件的样式
        central_widget.setStyleSheet(
            "QWidget { background-color: #FFF6F8; border-radius: 10px; }"
        )
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建自定义标题栏
        self.title_bar = TitleBar(self, "LovelyHashcat")
        main_layout.addWidget(self.title_bar)
        
        # 创建内容容器
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 初始化UI组件
        self.ui_components.init_components(content_layout)
        
        # 创建状态栏
        self.create_status_bar(content_layout)
        
        # 将内容容器添加到主布局
        main_layout.addWidget(content_container, 1)  # 1表示可伸缩
        
        # 连接自定义标题栏的信号
        self.title_bar.minimized.connect(self.showMinimized)
        self.title_bar.closed.connect(self.close)
        
        # 设置中心部件
        self.setCentralWidget(central_widget)
        
        # 设置窗口阴影（模拟边框）
        self.shadow_effect()
    
    def shadow_effect(self):
        """为窗口添加阴影效果"""
        # 创建一个Qt的阴影效果
        # 注意：PySide6中直接使用样式表来设置阴影会比较复杂
        # 这里我们通过在窗口底部添加边框来模拟阴影效果
        self.setStyleSheet(
            "QMainWindow { border: 1px solid #FFCCE5; }"
        )
    
    # 重写鼠标事件以支持拖动无边框窗口
    def mousePressEvent(self, event):
        """
        鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        # 标题栏区域的鼠标事件已经在TitleBar类中处理
        # 这里只处理其他区域的鼠标事件
        super().mousePressEvent(event)
    
    def create_menus(self):
        """创建菜单栏"""
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 打开哈希文件动作
        open_hash_action = QAction("打开哈希文件", self)
        open_hash_action.setShortcut("Ctrl+O")
        open_hash_action.triggered.connect(self.ui_components.open_hash_file)
        file_menu.addAction(open_hash_action)
        
        # 保存结果动作
        save_results_action = QAction("保存结果", self)
        save_results_action.setShortcut("Ctrl+S")
        save_results_action.triggered.connect(self.save_results)
        file_menu.addAction(save_results_action)
        
        file_menu.addSeparator()
        
        # 设置动作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menu_bar.addMenu("工具")
        
        # 显示Potfile动作
        show_pot_action = QAction("显示已破解的哈希", self)
        show_pot_action.triggered.connect(self.show_potfile)
        tools_menu.addAction(show_pot_action)
        
        # 显示剩余哈希动作
        show_left_action = QAction("显示未破解的哈希", self)
        show_left_action.triggered.connect(self.show_left_hashes)
        tools_menu.addAction(show_left_action)
        
        tools_menu.addSeparator()
        
        # 清空结果动作
        clear_results_action = QAction("清空结果", self)
        clear_results_action.triggered.connect(self.ui_components.clear_results)
        tools_menu.addAction(clear_results_action)
        
        tools_menu.addSeparator()
        
        # 查看设备信息动作
        device_info_action = QAction("查看设备信息", self)
        device_info_action.triggered.connect(self.get_device_info)
        tools_menu.addAction(device_info_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self, parent_layout):
        """创建状态栏
        
        Args:
            parent_layout: 父布局
        """
        # 创建状态栏容器
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        # 设置粉色背景和圆角
        status_container.setStyleSheet(
            "QWidget { background-color: #FFF0F5; border: 1px solid #FFE6EE; border-radius: 5px; }"
        )
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #7D6B7D;")
        status_layout.addWidget(self.status_label, 1)
        
        # 添加哈希路径标签
        self.hashcat_path_label = QLabel("")
        self.hashcat_path_label.setStyleSheet("color: #7D6B7D;")
        status_layout.addWidget(self.hashcat_path_label)
        
        # 将状态栏添加到父布局
        parent_layout.addWidget(status_container)
        
        # 更新Hashcat路径标签
        self.update_hashcat_path_label()
    
    def connect_signals(self):
        """连接信号与槽"""
        # 连接Hashcat运行器的信号
        self.hashcat_runner.output_ready.connect(self.ui_components.update_output)
        self.hashcat_runner.error_occurred.connect(self.handle_error)
        self.hashcat_runner.process_finished.connect(self.handle_process_finished)
        self.hashcat_runner.password_found.connect(self.ui_components.add_result)
        self.hashcat_runner.status_update.connect(self.update_status)
        
        # 连接UI组件的信号
        self.ui_components.start_button.clicked.connect(self.start_cracking)
        self.ui_components.stop_button.clicked.connect(self.stop_cracking)
        self.ui_components.attack_mode_combo.currentIndexChanged.connect(self.ui_components.update_attack_mode_panel)
        self.ui_components.hash_mode_combo.currentIndexChanged.connect(self.update_hash_mode_description)
    
    def load_hash_modes(self):
        """加载哈希模式列表"""
        # 获取哈希模式文件路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        hash_modes_path = os.path.join(base_dir, "data", "hash_modes.json")
        
        # 加载哈希模式
        hash_modes = load_hash_modes(hash_modes_path)
        
        # 更新哈希模式下拉框
        self.ui_components.update_hash_modes(hash_modes)
    
    def check_hashcat_path(self):
        """检查Hashcat路径是否有效"""
        hashcat_path = self.config_manager.get_hashcat_path()
        if not hashcat_path or not os.path.exists(hashcat_path):
            show_warning(
                self, 
                "Hashcat路径未设置", 
                "请在设置中配置Hashcat可执行文件的路径。"
            )
            self.open_settings()
    
    def update_hashcat_path_label(self):
        """更新状态栏中的Hashcat路径标签"""
        hashcat_path = self.config_manager.get_hashcat_path()
        if hashcat_path and os.path.exists(hashcat_path):
            self.hashcat_path_label.setText(f"Hashcat: {hashcat_path}")
        else:
            self.hashcat_path_label.setText("Hashcat: 未配置")
    
    def update_hash_mode_description(self):
        """更新哈希模式描述"""
        # 获取当前选择的哈希模式
        current_index = self.ui_components.hash_mode_combo.currentIndex()
        if current_index >= 0:
            hash_mode_id = self.ui_components.hash_mode_combo.itemData(current_index)
            hash_mode_name = self.ui_components.hash_mode_combo.currentText()
            self.status_label.setText(f"哈希类型: {hash_mode_id} - {hash_mode_name}")
    
    def update_status(self, status_info):
        """更新状态信息"""
        self.ui_components.update_status_info(status_info)
    
    def start_cracking(self):
        """开始破解过程"""
        # 检查Hashcat路径
        hashcat_path = self.config_manager.get_hashcat_path()
        if not hashcat_path or not os.path.exists(hashcat_path):
            show_error(self, "错误", "Hashcat可执行文件路径无效，请在设置中配置")
            self.open_settings()
            return
        
        # 获取参数
        params = self.ui_components.get_parameters()
        
        # 验证必需参数
        if not params.get('hash_file'):
            show_error(self, "错误", "请选择哈希文件")
            return
        
        if params.get('hash_mode') is None:
            show_error(self, "错误", "请选择哈希类型")
            return
        
        # 根据攻击模式验证参数
        attack_mode = params.get('attack_mode')
        if attack_mode == 0:  # 字典攻击
            if not params.get('dict_file'):
                show_error(self, "错误", "请选择字典文件")
                return
        elif attack_mode == 1:  # 组合攻击
            if not params.get('dict_file1') or not params.get('dict_file2'):
                show_error(self, "错误", "请选择两个字典文件")
                return
        elif attack_mode == 3:  # 掩码攻击
            if not params.get('mask'):
                show_error(self, "错误", "请输入掩码")
                return
        elif attack_mode == 6:  # 混合攻击(字典+掩码)
            if not params.get('dict_file') or not params.get('mask'):
                show_error(self, "错误", "请选择字典文件和输入掩码")
                return
        elif attack_mode == 7:  # 混合攻击(掩码+字典)
            if not params.get('dict_file') or not params.get('mask'):
                show_error(self, "错误", "请选择字典文件和输入掩码")
                return
        
        # 启动破解
        if self.hashcat_runner.start_cracking(params):
            self.status_label.setText("破解进行中...")
            self.ui_components.set_cracking_state(True)
        else:
            show_error(self, "错误", "启动Hashcat进程失败")
    
    def stop_cracking(self):
        """停止破解进程"""
        if self.hashcat_runner.stop_cracking():
            self.status_label.setText("破解已停止")
            self.ui_components.set_cracking_state(False)
    
    def show_potfile(self):
        """显示Potfile中的已破解哈希"""
        # 获取哈希文件
        hash_file = self.ui_components.hash_file_input.get_path()
        if not hash_file:
            show_error(self, "错误", "请先选择哈希文件")
            return
        
        # 获取potfile路径
        potfile_path = self.config_manager.get_potfile_path()
        
        # 显示potfile
        self.hashcat_runner.show_potfile(hash_file, potfile_path)
        self.status_label.setText("显示已破解的哈希...")
    
    def show_left_hashes(self):
        """显示未破解的哈希"""
        # 获取哈希文件
        hash_file = self.ui_components.hash_file_input.get_path()
        if not hash_file:
            show_error(self, "错误", "请先选择哈希文件")
            return
        
        # 获取potfile路径
        potfile_path = self.config_manager.get_potfile_path()
        
        # 显示未破解的哈希
        self.hashcat_runner.show_left_hashes(hash_file, potfile_path)
        self.status_label.setText("显示未破解的哈希...")
    
    def get_device_info(self):
        """获取设备信息"""
        self.hashcat_runner.get_device_info()
        self.status_label.setText("获取设备信息...")
    
    def save_results(self):
        """保存结果到文件"""
        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存结果",
            os.path.join(self.config_manager.get_work_dir(), "hashcat_results.txt"),
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            # 导出结果
            if self.ui_components.results_table.export_results(file_path):
                show_message(self, "成功", f"结果已保存到 {file_path}")
            else:
                show_error(self, "错误", "保存结果失败")
    
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 更新Hashcat路径
            self.hashcat_runner.update_hashcat_path()
            self.update_hashcat_path_label()
            
            # 应用主题
            theme = self.config_manager.get_theme()
            if theme == "pink":
                StyleLoader.apply_style("style.qss")
            elif theme == "dark":
                StyleLoader.apply_style("dark.qss")
            else:
                StyleLoader.apply_style("default.qss")
    
    def show_about(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def handle_error(self, error_message):
        """处理错误"""
        self.ui_components.update_output(error_message, error=True)
        self.status_label.setText("错误")
    
    def handle_process_finished(self, exit_code, exit_status):
        """处理进程结束"""
        if exit_code == 0:
            self.status_label.setText("破解完成")
        else:
            self.status_label.setText(f"破解终止，退出代码: {exit_code}")
        
        self.ui_components.set_cracking_state(False)
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 如果进程正在运行，询问是否确定退出
        if self.hashcat_runner.process and self.hashcat_runner.process.state() != 0:
            if not confirm(
                self,
                "确认退出",
                "Hashcat进程正在运行，确定要退出吗？"
            ):
                event.ignore()
                return
            
            # 停止进程
            self.hashcat_runner.stop_cracking()
        
        # 调用父类方法
        super().closeEvent(event)
