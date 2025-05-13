#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hashcat执行器 - 负责构建和执行Hashcat命令，处理进程交互
"""

import os
import re
import shlex
import time
import subprocess
from PySide6.QtCore import QObject, Signal, QProcess, QTimer


class HashcatRunner(QObject):
    """Hashcat执行器类，用于运行Hashcat命令并处理输出"""
    
    # 定义信号
    output_ready = Signal(str)  # 输出信号
    error_occurred = Signal(str)  # 错误信号
    process_finished = Signal(int, object)  # 进程结束信号
    password_found = Signal(str, str)  # 密码找到信号
    status_update = Signal(dict)  # 状态更新信号
    
    def __init__(self, config_manager):
        """
        初始化Hashcat执行器
        
        Args:
            config_manager: 配置管理器实例
        """
        super().__init__()
        self.config_manager = config_manager
        self.process = None
        self.hashcat_path = ""
        self._current_params = None
        self._result_check_scheduled = False
        self._result_read_scheduled = False    # 是否已经安排从 potfile 文件中读取结果
        self._last_show_potfile_time = 0       # 上次运行show_potfile的时间
        self._getting_results = False          # 是否正在获取结果
        self.processed_hashes = set()          # 已处理的哈希值集合，避免重复
        self.update_hashcat_path()
        
        # 正则表达式，用于从输出中提取信息
        self.status_regex = re.compile(r'Status\.+: (.+)')
        self.speed_regex = re.compile(r'Speed\.#1\.+: (.+)')
        self.recovered_regex = re.compile(r'Recovered\.+: (\d+)/(\d+)')
        self.progress_regex = re.compile(r'Progress\.+: (\d+)/(\d+)')
        self.hash_target_regex = re.compile(r'Hash\.Target\.+: (.+)')
        self.time_regex = re.compile(r'Time\.Started\.+: (.+)')
        self.hash_type_regex = re.compile(r'Hash\.Type\.+: (.+)')
        self.guess_base_regex = re.compile(r'Guess\.Base\.+: (.+)')
        self.guess_queue_regex = re.compile(r'Guess\.Queue\.+: (.+)')
        self.guess_charset_regex = re.compile(r'Guess\.Charset\.+: (.+)')
        # 扩展破解结果正则表达式，支持更多格式，但避免误匹配hashcat输出的状态信息
        self.cracked_regex = re.compile(r'^\s*([0-9a-f$\-_\.:+\[\]]+):\s+([^\s].+)$')
        # 特别检测的正则表达式
        self.pkzip_regex = re.compile(r'(\$pkzip2\$[^:]+):\s+(\S+)')
        self.recovery_status_regex = re.compile(r'Recovered\.\.+: (\d+)/(\d+)')
    
    def update_hashcat_path(self):
        """更新Hashcat路径"""
        self.hashcat_path = self.config_manager.get_hashcat_path()
    
    def start_cracking(self, params):
        """
        开始破解过程
        
        Args:
            params (dict): 破解参数字典
            
        Returns:
            bool: 是否成功启动破解
        """
        # 保存当前参数，以便在检测到potfile条目时使用
        self._current_params = params.copy()
        
        # 检查是否有临时哈希文件
        if params.get('_temp_hash_file') and params.get('hash_file'):
            self._temp_hash_file_path = params['hash_file']
            
        # 检查Hashcat路径是否存在
        if not self.hashcat_path or not os.path.exists(self.hashcat_path):
            self.error_occurred.emit("Hashcat可执行文件路径无效，请在设置中配置")
            return False
            
        # 构建命令行参数
        cmd_args = [self.hashcat_path]
        
        # 添加基本参数
        if params.get('hash_file'):
            cmd_args.append(params['hash_file'])
        
        # 特别处理哈希模式，需要处理哈希模式为0的情况
        if 'hash_mode' in params:
            cmd_args.extend(['-m', str(params['hash_mode'])])
        
        if params.get('attack_mode') is not None:
            cmd_args.extend(['-a', str(params['attack_mode'])])
            
        # 根据攻击模式添加特定参数
        attack_mode = params.get('attack_mode')
        
        if attack_mode == 0:  # 字典攻击
            if params.get('dict_file'):
                cmd_args.append(params['dict_file'])
            if params.get('rule_file'):
                cmd_args.extend(['-r', params['rule_file']])
                
        elif attack_mode == 1:  # 组合攻击
            if params.get('dict_file1') and params.get('dict_file2'):
                cmd_args.append(params['dict_file1'])
                cmd_args.append(params['dict_file2'])
                
        elif attack_mode == 3:  # 暴力攻击
            if params.get('mask'):
                cmd_args.append(params['mask'])
                
        elif attack_mode == 6:  # 混合攻击(字典+掩码)
            if params.get('dict_file') and params.get('mask'):
                cmd_args.append(params['dict_file'])
                cmd_args.append(params['mask'])
                
        elif attack_mode == 7:  # 混合攻击(掩码+字典)
            if params.get('mask') and params.get('dict_file'):
                cmd_args.append(params['mask'])
                cmd_args.append(params['dict_file'])
        
        # 添加输出文件参数
        if params.get('output_file'):
            cmd_args.extend(['-o', params['output_file']])
            
        # 添加potfile参数
        if params.get('potfile_path') and not params.get('potfile_disable'):
            cmd_args.extend(['--potfile-path', params['potfile_path']])
            
        # 添加会话参数
        if params.get('session'):
            cmd_args.extend(['--session', params['session']])
            
        # 添加设备参数
        if params.get('devices'):
            cmd_args.extend(['-d', ','.join(params['devices'])])
            
        # 添加其他参数
        if params.get('force'):
            cmd_args.append('--force')
            
        if params.get('remove'):
            cmd_args.append('--remove')
            
        if params.get('status'):
            cmd_args.append('--status')
            
        if params.get('status_timer'):
            cmd_args.extend(['--status-timer', str(params['status_timer'])])
            
        if params.get('hwmon_temp_abort') is not None:
            cmd_args.extend(['--hwmon-temp-abort', str(params['hwmon_temp_abort'])])
        
        # 添加参数确保处理所有哈希值
        cmd_args.append('--keep-guessing')            # 在发现一个匹配后继续处理剩余哈希
        cmd_args.append('--outfile-autohex-disable')   # 禁用自动跳过
        
        # 特别的参数，保证我们能匹配到所有哈希值
        cmd_args.append('--runtime=60')                # 最多运行60秒
        
        # 输出多个哈希相关参数
        if not params.get('skip_output'):
            # 设置临时输出文件保存破解结果
            temp_output_file = os.path.join(os.path.dirname(params.get('hash_file', '')), 'hash_results.txt')
            cmd_args.extend(['-o', temp_output_file])
            params['_temp_output_file'] = temp_output_file
            
            # 设置输出格式
            cmd_args.append('--outfile-format=3')     # 使用格式3: hash:password
    
        # 不禁用potfile，而是利用它来记录破解结果
        if params.get('potfile_path'):
            cmd_args.extend(['--potfile-path', params['potfile_path']])
        else:
            # 使用默认的potfile路径
            default_potfile = os.path.join(os.path.dirname(self.hashcat_path), "hashcat.potfile")
            cmd_args.extend(['--potfile-path', default_potfile])
        
        # 创建QProcess实例
        self.process = QProcess()
        
        # 连接信号
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_error)
        
        # 设置工作目录为hashcat所在的目录
        hashcat_dir = os.path.dirname(self.hashcat_path)
        self.process.setWorkingDirectory(hashcat_dir)
        
        # 启动进程
        self.output_ready.emit(f"运行命令: {' '.join(cmd_args)}")
        self.process.start(cmd_args[0], cmd_args[1:])
        
        # 检查是否成功启动
        if not self.process.waitForStarted(3000):
            self.error_occurred.emit("启动Hashcat进程失败")
            return False
            
        return True
    
    def stop_cracking(self):
        """停止破解进程"""
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            # 给进程一些时间来优雅地退出
            QTimer.singleShot(2000, self._kill_if_running)
            return True
        return False
    
    def _kill_if_running(self):
        """如果进程仍在运行，则强制终止"""
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.kill()
    
    def show_potfile(self, hash_file, potfile_path=None):
        """
        显示已破解的哈希
        
        Args:
            hash_file (str): 哈希文件路径
            potfile_path (str, optional): potfile路径
            
        Returns:
            bool: 是否成功启动命令
        """
        if not self.hashcat_path or not os.path.exists(self.hashcat_path):
            self.error_occurred.emit("Hashcat可执行文件路径无效，请在设置中配置")
            return False
            
        # 构建命令行参数
        cmd_args = [self.hashcat_path, "--show", hash_file]
        
        # 添加potfile参数
        if potfile_path:
            cmd_args.extend(["--potfile-path", potfile_path])
            
        # 创建QProcess实例
        self.process = QProcess()
        
        # 连接信号
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_error)
        
        # 设置工作目录为hashcat所在的目录
        hashcat_dir = os.path.dirname(self.hashcat_path)
        self.process.setWorkingDirectory(hashcat_dir)
        
        # 加入环境变量，确保它可以找到OpenCL目录
        environment = QProcess.systemEnvironment()
        environment.append(f"PATH={hashcat_dir};%PATH%")
        self.process.setEnvironment(environment)
        
        # 启动进程
        self.output_ready.emit(f"运行命令: {' '.join(cmd_args)}")
        self.process.start(cmd_args[0], cmd_args[1:])
        
        # 检查是否成功启动
        if not self.process.waitForStarted(3000):
            self.error_occurred.emit("启动Hashcat进程失败")
            return False
            
        return True
    
    def show_left_hashes(self, hash_file, potfile_path=None):
        """
        显示未破解的哈希
        
        Args:
            hash_file (str): 哈希文件路径
            potfile_path (str, optional): potfile路径
            
        Returns:
            bool: 是否成功启动命令
        """
        if not self.hashcat_path or not os.path.exists(self.hashcat_path):
            self.error_occurred.emit("Hashcat可执行文件路径无效，请在设置中配置")
            return False
            
        cmd_args = [self.hashcat_path, '--left']
        
        if hash_file:
            cmd_args.append(hash_file)
            
        if potfile_path:
            cmd_args.extend(['--potfile-path', potfile_path])
        
        # 创建QProcess实例
        self.process = QProcess()
        
        # 连接信号
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_error)
        
        # 启动进程
        self.output_ready.emit(f"运行命令: {' '.join(cmd_args)}")
        self.process.start(cmd_args[0], cmd_args[1:])
        
        return True
    
    def get_device_info(self):
        """
        获取设备信息
        
        Returns:
            bool: 是否成功启动命令
        """
        if not self.hashcat_path or not os.path.exists(self.hashcat_path):
            self.error_occurred.emit("Hashcat可执行文件路径无效，请在设置中配置")
            return False
            
        cmd_args = [self.hashcat_path, '-I']
        
        # 创建QProcess实例
        self.process = QProcess()
        
        # 连接信号
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_error)
        
        # 启动进程
        self.output_ready.emit(f"运行命令: {' '.join(cmd_args)}")
        self.process.start(cmd_args[0], cmd_args[1:])
        
        return True
    
    def _handle_stdout(self):
        """处理标准输出"""
        if self.process:
            data = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            self.output_ready.emit(data)
            self._parse_output(data)
    
    def _handle_stderr(self):
        """处理标准错误"""
        if self.process:
            data = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')
            self.error_occurred.emit(data)
    
    def _handle_finished(self, exit_code, exit_status):
        """
        处理进程结束
        
        Args:
            exit_code (int): 退出代码
            exit_status (QProcess.ExitStatus): 退出状态
        """
        # 输出任务结束提示
        self.output_ready.emit("检测到任务已完成或中断，正在获取结果...")
        
        # 首先从 potfile 读取结果，确保在清理临时文件前完成
        self.output_ready.emit("检测到破解已完成，将从 potfile 文件读取结果...")
        self._read_results_from_potfile()
        
        # 输出格式化的时间信息
        started = time.strftime("%c", time.localtime(self.start_time)) if hasattr(self, 'start_time') else "未知时间"
        stopped = time.strftime("%c", time.localtime())
        self.output_ready.emit(f"Started: {started}\nStopped: {stopped}")
        
        # 发送进程结束信号
        self.process_finished.emit(exit_code, exit_status)
        
        # 所有处理完成后，清理临时哈希文件
        self._cleanup_temp_hash_file()
    
    def _cleanup_temp_hash_file(self):
        """清理临时哈希文件"""
        # 检查是否存在临时文件属性
        temp_file_path = getattr(self, '_temp_hash_file_path', None)
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                self.output_ready.emit(f"已清理临时哈希文件: {temp_file_path}")
            except Exception as e:
                self.error_occurred.emit(f"清理临时文件时出错: {str(e)}")
            
            # 重置临时文件路径
            self._temp_hash_file_path = None
    
    def _handle_error(self, error):
        """
        处理进程错误
        
        Args:
            error (QProcess.ProcessError): 错误类型
        """
        error_messages = {
            QProcess.FailedToStart: "进程启动失败",
            QProcess.Crashed: "进程崩溃",
            QProcess.Timedout: "进程超时",
            QProcess.WriteError: "写入进程失败",
            QProcess.ReadError: "读取进程失败",
            QProcess.UnknownError: "未知错误"
        }
        self.error_occurred.emit(f"进程错误: {error_messages.get(error, '未知错误')}")
    
    def _parse_output(self, output):
        """
        解析输出，提取状态信息和破解结果
        
        Args:
            output (str): 输出文本
        """
        # 解析状态信息
        status_info = {}
        
        status_match = self.status_regex.search(output)
        if status_match:
            status_info['status'] = status_match.group(1)
            
        speed_match = self.speed_regex.search(output)
        if speed_match:
            status_info['speed'] = speed_match.group(1)
            
        recovered_match = self.recovered_regex.search(output)
        if recovered_match:
            status_info['recovered'] = f"{recovered_match.group(1)}/{recovered_match.group(2)}"
            # 如果发现破解了哈希，记录下来
            try:
                recovered = int(recovered_match.group(1))
                total = int(recovered_match.group(2))
                if recovered > 0:
                    self.output_ready.emit(f"破解进度: {recovered}/{total} ({recovered/total*100:.2f}%)")
                    # 如果有破解结果，确保在进程结束后显示结果
                    if hasattr(self, '_result_check_scheduled') and not self._result_check_scheduled:
                        self._result_check_scheduled = True
                        self.output_ready.emit("检测到有破解结果，将在完成后显示")
                        # 等待1秒后尝试显示当前的破解结果
                        QTimer.singleShot(1000, lambda: self._check_current_results())
            except (ValueError, ZeroDivisionError):
                pass
        
        progress_match = self.progress_regex.search(output)
        if progress_match:
            try:
                current = int(progress_match.group(1))
                total = int(progress_match.group(2))
                percentage = 0
                if total > 0:
                    percentage = (current / total) * 100
                status_info['progress'] = f"{current}/{total} ({percentage:.2f}%)"
                status_info['progress_percent'] = percentage
            except ValueError:
                pass
        
        hash_target_match = self.hash_target_regex.search(output)
        if hash_target_match:
            status_info['hash_target'] = hash_target_match.group(1)
            
        time_match = self.time_regex.search(output)
        if time_match:
            status_info['time_started'] = time_match.group(1)
            
        hash_type_match = self.hash_type_regex.search(output)
        if hash_type_match:
            status_info['hash_type'] = hash_type_match.group(1)
            
        # 如果有状态信息，发出状态更新信号
        if status_info:
            self.status_update.emit(status_info)
        
        # 检测是否出现「哈希已在potfile中」的消息
        if "All hashes found as potfile" in output and hasattr(self, '_current_params') and self._current_params:
            self.output_ready.emit("检测到哈希已存在于potfile中，正在获取破解结果...")
            # 等待进程结束后自动运行show_potfile命令
            QTimer.singleShot(500, lambda: self._auto_show_potfile(self._current_params.get('hash_file')))
        
        # 检测是否显示"Session........"，表示已完成或中断
        if "Session..........: hashcat" in output and "Status...........:" in output:
            self.output_ready.emit("检测到任务已完成或中断，正在获取结果...")
            # 等待进程结束后检查结果
            QTimer.singleShot(500, lambda: self._check_current_results())
        
        # 检测特殊格式的破解结果（例如pkzip）
        for line in output.splitlines():
            # 跳过含有特定状态信息的行
            if 'Time.Started' in line or 'Status...........:' in line or 'Recovered' in line or 'Progress' in line:
                continue
            
            pkzip_match = self.pkzip_regex.match(line)
            if pkzip_match:
                hash_val = pkzip_match.group(1)
                password = pkzip_match.group(2)
                # 检查是否是误匹配的状态行
                if 'Started' not in password and 'Status' not in password and 'Recovery' not in password:
                    self.output_ready.emit(f"检测到PKZIP格式结果: {hash_val}:{password}")
                    self.password_found.emit(hash_val, password)
        
        # 我们不从输出流中检测破解结果，而是在破解结束后从 potfile 文件中读取
        # 破解完成标记
        if "Session..........: hashcat" in output and "Status...........:" in output:
            self.output_ready.emit("检测到破解已完成，将从 potfile 文件读取结果...")
            # 在进程结束后从 potfile 文件中读取破解结果
            if hasattr(self, '_result_read_scheduled') and not self._result_read_scheduled:
                self._result_read_scheduled = True
                QTimer.singleShot(1000, self._read_results_from_potfile)
    
    def _auto_show_potfile(self, hash_file):
        """自动运行show_potfile命令"""
        # 防止死循环，如果刚刚运行了show_potfile，则不重复运行
        if hasattr(self, '_last_show_potfile_time') and time.time() - self._last_show_potfile_time < 5:
            return
        
        if hash_file:
            self._last_show_potfile_time = time.time()
            self.show_potfile(hash_file, self._current_params.get('potfile_path'))

    def _read_results_from_potfile(self):
        """从potfile文件中读取破解结果"""
        # 获取当前哈希文件和potfile路径
        hash_file = None
        potfile_path = None
        
        if hasattr(self, '_current_params') and self._current_params:
            hash_file = self._current_params.get('hash_file')
            if self._current_params.get('potfile_path'):
                potfile_path = self._current_params.get('potfile_path')
            else:
                potfile_path = os.path.join(os.path.dirname(self.hashcat_path), "hashcat.potfile")
        
        if not hash_file:
            self.output_ready.emit("无法获取当前哈希文件路径")
            return
            
        if not potfile_path or not os.path.exists(potfile_path):
            self.output_ready.emit("无法找到potfile文件或文件不存在")
            return
            
        # 首先读取当前哈希文件中的所有哈希值
        hash_values = set()
        try:
            with open(hash_file, 'r', encoding='utf-8', errors='ignore') as f:
                hash_content = f.readlines()
                
            for line in hash_content:
                line = line.strip()
                if not line:
                    continue
                # 尝试从行中提取哈希值（可能有不同格式）
                if ':' in line:
                    hash_part = line.split(':', 1)[0].strip()
                    hash_values.add(hash_part)
                else:
                    hash_values.add(line.strip())
                    
            self.output_ready.emit(f"从哈希文件中读取到 {len(hash_values)} 个哈希值")
        except Exception as e:
            self.output_ready.emit(f"读取哈希文件时出错: {str(e)}")
            return
        
        # 读取potfile文件
        try:
            with open(potfile_path, 'r', encoding='utf-8', errors='ignore') as f:
                potfile_content = f.readlines()
            
            # 处理每一行，并只匹配当前哈希文件中的哈希值
            result_count = 0
            for line in potfile_content:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                    
                hash_val, password = line.split(':', 1)
                
                # 检查是否是我们当前关心的哈希值
                # 首先检查完整匹配
                hash_found = False
                if hash_val in hash_values:
                    hash_found = True
                else:
                    # 检查哈希值是否是当前文件中任何哈希的子串或超串
                    for h in hash_values:
                        if h in hash_val or hash_val in h:
                            hash_found = True
                            break
                
                if not hash_found:
                    continue
                    
                # 检查是否已处理过该哈希值
                if hash_val in self.processed_hashes:
                    continue
                
                # 添加到已处理集合
                self.processed_hashes.add(hash_val)
                
                # 发送破解结果
                self.password_found.emit(hash_val, password)
                result_count += 1
            
            self.output_ready.emit(f"从 potfile 文件中读取到 {result_count} 条相关破解结果")
            
        except Exception as e:
            self.output_ready.emit(f"读取 potfile 文件时出错: {str(e)}")

    def _check_current_results(self):
        """检查当前破解结果"""
        # 重置检查标记
        self._result_check_scheduled = False
        
        # 从 potfile 文件中读取破解结果
        self._read_results_from_potfile()
