#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LovelyHashcat 启动脚本
"""

import os
import sys

# 将当前目录添加到Python路径中，这样可以导入hashcat_gui包
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入主函数
from hashcat_gui.main import main

if __name__ == "__main__":
    main()
