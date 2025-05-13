#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI组件 - 主窗口的UI组件集合
"""

import os
from datetime import datetime
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, 
                              QGroupBox, QFormLayout, QGridLayout, QTabWidget, QFileDialog,
                              QSpacerItem, QSizePolicy, QProgressBar, QStackedWidget, QWidget,
                              QPlainTextEdit,QRadioButton,QLineEdit)
from PySide6.QtCore import Qt, QDateTime, Slot
from PySide6.QtGui import QFont

from hashcat_gui.gui.widgets.file_input_widget import FileInputWidget
from hashcat_gui.gui.widgets.attack_mode_panel import AttackModePanel
from hashcat_gui.gui.widgets.output_console import OutputConsole
from hashcat_gui.gui.widgets.results_table import ResultsTable
from hashcat_gui.gui.widgets.searchable_results_table import SearchableResultsTable
from hashcat_gui.core.potfile_parser import load_already_cracked


class UIComponents:
    """UI组件管理类，负责创建和管理主窗口的UI组件"""
    
    def __init__(self, main_window):
        """
        初始化UI组件
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.config_manager = main_window.config_manager
    
    def init_components(self, main_layout):
        """
        初始化UI组件
        
        Args:
            main_layout: 主布局
        """
        # 创建水平布局作为主要内容布局
        content_layout = QHBoxLayout()
        
        # 创建左右两侧的布局
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # 左侧布局
        self.create_control_area(left_layout)      # 控制区域
        self.create_core_config_area(left_layout)  # 核心配置区域
        self.create_advanced_options_area(left_layout)  # 高级选项区域
        
        # 右侧布局
        self.create_john_tools_area(right_layout)    # John哈希转换工具区域
        self.create_attack_mode_area(right_layout)  # 攻击模式配置区域
        
        # 添加弹性空间
        left_layout.addStretch(1)
        right_layout.addStretch(1)
        
        # 将左右布局添加到水平布局
        content_layout.addLayout(left_layout, 2)  # 左侧占比2
        content_layout.addLayout(right_layout, 1) # 右侧占比1
        
        # 将水平布局添加到主布局
        main_layout.addLayout(content_layout)
        
        # 创建输出和结果区（底部）
        self.create_output_results_area(main_layout)
    
    def create_core_config_area(self, parent_layout):
        """
        创建核心配置区
        
        Args:
            parent_layout: 父布局
        """
        # 创建分组框
        group_box = QGroupBox("核心配置")
        group_layout = QFormLayout()
        
        # 创建哈希输入方式选择
        input_method_group = QGroupBox("哈希输入方式")
        input_method_layout = QHBoxLayout()
        
        # 添加单选按钮
        self.file_radio = QRadioButton("从文件读取")
        self.text_radio = QRadioButton("直接输入")
        self.file_radio.setChecked(True)  # 默认选中文件模式
        
        # 连接信号
        self.file_radio.toggled.connect(self._update_hash_input_state)
        self.text_radio.toggled.connect(self._update_hash_input_state)
        
        # 添加到布局
        input_method_layout.addWidget(self.file_radio)
        input_method_layout.addWidget(self.text_radio)
        input_method_layout.addStretch(1)
        input_method_group.setLayout(input_method_layout)
        group_layout.addRow(input_method_group)
        
        # 哈希文件选择
        file_input_container = QWidget()
        file_input_layout = QVBoxLayout(file_input_container)
        file_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.hash_file_input = FileInputWidget(
            self.main_window, 
            dialog_title="选择哈希文件",
            file_filter="哈希文件 (*.txt *.hash *.lst *.hashes);;所有文件 (*.*)",
            placeholder="选择包含哈希值的文件"
        )
        self.hash_file_input.path_changed.connect(self._on_hash_file_changed)
        file_input_layout.addWidget(self.hash_file_input)
        
        # 添加到主布局
        group_layout.addRow("哈希文件:", file_input_container)
        
        # 添加文本输入部分
        text_input_container = QWidget()
        text_input_layout = QVBoxLayout(text_input_container)
        text_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.hash_text_input = QPlainTextEdit()
        self.hash_text_input.setPlaceholderText("在此处粘贴哈希值，每行一个")
        self.hash_text_input.setMinimumHeight(40)  # 减小高度，大约2行文字
        self.hash_text_input.setMaximumHeight(60)  # 设置最大高度
        self.hash_text_input.setFixedHeight(45)    # 固定高度
        self.hash_text_input.setStyleSheet(
            "QPlainTextEdit {"
            "    background-color: #FFFFFF;"
            "    border: 1px solid #FFC0CB;"
            "    border-radius: 6px;"
            "    padding: 3px;"
            "}"
        )
        text_input_layout.addWidget(self.hash_text_input)
        
        # 添加到主布局
        group_layout.addRow("直接输入:", text_input_container)
        
        # 初始化状态
        self._update_hash_input_state()
        
        # 哈希类型搜索和选择
        hash_type_container = QWidget()
        hash_type_layout = QVBoxLayout(hash_type_container)
        hash_type_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建搜索框
        self.hash_mode_search = QLineEdit()
        self.hash_mode_search.setPlaceholderText("搜索哈希类型...") 
        self.hash_mode_search.textChanged.connect(self._filter_hash_modes)
        hash_type_layout.addWidget(self.hash_mode_search)
        
        # 创建哈希类型下拉框
        self.hash_mode_combo = QComboBox()
        self.hash_mode_combo.setMaxVisibleItems(15)  # 设置最大可见项数
        self.hash_mode_combo.setStyleSheet("QComboBox { min-height: 22px; }")
        hash_type_layout.addWidget(self.hash_mode_combo)
        
        group_layout.addRow("哈希类型:", hash_type_container)
        
        # 存储原始哈希模式列表，用于过滤
        self.all_hash_modes = []
        self.hash_mode_combo.setEditable(True)
        self.hash_mode_combo.setInsertPolicy(QComboBox.NoInsert)
        self.hash_mode_combo.lineEdit().setPlaceholderText("选择或搜索哈希类型")
        
        # 攻击模式选择已移动到攻击模式配置区
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        parent_layout.addWidget(group_box)
    
    def create_attack_mode_area(self, parent_layout):
        """
        创建攻击模式特定配置区
        
        Args:
            parent_layout: 父布局
        """
        # 创建攻击模式选择分组框
        mode_select_box = QGroupBox("攻击模式选择")
        mode_select_layout = QVBoxLayout()
        
        # 创建攻击模式选择下拉框
        self.attack_mode_combo = QComboBox()
        self.attack_mode_combo.addItem("字典攻击 (Wordlist)", 0)
        self.attack_mode_combo.addItem("组合攻击 (Combination)", 1)
        self.attack_mode_combo.addItem("掌码攻击 (Brute-Force)", 3)
        self.attack_mode_combo.addItem("混合攻击 (字典+掌码)", 6)
        self.attack_mode_combo.addItem("混合攻击 (掌码+字典)", 7)
        
        # 将攻击模式选择添加到布局
        mode_select_layout.addWidget(self.attack_mode_combo)
        mode_select_box.setLayout(mode_select_layout)
        
        # 添加攻击模式选择分组框到父布局
        parent_layout.addWidget(mode_select_box)
        
        # 创建攻击模式面板
        self.attack_mode_panel = AttackModePanel(self.main_window)
        
        # 创建分组框
        group_box = QGroupBox("攻击模式配置")
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.attack_mode_panel)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        parent_layout.addWidget(group_box)
        
        # 设置初始攻击模式
        self.update_attack_mode_panel(self.attack_mode_combo.currentIndex())
        
        # 连接攻击模式变化信号
        self.attack_mode_combo.currentIndexChanged.connect(self.update_attack_mode_panel)
    
    def create_control_area(self, parent_layout):
        """
        创建控制区
        
        Args:
            parent_layout: 父布局
        """
        # 创建分组框
        group_box = QGroupBox("控制")
        group_layout = QVBoxLayout()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 开始破解按钮
        self.start_button = QPushButton("开始破解")
        self.start_button.setMinimumHeight(40)
        # 设置少女风格的粉色按钮
        self.start_button.setStyleSheet(
            "QPushButton { background-color: #FFCCE5; color: #7D6B7D; }"
            "QPushButton:hover { background-color: #FFD9EC; }"
            "QPushButton:pressed { background-color: #FFC0CB; }"
        )
        button_layout.addWidget(self.start_button)
        
        # 停止破解按钮
        self.stop_button = QPushButton("停止破解")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        # 设置少女风格的粉色按钮
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #FFCCE5; color: #7D6B7D; }"
            "QPushButton:hover { background-color: #FFD9EC; }"
            "QPushButton:pressed { background-color: #FFC0CB; }"
            "QPushButton:disabled { background-color: #F2F2F2; color: #AAAAAA; }"
        )
        button_layout.addWidget(self.stop_button)
        
        # 添加按钮布局到分组框布局
        group_layout.addLayout(button_layout)
        
        # 创建状态信息布局
        status_layout = QFormLayout()
        
        # 状态标签
        self.status_value_label = QLabel("就绪")
        status_layout.addRow("状态:", self.status_value_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        # 设置少女风格的进度条
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #FFC0CB; border-radius: 7px; text-align: center; background-color: #FFFFFF; }"
            "QProgressBar::chunk { background-color: #FFCCE5; border-radius: 6px; }"
        )
        status_layout.addRow("进度:", self.progress_bar)
        
        # 速度和恢复比例显示（同一行）
        speed_recovered_container = QWidget()
        speed_recovered_layout = QHBoxLayout(speed_recovered_container)
        speed_recovered_layout.setContentsMargins(0, 0, 0, 0)
        
        # 速度部分
        speed_layout = QHBoxLayout()
        speed_label_title = QLabel("速度:")
        self.speed_label = QLabel("0 H/s")
        speed_layout.addWidget(speed_label_title)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addStretch(1)
        
        # 已恢复部分
        recovered_layout = QHBoxLayout()
        recovered_label_title = QLabel("已恢复:")
        self.recovered_label = QLabel("0/0")
        recovered_layout.addWidget(recovered_label_title)
        recovered_layout.addWidget(self.recovered_label)
        
        # 添加到容器
        speed_recovered_layout.addLayout(speed_layout, 1)
        speed_recovered_layout.addLayout(recovered_layout, 1)
        
        # 添加到信息布局
        status_layout.addRow("", speed_recovered_container)
        
        # 添加状态信息布局到分组框布局
        group_layout.addLayout(status_layout)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        parent_layout.addWidget(group_box)
    
    def create_john_tools_area(self, parent_layout):
        """
        创建John哈希转换工具区
        
        Args:
            parent_layout: 父布局
        """
        # 创建分组框
        group_box = QGroupBox("John转换")
        group_layout = QVBoxLayout()
        
        # 添加说明标签
        description_label = QLabel("使用John工具将加密文件转换为哈希格式")
        description_label.setWordWrap(True)
        group_layout.addWidget(description_label)
        
        # 添加支持的文件类型标签
        supported_label = QLabel("支持格式: ZIP, RAR, 7Z, PDF, KeePass, Office等")
        supported_label.setWordWrap(True)
        group_layout.addWidget(supported_label)
        
        # 为了保持兼容性，使用隐藏的字段标记当前是hashcat格式
        self.join_type_combo = QComboBox()
        self.join_type_combo.addItems(["join2john", "join2hashcat"])
        self.join_type_combo.setCurrentIndex(1)  # 默认选择hashcat格式
        self.join_type_combo.hide()  # 隐藏这个控件
        
        # 创建文件选择按钮
        file_layout = QHBoxLayout()
        self.join_file_input = FileInputWidget(
            self.main_window,
            dialog_title="选择要转换的加密文件",
            file_filter="支持的文件 (*.zip *.rar *.7z *.pdf *.kdbx *.docx *.xlsx *.pptx);;所有文件 (*.*)",
            placeholder="选择要转换的加密文件"
        )
        file_layout.addWidget(self.join_file_input)
        group_layout.addLayout(file_layout)
        
        # 创建转换按钮
        import_button = QPushButton("John!")
        import_button.setStyleSheet(
            "QPushButton { background-color: #FFCCE5; color: #7D6B7D; }"
            "QPushButton:hover { background-color: #FFD9EC; }"
            "QPushButton:pressed { background-color: #FFC0CB; }"
        )
        import_button.clicked.connect(self.import_hash_file)
        group_layout.addWidget(import_button)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        parent_layout.addWidget(group_box)
    
    def import_hash_file(self):
        """
        导入Hash文件
        """
        # 获取导入类型
        join_type = self.join_type_combo.currentText()
        # 获取源文件路径
        source_file = self.join_file_input.get_path()
        
        if not source_file:
            from hashcat_gui.core.utils import show_error
            show_error(self.main_window, "错误", "请先选择要导入的文件")
            return
        
        # 目标文件路径
        output_path = os.path.splitext(source_file)[0] + ".hash"
        
        try:
            # 使用John的二进制工具
            import subprocess
            import tempfile
            
            # 获取文件扩展名
            file_ext = os.path.splitext(source_file)[1].lower()
            
            # 从配置管理器获取John路径
            john_path = self.config_manager.get_john_path()
            if not john_path:
                # 如果未设置，使用默认路径
                john_bin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..")
                john_bin_dir = os.path.abspath(os.path.join(john_bin_dir, "john_bin", "run"))
                self.update_output("警告: 未设置John路径，使用默认路径", error=True)
            else:
                # 使用配置的John路径
                john_bin_dir = os.path.dirname(john_path)
            
            # 根据文件类型选择适当的转换工具
            command = None
            
            # 支持的文件类型和对应的转换器
            converters = {
                ".zip": "zip2john.exe",
                ".rar": "rar2john.exe",
                ".7z": "7z2john.exe",
                ".pdf": "pdf2john.py",
                ".kdbx": "keepass2john.exe",
                ".docx": "office2john.py",
                ".xlsx": "office2john.py",
                ".pptx": "office2john.py"
            }
            
            if file_ext in converters:
                converter = converters[file_ext]
                converter_path = os.path.join(john_bin_dir, converter)
                
                # 如果是 Python 脚本
                if converter.endswith(".py"):
                    import sys
                    command = [sys.executable, converter_path, source_file]
                else:
                    command = [converter_path, source_file]
            else:
                from hashcat_gui.core.utils import show_error
                show_error(self.main_window, "错误", f"不支持的文件类型: {file_ext}")
                return
            
            # 检查转换器是否存在
            if not os.path.exists(converter_path):
                from hashcat_gui.core.utils import show_error
                show_error(self.main_window, "错误", f"找不到转换器: {converter_path}")
                return
            
            # 执行命令并捕获输出
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.hash') as temp_file:
                temp_path = temp_file.name
            
            # 打印调试信息
            cmd_str = ' '.join(str(x) for x in command)
            print(f"\n\n执行命令: {cmd_str}")
            
            # 根据是否为Python脚本来确定执行方式
            if converter.endswith(".py"):
                # Python脚本用参数列表执行
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                # EXE文件使用shell执行
                cmd_str = f'"{converter_path}" "{source_file}"'
                result = subprocess.run(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            
            # 打印命令结果
            print(f"返回码: {result.returncode}")
            print(f"标准输出: {result.stdout[:100]}{'...' if len(result.stdout) > 100 else ''}")
            print(f"错误输出: {result.stderr}")
            
            # 获取输出内容 - 注意有些John工具的输出写入stderr而非stdout
            output_content = result.stdout
            
            # 如果stdout为空，但stderr有内容，则使用stderr
            if not output_content.strip() and result.stderr.strip():
                output_content = result.stderr
            
            # 将输出写入临时文件
            with open(temp_path, 'w', encoding='utf-8') as outfile:
                outfile.write(output_content)
            
            # 检查执行结果
            if result.returncode != 0:
                from hashcat_gui.core.utils import show_error
                error_msg = result.stderr if result.stderr else "未知错误"
                show_error(self.main_window, "错误", f"转换失败: {error_msg}")
                os.remove(temp_path)  # 删除临时文件
                return
            
            # 读取临时文件内容
            with open(temp_path, 'r') as infile:
                hash_content = infile.read()
            
            # 检查是否有内容
            if not hash_content.strip():
                from hashcat_gui.core.utils import show_error
                show_error(self.main_window, "错误", "转换结果为空")
                os.remove(temp_path)  # 删除临时文件
                return
            
            # 始终输出hashcat格式
            # 将John格式转换为Hashcat格式
            # 通常John格式是: filename:$hash$...
            # Hashcat格式是: $hash$...
            if "$" in hash_content and ":" in hash_content:
                hash_content = hash_content.split(":", 1)[-1]
            
            # 将内容写入目标文件
            with open(output_path, 'w') as outfile:
                outfile.write(hash_content)
            
            # 删除临时文件
            os.remove(temp_path)
            
            # 更新哈希文件输入框
            self.hash_file_input.set_path(output_path)
            
            # 显示成功消息
            from hashcat_gui.core.utils import show_message
            show_message(self.main_window, "成功", f"已成功导入哈希文件到 {output_path}")
            
        except Exception as e:
            from hashcat_gui.core.utils import show_error
            show_error(self.main_window, "错误", f"导入失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def create_advanced_options_area(self, parent_layout):
        """
        创建高级选项区
        
        Args:
            parent_layout: 父布局
        """
        # 创建分组框
        group_box = QGroupBox("高级选项")
        group_layout = QFormLayout()
        
        # 输出文件
        self.output_file_input = FileInputWidget(
            self.main_window,
            dialog_title="选择输出文件",
            file_filter="文本文件 (*.txt);;所有文件 (*.*)",
            is_save=True,
            placeholder="保存结果的文件路径（可选）"
        )
        group_layout.addRow("输出文件:", self.output_file_input)
        
        # Potfile文件
        self.potfile_input = FileInputWidget(
            self.main_window,
            dialog_title="选择Potfile文件",
            file_filter="Potfile (*.pot);;所有文件 (*.*)",
            placeholder="Potfile路径（可选）"
        )
        # 默认使用配置中的Potfile路径
        potfile_path = self.config_manager.get_potfile_path()
        if potfile_path:
            self.potfile_input.set_path(potfile_path)
            
        group_layout.addRow("Potfile:", self.potfile_input)
        
        # 会话名称
        self.session_input = FileInputWidget(
            self.main_window,
            dialog_title="选择会话文件",
            file_filter="会话文件 (*.restore);;所有文件 (*.*)",
            placeholder="会话名称（可选）"
        )
        group_layout.addRow("会话名称:", self.session_input)
        
        # 设置分组框布局
        group_box.setLayout(group_layout)
        parent_layout.addWidget(group_box)
    
    def create_output_results_area(self, parent_layout):
        """
        创建输出和结果区
        
        Args:
            parent_layout: 父布局
        """
        # 创建标签页控件
        tab_widget = QTabWidget()
        
        # 输出控制台
        self.output_console = OutputConsole(self.main_window)
        tab_widget.addTab(self.output_console, "输出")
        
        # 可搜索的结果表格
        self.searchable_results_table = SearchableResultsTable(self.main_window)
        self.results_table = self.searchable_results_table.results_table  # 保留对原始表格的引用，保持兼容性
        tab_widget.addTab(self.searchable_results_table, "结果")
        
        # 添加标签页控件到父布局
        parent_layout.addWidget(tab_widget, 1)  # 1表示拉伸因子，这样输出区会占据大部分空间
    
    def update_hash_modes(self, hash_modes):
        """
        更新哈希模式下拉框
        
        Args:
            hash_modes (list): 哈希模式列表
        """
        # 清空下拉框
        self.hash_mode_combo.clear()
        
        # 保存原始哈希模式列表，用于搜索过滤
        self.all_hash_modes = hash_modes
        
        # 添加哈希模式到下拉框
        for mode in hash_modes:
            self.hash_mode_combo.addItem(f"{mode['id']} - {mode['name']}", mode['id'])
            
        # 设置初始选择
        self.hash_mode_combo.setCurrentIndex(0)
        
    def _filter_hash_modes(self, search_text):
        """
        根据搜索文本过滤哈希模式
        
        Args:
            search_text (str): 搜索文本
        """
        # 如果还没有哈希模式列表，直接返回
        if not hasattr(self, 'all_hash_modes') or not self.all_hash_modes:
            return
            
        # 保存当前选择的哈希模式
        current_mode = self.hash_mode_combo.currentData()
        
        # 清空并重新填充下拉框
        self.hash_mode_combo.clear()
        
        # 如果搜索文本为空，显示所有哈希模式
        if not search_text:
            for mode in self.all_hash_modes:
                self.hash_mode_combo.addItem(f"{mode['id']} - {mode['name']}", mode['id'])
        else:
            # 过滤哈希模式
            search_text = search_text.lower()
            found = False
            
            for mode in self.all_hash_modes:
                mode_id = str(mode['id'])
                mode_name = mode['name'].lower()
                
                # 如果搜索文本在 ID 或名称中
                if search_text in mode_id or search_text in mode_name:
                    self.hash_mode_combo.addItem(f"{mode['id']} - {mode['name']}", mode['id'])
                    found = True
            
            # 如果没有找到任何匹配项，显示所有哈希模式
            if not found:
                for mode in self.all_hash_modes:
                    self.hash_mode_combo.addItem(f"{mode['id']} - {mode['name']}", mode['id'])
                    
        # 尝试恢复之前的选中项
        if current_mode is not None:
            for i in range(self.hash_mode_combo.count()):
                if self.hash_mode_combo.itemData(i) == current_mode:
                    self.hash_mode_combo.setCurrentIndex(i)
                    break
    
    def update_attack_mode_panel(self, index):
        """
        根据攻击模式更新攻击模式面板
        
        Args:
            index (int): 攻击模式下拉框的索引
        """
        # 获取攻击模式ID
        attack_mode = self.attack_mode_combo.itemData(index)
        
        # 设置攻击模式面板
        self.attack_mode_panel.set_attack_mode(attack_mode)
    
    def _update_hash_input_state(self):
        """
        更新哈希输入相关控件的状态
        """
        # 根据单选按钮状态启用/禁用相应的输入控件
        is_file_mode = self.file_radio.isChecked()
        
        # 设置文件选择控件的启用状态
        self.hash_file_input.setEnabled(is_file_mode)
        
        # 设置直接输入文本框的启用状态
        self.hash_text_input.setEnabled(not is_file_mode)
    
    def set_cracking_state(self, is_cracking):
        """
        设置破解状态，更新UI状态
        
        Args:
            is_cracking (bool): 是否正在破解
        """
        # 启用/禁用控制按钮
        self.start_button.setEnabled(not is_cracking)
        self.stop_button.setEnabled(is_cracking)
        
        # 启用/禁用重要输入控件
        self.attack_mode_combo.setEnabled(not is_cracking)
        self.hash_mode_combo.setEnabled(not is_cracking)
        self.file_radio.setEnabled(not is_cracking)
        self.text_radio.setEnabled(not is_cracking)
        
        # 根据状态更新输入控件
        if not is_cracking:
            # 恢复正常状态
            self._update_hash_input_state()
        else:
            # 当破解进行时，禁用所有输入控件
            self.hash_file_input.setEnabled(False)
            self.hash_text_input.setEnabled(False)
        
        # 重置进度返回状态
        if not is_cracking:
            self.progress_bar.setValue(0)
            self.speed_label.setText("0 H/s")
            self.recovered_label.setText("0/0")
            self.status_value_label.setText("就绪")
    
    def update_output(self, text, error=False, success=False):
        """
        更新输出控制台
        
        Args:
            text (str): 输出文本
            error (bool): 是否为错误信息
            success (bool): 是否为成功信息
        """
        if self.output_console:
            self.output_console.append_text(text, error, success)
            
    def _on_hash_file_changed(self, path):
        """
        哈希文件改变时的处理方法
        
        Args:
            path (str): 新选择的哈希文件路径
        """
        if path and os.path.exists(path):
            # 获取potfile路径
            potfile_path = self.config_manager.get_potfile_path()
            if not potfile_path or not os.path.exists(potfile_path):
                potfile_path = os.path.join(os.path.dirname(self.main_window.hashcat_runner.hashcat_path), "hashcat.potfile")
                
            if potfile_path and os.path.exists(potfile_path):
                # 加载已破解的结果
                self.load_already_cracked_hashes(path, potfile_path)
                
    def load_already_cracked_hashes(self, hash_file_path, potfile_path):
        """
        从 potfile 中加载已破解的哈希结果
        
        Args:
            hash_file_path (str): 哈希文件路径
            potfile_path (str): potfile路径
        """
        if not hash_file_path or not potfile_path or not os.path.exists(hash_file_path) or not os.path.exists(potfile_path):
            return
            
        # 加载已破解的结果
        results = load_already_cracked(hash_file_path, potfile_path)
        
        if results:
            # 更新输出信息
            self.update_output(f"从 potfile 中加载了 {len(results)} 个已破解的哈希结果", success=True)
            
            # 添加到结果表格
            self.results_table.add_results(results)
    
    def update_status_info(self, status_info):
        """
        更新状态信息
        
        Args:
            status_info (dict): 状态信息字典
        """
        # 更新状态标签
        if 'status' in status_info:
            self.status_value_label.setText(status_info['status'])
        
        # 更新进度条
        if 'progress_percent' in status_info:
            self.progress_bar.setValue(int(status_info['progress_percent']))
        
        # 更新速度标签
        if 'speed' in status_info:
            self.speed_label.setText(status_info['speed'])
        
        # 更新已恢复标签
        if 'recovered' in status_info:
            self.recovered_label.setText(status_info['recovered'])
    
    def add_result(self, hash_val, password):
        """
        添加破解结果
        
        Args:
            hash_val (str): 哈希值
            password (str): 破解得到的密码
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 使用可搜索结果表格添加结果
        if hasattr(self, 'searchable_results_table'):
            self.searchable_results_table.add_result(hash_val, password, now)
        else:
            # 兼容性处理
            self.results_table.add_result(hash_val, password, now)
    
    def clear_results(self):
        """清空结果表格"""
        # 使用可搜索结果表格清除结果
        if hasattr(self, 'searchable_results_table'):
            self.searchable_results_table.clear_results()
        else:
            # 兼容性处理
            self.results_table.clear_results()
    
    def get_parameters(self):
        """
        获取所有参数
        
        Returns:
            dict: 参数字典
        """
        params = {}
        
        # 获取核心参数
        # 根据单选按钮状态决定哈希输入方式
        if self.file_radio.isChecked():  # 文件模式
            params['hash_file'] = self.hash_file_input.get_path()
        else:  # 直接输入模式
            # 获取文本输入内容
            hash_text = self.hash_text_input.toPlainText().strip()
            if hash_text:
                # 创建临时文件
                import tempfile
                import os
                
                # 生成一个临时文件名
                fd, temp_path = tempfile.mkstemp(suffix='.hash', prefix='hashcat_temp_')
                os.close(fd)
                
                # 写入数据
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(hash_text)
                    
                # 设置临时文件路径作为哈希文件
                params['hash_file'] = temp_path
                params['_temp_hash_file'] = True  # 标记临时文件，便于后续清理
                
                # 在日志中显示信息
                self.update_output(f"已创建临时哈希文件: {temp_path}", success=True)
        
        # 获取哈希模式
        hash_mode_index = self.hash_mode_combo.currentIndex()
        if hash_mode_index >= 0:
            # 获取itemData，如果为None，尝试从文本中提取
            hash_mode = self.hash_mode_combo.itemData(hash_mode_index)
            if hash_mode is None:
                # 尝试从文本中提取哈希模式编号
                text = self.hash_mode_combo.currentText()
                if text:
                    # 格式应该是 "123 - 哈希名称"
                    try:
                        hash_mode = int(text.split(' - ')[0])
                    except (ValueError, IndexError):
                        hash_mode = None
            
            if hash_mode is not None:
                # 强制将hash_mode转换为int，确保类型正确
                params['hash_mode'] = int(hash_mode)
                
            # 打印一些调试信息，帮助识别问题
            print(f"Selected hash mode: {hash_mode}, type: {type(hash_mode)}")
            print(f"Params: {params}")
            print(f"ComboBox text: {self.hash_mode_combo.currentText()}")
            print(f"ComboBox data: {self.hash_mode_combo.itemData(hash_mode_index)}")
            print(f"ComboBox index: {hash_mode_index}")
            
            # 在日志中输出信息
            self.main_window.hashcat_runner.output_ready.emit(f"已选择哈希模式: {hash_mode}, 类型: {type(hash_mode)}, 参数: {params.get('hash_mode')}")
            self.main_window.hashcat_runner.output_ready.emit(f"下拉框文本: {self.hash_mode_combo.currentText()}, 数据: {self.hash_mode_combo.itemData(hash_mode_index)}")
            
        
        # 获取攻击模式
        attack_mode_index = self.attack_mode_combo.currentIndex()
        if attack_mode_index >= 0:
            params['attack_mode'] = self.attack_mode_combo.itemData(attack_mode_index)
        
        # 获取攻击模式特定参数
        attack_mode_params = self.attack_mode_panel.get_params()
        params.update(attack_mode_params)
        
        # 获取高级选项参数
        params['output_file'] = self.output_file_input.get_path()
        params['potfile_path'] = self.potfile_input.get_path()
        params['session'] = self.session_input.get_path()
        
        # 添加默认选项
        params['force'] = True
        params['status'] = True
        params['status_timer'] = 1
        
        return params
    
    def open_hash_directory(self):
        """打开哈希文件目录选择器"""
        directory = QFileDialog.getExistingDirectory(self.main_window, "选择哈希文件目录")
        if directory:
            self.directory_hash_input.setText(directory)
            
    def open_hash_file(self):
        """打开哈希文件"""
        # 获取文件路径
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "选择哈希文件",
            self.config_manager.get_work_dir(),
            "哈希文件 (*.txt *.hash *.lst *.hashes);;所有文件 (*.*)"
        )
        
        if file_path:
            self.hash_file_input.set_path(file_path)
