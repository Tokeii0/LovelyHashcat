#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器 - 用于管理应用程序设置
"""

import os
import json
from PySide6.QtCore import QSettings


class ConfigManager:
    """配置管理器类，用于管理应用程序设置"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.settings = QSettings("LovelyHashcat", "LovelyHashcat")
        self.default_config = {
            # Hashcat 相关设置
            "hashcat_path": "",
            "default_work_dir": "",
            "potfile_path": "",
            
            # John the Ripper 相关设置
            "john_path": "",               # John 可执行文件路径
            "john_config_path": "",        # John 配置文件路径
            "john_pot_path": "",           # John pot 文件路径
            "john_wordlist_path": "",      # John 默认字典路径
            "john_rules_path": "",         # John 规则文件路径
            
            # 界面相关设置
            "interface_theme": "default",
            "font_size": 10,
            "save_output": True,
            "output_dir": ""
        }
    
    def get_hashcat_path(self):
        """
        获取Hashcat可执行文件路径
        
        Returns:
            str: Hashcat可执行文件路径
        """
        return self.settings.value("hashcat_path", "")
    
    def set_hashcat_path(self, path):
        """
        设置Hashcat可执行文件路径
        
        Args:
            path (str): Hashcat可执行文件路径
        """
        self.settings.setValue("hashcat_path", path)
    
    def get_work_dir(self):
        """
        获取默认工作目录
        
        Returns:
            str: 默认工作目录
        """
        work_dir = self.settings.value("default_work_dir", "")
        if not work_dir:
            work_dir = os.path.expanduser("~")
        return work_dir
    
    def set_work_dir(self, path):
        """
        设置默认工作目录
        
        Args:
            path (str): 默认工作目录
        """
        self.settings.setValue("default_work_dir", path)
    
    def get_potfile_path(self):
        """
        获取potfile文件路径
        
        Returns:
            str: potfile文件路径
        """
        # 先检查设置中是否有指定的potfile路径
        path = self.settings.value("potfile_path", "")
        if path and os.path.exists(path):
            return path
        
        # 如果没有指定或路径不存在，尝试使用hashcat路径下的默认potfile
        hashcat_dir = os.path.dirname(self.get_hashcat_path())
        default_path = os.path.join(hashcat_dir, "hashcat.potfile")
        if os.path.exists(default_path):
            return default_path
            
        return ""
        
    def set_potfile_path(self, path):
        """
        设置potfile文件路径
        
        Args:
            path (str): potfile文件路径
        """
        self.settings.setValue("potfile_path", path)
        
    # John the Ripper 相关方法
    def get_john_path(self):
        """
        获取John the Ripper可执行文件路径
        
        Returns:
            str: John可执行文件路径
        """
        return self.settings.value("john_path", "")
    
    def set_john_path(self, path):
        """
        设置John the Ripper可执行文件路径
        
        Args:
            path (str): John可执行文件路径
        """
        self.settings.setValue("john_path", path)
    
    def get_john_config_path(self):
        """
        获取John配置文件路径
        
        Returns:
            str: John配置文件路径
        """
        # 先检查设置中是否有指定的配置文件路径
        path = self.settings.value("john_config_path", "")
        if path and os.path.exists(path):
            return path
        
        # 如果没有指定或路径不存在，尝试使用John路径下的默认配置
        john_dir = os.path.dirname(self.get_john_path())
        default_path = os.path.join(john_dir, "john.conf")
        if os.path.exists(default_path):
            return default_path
            
        return ""
    
    def set_john_config_path(self, path):
        """
        设置John配置文件路径
        
        Args:
            path (str): John配置文件路径
        """
        self.settings.setValue("john_config_path", path)
    
    def get_john_pot_path(self):
        """
        获取John pot文件路径
        
        Returns:
            str: John pot文件路径
        """
        # 先检查设置中是否有指定的pot文件路径
        path = self.settings.value("john_pot_path", "")
        if path and os.path.exists(path):
            return path
        
        # 如果没有指定或路径不存在，尝试使用John路径下的默认pot文件
        john_dir = os.path.dirname(self.get_john_path())
        default_path = os.path.join(john_dir, "john.pot")
        if os.path.exists(default_path):
            return default_path
            
        return ""
    
    def set_john_pot_path(self, path):
        """
        设置John pot文件路径
        
        Args:
            path (str): John pot文件路径
        """
        self.settings.setValue("john_pot_path", path)
    
    def get_john_wordlist_path(self):
        """
        获取John默认字典路径
        
        Returns:
            str: John默认字典路径
        """
        return self.settings.value("john_wordlist_path", "")
    
    def set_john_wordlist_path(self, path):
        """
        设置John默认字典路径
        
        Args:
            path (str): John默认字典路径
        """
        self.settings.setValue("john_wordlist_path", path)
    
    def get_john_rules_path(self):
        """
        获取John规则文件路径
        
        Returns:
            str: John规则文件路径
        """
        return self.settings.value("john_rules_path", "")
    
    def set_john_rules_path(self, path):
        """
        设置John规则文件路径
        
        Args:
            path (str): John规则文件路径
        """
        self.settings.setValue("john_rules_path", path)
    
    def get_theme(self):
        """
        获取界面主题
        
        Returns:
            str: 界面主题名称
        """
        return self.settings.value("interface_theme", "default")
    
    def set_theme(self, theme):
        """
        设置界面主题
        
        Args:
            theme (str): 界面主题名称
        """
        self.settings.setValue("interface_theme", theme)
    
    def get_font_size(self):
        """
        获取字体大小
        
        Returns:
            int: 字体大小
        """
        return int(self.settings.value("font_size", 10))
    
    def set_font_size(self, size):
        """
        设置字体大小
        
        Args:
            size (int): 字体大小
        """
        self.settings.setValue("font_size", size)
    
    def get_save_output(self):
        """
        获取是否保存输出
        
        Returns:
            bool: 是否保存输出
        """
        return self.settings.value("save_output", True, bool)
    
    def set_save_output(self, save):
        """
        设置是否保存输出
        
        Args:
            save (bool): 是否保存输出
        """
        self.settings.setValue("save_output", save)
    
    def get_output_dir(self):
        """
        获取输出保存目录
        
        Returns:
            str: 输出保存目录
        """
        output_dir = self.settings.value("output_dir", "")
        if not output_dir:
            output_dir = os.path.expanduser("~")
        return output_dir
    
    def set_output_dir(self, path):
        """
        设置输出保存目录
        
        Args:
            path (str): 输出保存目录
        """
        self.settings.setValue("output_dir", path)
    
    def load_settings(self):
        """
        加载所有设置
        
        Returns:
            dict: 包含所有设置的字典
        """
        config = {}
        for key in self.default_config.keys():
            if key in ["save_output"]:
                config[key] = self.settings.value(key, self.default_config[key], bool)
            elif key in ["font_size"]:
                config[key] = int(self.settings.value(key, self.default_config[key]))
            else:
                config[key] = self.settings.value(key, self.default_config[key])
        return config
    
    def save_settings(self, config):
        """
        保存所有设置
        
        Args:
            config (dict): 包含所有设置的字典
        """
        for key, value in config.items():
            self.settings.setValue(key, value)
    
    def reset_to_default(self):
        """重置所有设置为默认值"""
        for key, value in self.default_config.items():
            self.settings.setValue(key, value)
