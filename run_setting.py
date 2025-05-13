#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置启动器 - 直接打开配置对话框，无需启动主程序
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from hashcat_gui.core.config_manager import ConfigManager
from hashcat_gui.gui.dialogs.settings_dialog import SettingsDialog
from hashcat_gui.gui.style_loader import StyleLoader

def main():
    """主函数，运行设置对话框"""
    # 初始化应用程序
    app = QApplication(sys.argv)
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(__file__), "hashcat_gui", "assets", "icons", "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 应用样式
    StyleLoader.apply_style()
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 创建设置对话框
    dialog = SettingsDialog(config_manager)
    
    # 修改对话框标题，以便区分是从设置启动器打开的
    dialog.setWindowTitle("LovelyHashcat - 设置")
    
    # 显示对话框
    result = dialog.exec()
    
    # 如果用户点击了确定按钮，显示保存成功的消息
    if result:
        QMessageBox.information(None, "设置已保存", "设置已成功保存！\n\n下次启动程序时将应用新设置。")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
