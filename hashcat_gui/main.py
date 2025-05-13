#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LovelyHashcat - 主程序入口
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale

from hashcat_gui.gui.main_window import MainWindow


def main():
    """应用程序主入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序名称和组织
    app.setApplicationName("LovelyHashcat")
    app.setOrganizationName("LovelyHashcat")
    
    # 尝试使用系统语言
    translator = QTranslator()
    locale = QLocale.system().name()
    if translator.load(f":/translations/lovelyhashcat_{locale}"):
        app.installTranslator(translator)
    
    # 创建并显示主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 进入事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
