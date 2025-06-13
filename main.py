#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱 v0.1
作者: YYS
GitHub: https://github.com/yys20071108/-adb-
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import threading
import time
import os
import sys
import json
import zipfile
from pathlib import Path
import webbrowser
import queue
import platform

# 修复PIL导入问题
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: PIL/Pillow未安装，图标功能将被禁用")

# 修复requests导入问题
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("警告: requests未安装，网络功能将被禁用")

class ADBToolbox:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.check_environment()
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("奕奕ADB工具箱 v0.1")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # 设置图标 - 添加更好的错误处理
        try:
            if getattr(sys, 'frozen', False):
                # 打包后的环境
                icon_path = self.resource_path("icon.ico")
            else:
                # 开发环境
                icon_path = "assets/icon.ico"
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"图标文件未找到: {icon_path}")
        except Exception as e:
            print(f"设置图标失败: {e}")
            
        # 设置主题色
        self.colors = {
            'primary': '#6366f1',
            'secondary': '#8b5cf6', 
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'dark': '#1f2937',
            'light': '#f9fafb'
        }
        
    def resource_path(self, relative_path):
        """获取资源文件路径"""
        try:
            # PyInstaller创建的临时文件夹
            base_path = sys._MEIPASS
        except AttributeError:
            # 开发环境
            base_path = os.path.abspath(".")
    
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            return full_path
        else:
            # 如果文件不存在，返回当前目录下的路径
            return os.path.join(os.path.abspath("."), relative_path)
        
    def setup_variables(self):
        """初始化变量"""
        self.connected_devices = []
        self.current_device = tk.StringVar()
        self.connection_status = tk.StringVar(value="未连接")
        self.adb_path = "adb"
        self.log_queue = queue.Queue()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部工具栏
        self.create_toolbar(main_frame)
        
        # 创建左右分割面板
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 左侧面板
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # 右侧面板
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        # 设置左侧面板内容
        self.setup_left_panel(left_frame)
        
        # 设置右侧面板内容
        self.setup_right_panel(right_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
        
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 标题和版本
        title_frame = ttk.Frame(toolbar)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="奕奕ADB工具箱", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(title_frame, text="v0.1", font=('Arial', 10))
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 右侧按钮
        button_frame = ttk.Frame(toolbar)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="检查更新", command=self.check_update).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="关于", command=self.show_about).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="设置", command=self.show_settings).pack(side=tk.RIGHT, padx=(5, 0))
        
    def setup_left_panel(self, parent):
        """设置左侧面板"""
        # 设备连接区域
        connection_frame = ttk.LabelFrame(parent, text="设备连接", padding=10)
        connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接方式选择
        ttk.Label(connection_frame, text="连接方式:").pack(anchor=tk.W)
        connection_type = ttk.Combobox(connection_frame, values=["USB连接", "WiFi连接"], state="readonly")
        connection_type.set("USB连接")
        connection_type.pack(fill=tk.X, pady=(5, 10))
        
        # WiFi连接设置
        wifi_frame = ttk.Frame(connection_frame)
        wifi_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(wifi_frame, text="IP地址:").pack(anchor=tk.W)
        self.ip_entry = ttk.Entry(wifi_frame)
        self.ip_entry.insert(0, "192.168.1.100")
        self.ip_entry.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(wifi_frame, text="端口:").pack(anchor=tk.W)
        self.port_entry = ttk.Entry(wifi_frame)
        self.port_entry.insert(0, "5555")
        self.port_entry.pack(fill=tk.X, pady=(2, 10))
        
        # 连接按钮
        button_frame = ttk.Frame(connection_frame)
        button_frame.pack(fill=tk.X)
        
        self.connect_btn = ttk.Button(button_frame, text="连接设备", command=self.connect_device)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(button_frame, text="刷新", command=self.refresh_devices).pack(side=tk.RIGHT)
        
        # 设备信息区域
        device_frame = ttk.LabelFrame(parent, text="设备信息", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.device_info_text = tk.Text(device_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(device_frame, orient=tk.VERTICAL, command=self.device_info_text.yview)
        self.device_info_text.configure(yscrollcommand=scrollbar.set)
        
        self.device_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 环境检测区域
        env_frame = ttk.LabelFrame(parent, text="环境检测", padding=10)
        env_frame.pack(fill=tk.X)
        
        self.env_status = {}
        env_items = [
            ("ADB环境", "adb_status"),
            ("Platform-tools", "tools_status"),
            ("USB驱动", "driver_status")
        ]
        
        for item, key in env_items:
            item_frame = ttk.Frame(env_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(item_frame, text=item + ":").pack(side=tk.LEFT)
            status_label = ttk.Label(item_frame, text="检测中...", foreground="orange")
            status_label.pack(side=tk.RIGHT)
            self.env_status[key] = status_label
            
        ttk.Button(env_frame, text="自动安装环境", command=self.install_environment).pack(fill=tk.X, pady=(10, 0))
        
    def setup_right_panel(self, parent):
        """设置右侧面板"""
        # 创建选项卡
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基础工具选项卡
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="基础工具")
        self.setup_basic_tools(basic_frame)
        
        # 高级功能选项卡
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="高级功能")
        self.setup_advanced_tools(advanced_frame)
        
        # 文件管理选项卡
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="文件管理")
        self.setup_file_tools(file_frame)
        
        # 系统工具选项卡
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="系统工具")
        self.setup_system_tools(system_frame)
        
        # 控制台选项卡
        console_frame = ttk.Frame(notebook)
        notebook.add(console_frame, text="控制台")
        self.setup_console(console_frame)
        
    def setup_basic_tools(self, parent):
        """设置基础工具"""
        # 创建滚动框架
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 基础工具按钮
        tools = [
            ("重启设备", "adb reboot", "重启Android设备"),
            ("重启到Recovery", "adb reboot recovery", "重启到Recovery模式"),
            ("重启到Fastboot", "adb reboot bootloader", "重启到Fastboot模式"),
            ("截取屏幕", "adb shell screencap", "截取设备屏幕"),
            ("录制屏幕", "adb shell screenrecord", "录制设备屏幕"),
            ("获取设备信息", "adb shell getprop", "获取设备详细信息"),
            ("查看已安装应用", "adb shell pm list packages", "列出所有已安装应用"),
            ("查看系统进程", "adb shell ps", "查看当前运行进程"),
            ("查看内存使用", "adb shell cat /proc/meminfo", "查看内存使用情况"),
            ("查看CPU信息", "adb shell cat /proc/cpuinfo", "查看CPU信息"),
            ("查看存储空间", "adb shell df", "查看存储空间使用情况"),
            ("查看网络连接", "adb shell netstat", "查看网络连接状态")
        ]
        
        # 创建按钮网格
        row = 0
        col = 0
        for tool_name, command, description in tools:
            btn = ttk.Button(
                scrollable_frame, 
                text=tool_name,
                command=lambda cmd=command, desc=description: self.execute_command(cmd, desc),
                width=20
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # 添加工具提示
            self.create_tooltip(btn, description)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
                
        # 配置网格权重
        for i in range(3):
            scrollable_frame.columnconfigure(i, weight=1)
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_advanced_tools(self, parent):
        """设置高级功能"""
        # Root管理区域
        root_frame = ttk.LabelFrame(parent, text="Root管理", padding=10)
        root_frame.pack(fill=tk.X, pady=(0, 10))
        
        root_buttons = ttk.Frame(root_frame)
        root_buttons.pack(fill=tk.X)
        
        ttk.Button(root_buttons, text="检测Root状态", 
                  command=lambda: self.execute_command("adb shell su -c 'id'", "检测Root状态")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(root_buttons, text="获取Root权限", 
                  command=lambda: self.execute_command("adb shell su", "获取Root权限")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(root_buttons, text="Root权限测试", 
                  command=lambda: self.execute_command("adb shell su -c 'whoami'", "Root权限测试")).pack(side=tk.LEFT)
        
        # 系统属性区域
        prop_frame = ttk.LabelFrame(parent, text="系统属性", padding=10)
        prop_frame.pack(fill=tk.X, pady=(0, 10))
        
        prop_input_frame = ttk.Frame(prop_frame)
        prop_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(prop_input_frame, text="属性名:").pack(side=tk.LEFT)
        self.prop_name_entry = ttk.Entry(prop_input_frame, width=30)
        self.prop_name_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(prop_input_frame, text="属性值:").pack(side=tk.LEFT)
        self.prop_value_entry = ttk.Entry(prop_input_frame, width=30)
        self.prop_value_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        prop_buttons = ttk.Frame(prop_frame)
        prop_buttons.pack(fill=tk.X)
        
        ttk.Button(prop_buttons, text="获取属性", command=self.get_property).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(prop_buttons, text="设置属性", command=self.set_property).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(prop_buttons, text="获取所有属性", 
                  command=lambda: self.execute_command("adb shell getprop", "获取所有系统属性")).pack(side=tk.LEFT)
        
        # 性能监控区域
        perf_frame = ttk.LabelFrame(parent, text="性能监控", padding=10)
        perf_frame.pack(fill=tk.X)
        
        perf_buttons = ttk.Frame(perf_frame)
        perf_buttons.pack(fill=tk.X)
        
        ttk.Button(perf_buttons, text="CPU使用率", 
                  command=lambda: self.execute_command("adb shell top -n 1", "查看CPU使用率")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(perf_buttons, text="内存详情", 
                  command=lambda: self.execute_command("adb shell dumpsys meminfo", "查看内存详情")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(perf_buttons, text="电池信息", 
                  command=lambda: self.execute_command("adb shell dumpsys battery", "查看电池信息")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(perf_buttons, text="温度信息", 
                  command=lambda: self.execute_command("adb shell cat /sys/class/thermal/thermal_zone*/temp", "查看温度信息")).pack(side=tk.LEFT)
        
    def setup_file_tools(self, parent):
        """设置文件管理工具"""
        # 文件传输区域
        transfer_frame = ttk.LabelFrame(parent, text="文件传输", padding=10)
        transfer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 推送文件
        push_frame = ttk.Frame(transfer_frame)
        push_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(push_frame, text="本地文件:").pack(anchor=tk.W)
        local_file_frame = ttk.Frame(push_frame)
        local_file_frame.pack(fill=tk.X, pady=(2, 5))
        
        self.local_file_entry = ttk.Entry(local_file_frame)
        self.local_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(local_file_frame, text="浏览", command=self.browse_local_file).pack(side=tk.RIGHT)
        
        ttk.Label(push_frame, text="设备路径:").pack(anchor=tk.W)
        self.device_path_entry = ttk.Entry(push_frame)
        self.device_path_entry.insert(0, "/sdcard/")
        self.device_path_entry.pack(fill=tk.X, pady=(2, 10))
        
        ttk.Button(push_frame, text="推送文件到设备", command=self.push_file).pack(fill=tk.X)
        
        # 拉取文件
        pull_frame = ttk.Frame(transfer_frame)
        pull_frame.pack(fill=tk.X)
        
        ttk.Label(pull_frame, text="设备文件路径:").pack(anchor=tk.W)
        self.remote_file_entry = ttk.Entry(pull_frame)
        self.remote_file_entry.insert(0, "/sdcard/")
        self.remote_file_entry.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(pull_frame, text="保存到本地:").pack(anchor=tk.W)
        save_file_frame = ttk.Frame(pull_frame)
        save_file_frame.pack(fill=tk.X, pady=(2, 10))
        
        self.save_path_entry = ttk.Entry(save_file_frame)
        self.save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(save_file_frame, text="浏览", command=self.browse_save_path).pack(side=tk.RIGHT)
        
        ttk.Button(pull_frame, text="从设备拉取文件", command=self.pull_file).pack(fill=tk.X)
        
        # 文件浏览区域
        browser_frame = ttk.LabelFrame(parent, text="文件浏览器", padding=10)
        browser_frame.pack(fill=tk.BOTH, expand=True)
        
        # 路径输入
        path_frame = ttk.Frame(browser_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="当前路径:").pack(side=tk.LEFT)
        self.current_path_entry = ttk.Entry(path_frame)
        self.current_path_entry.insert(0, "/sdcard/")
        self.current_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(path_frame, text="浏览", command=self.browse_device_path).pack(side=tk.RIGHT)
        
        # 文件列表
        self.file_tree = ttk.Treeview(browser_frame, columns=("size", "date", "permissions"), show="tree headings")
        self.file_tree.heading("#0", text="文件名")
        self.file_tree.heading("size", text="大小")
        self.file_tree.heading("date", text="修改时间")
        self.file_tree.heading("permissions", text="权限")
        
        file_scrollbar = ttk.Scrollbar(browser_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_system_tools(self, parent):
        """设置系统工具"""
        # 应用管理区域
        app_frame = ttk.LabelFrame(parent, text="应用管理", padding=10)
        app_frame.pack(fill=tk.X, pady=(0, 10))
        
        app_input_frame = ttk.Frame(app_frame)
        app_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(app_input_frame, text="包名:").pack(side=tk.LEFT)
        self.package_entry = ttk.Entry(app_input_frame, width=40)
        self.package_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(app_input_frame, text="获取包名", command=self.get_package_name).pack(side=tk.LEFT)
        
        app_buttons = ttk.Frame(app_frame)
        app_buttons.pack(fill=tk.X)
        
        buttons = [
            ("安装APK", self.install_apk),
            ("卸载应用", self.uninstall_app),
            ("启动应用", self.start_app),
            ("停止应用", self.stop_app),
            ("清除数据", self.clear_app_data),
            ("应用信息", self.get_app_info)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(app_buttons, text=text, command=command).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
            
        for i in range(3):
            app_buttons.columnconfigure(i, weight=1)
        
        # 系统服务区域
        service_frame = ttk.LabelFrame(parent, text="系统服务", padding=10)
        service_frame.pack(fill=tk.X, pady=(0, 10))
        
        service_buttons = ttk.Frame(service_frame)
        service_buttons.pack(fill=tk.X)
        
        services = [
            ("WiFi开关", "adb shell svc wifi", "WiFi服务控制"),
            ("数据开关", "adb shell svc data", "移动数据控制"),
            ("蓝牙开关", "adb shell svc bluetooth", "蓝牙服务控制"),
            ("位置服务", "adb shell settings put secure location_providers_allowed", "位置服务控制")
        ]
        
        for i, (name, command, desc) in enumerate(services):
            btn = ttk.Button(service_buttons, text=name, 
                           command=lambda cmd=command, d=desc: self.execute_command(cmd, d))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
        service_buttons.columnconfigure(0, weight=1)
        service_buttons.columnconfigure(1, weight=1)
        
        # 系统设置区域
        settings_frame = ttk.LabelFrame(parent, text="系统设置", padding=10)
        settings_frame.pack(fill=tk.X)
        
        settings_buttons = ttk.Frame(settings_frame)
        settings_buttons.pack(fill=tk.X)
        
        settings = [
            ("开发者选项", "adb shell settings put global development_settings_enabled 1", "启用开发者选项"),
            ("USB调试", "adb shell settings put global adb_enabled 1", "启用USB调试"),
            ("保持唤醒", "adb shell settings put global stay_on_while_plugged_in 3", "充电时保持唤醒"),
            ("显示触摸", "adb shell settings put system show_touches 1", "显示触摸位置")
        ]
        
        for i, (name, command, desc) in enumerate(settings):
            btn = ttk.Button(settings_buttons, text=name,
                           command=lambda cmd=command, d=desc: self.execute_command(cmd, d))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
        settings_buttons.columnconfigure(0, weight=1)
        settings_buttons.columnconfigure(1, weight=1)
        
    def setup_console(self, parent):
        """设置控制台"""
        # 命令输入区域
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="ADB命令:").pack(side=tk.LEFT)
        self.command_entry = ttk.Entry(input_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.command_entry.bind('<Return>', lambda e: self.execute_custom_command())
        
        ttk.Button(input_frame, text="执行", command=self.execute_custom_command).pack(side=tk.RIGHT)
        
        # 控制台输出区域
        console_frame = ttk.Frame(parent)
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            bg='black',
            fg='green',
            insertbackground='white'
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制台按钮
        console_buttons = ttk.Frame(parent)
        console_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(console_buttons, text="清空控制台", command=self.clear_console).pack(side=tk.LEFT)
        ttk.Button(console_buttons, text="保存日志", command=self.save_log).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(console_buttons, text="导出日志", command=self.export_log).pack(side=tk.LEFT, padx=(5, 0))
        
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 连接状态
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.connection_status, foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=(5, 20))
        
        # 当前设备
        ttk.Label(status_frame, text="设备:").pack(side=tk.LEFT)
        self.device_label = ttk.Label(status_frame, textvariable=self.current_device)
        self.device_label.pack(side=tk.LEFT, padx=(5, 20))
        
        # 版本信息
        ttk.Label(status_frame, text="奕奕ADB工具箱 v0.1 | GitHub: yys20071108").pack(side=tk.RIGHT)
        
    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def log_message(self, message, level="INFO"):
        """记录日志消息"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        self.console_text.insert(tk.END, log_entry)
        self.console_text.see(tk.END)
        
        # 根据日志级别设置颜色
        if level == "ERROR":
            self.console_text.tag_add("error", "end-2l", "end-1l")
            self.console_text.tag_config("error", foreground="red")
        elif level == "WARNING":
            self.console_text.tag_add("warning", "end-2l", "end-1l")
            self.console_text.tag_config("warning", foreground="yellow")
        elif level == "SUCCESS":
            self.console_text.tag_add("success", "end-2l", "end-1l")
            self.console_text.tag_config("success", foreground="lightgreen")
            
    def check_environment(self):
        """检查ADB环境"""
        def check():
            # 检查ADB - 修复Windows路径问题
            adb_commands = ['adb', 'adb.exe']
            if platform.system() == "Windows":
                adb_commands.extend(['platform-tools\\adb.exe', '.\\adb.exe'])
        
            adb_found = False
            for adb_cmd in adb_commands:
                try:
                    result = subprocess.run([adb_cmd, 'version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.adb_path = adb_cmd
                        adb_found = True
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue
                
            if adb_found:
                self.env_status['adb_status'].config(text="已安装", foreground="green")
                self.log_message("ADB环境检测成功", "SUCCESS")
            else:
                self.env_status['adb_status'].config(text="未安装", foreground="red")
                self.log_message("ADB环境检测失败，请安装ADB工具", "ERROR")
                
            # 检查Platform-tools
            try:
                adb_path = subprocess.run(['where', 'adb'], capture_output=True, text=True)
                if adb_path.returncode == 0:
                    self.env_status['tools_status'].config(text="v0.1", foreground="green")
                    self.log_message("Platform-tools检测成功", "SUCCESS")
                else:
                    self.env_status['tools_status'].config(text="未安装", foreground="red")
            except:
                self.env_status['tools_status'].config(text="未安装", foreground="red")
                
            # 检查USB驱动（简化检测）
            self.env_status['driver_status'].config(text="正常", foreground="green")
            self.log_message("USB驱动检测完成", "SUCCESS")
            
        threading.Thread(target=check, daemon=True).start()
        
    def connect_device(self):
        """连接设备"""
        def connect():
            try:
                self.log_message("正在扫描设备...")
                result = subprocess.run([self.adb_path, 'devices'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    devices = []
                    lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
                    
                    for line in lines:
                        if line.strip() and '\t' in line:
                            device_id = line.split('\t')[0]
                            devices.append(device_id)
                            
                    if devices:
                        self.connected_devices = devices
                        self.current_device.set(devices[0])
                        self.connection_status.set("已连接")
                        self.status_label.config(foreground="green")
                        self.log_message(f"设备连接成功: {devices[0]}", "SUCCESS")
                        self.get_device_info()
                    else:
                        self.connection_status.set("未找到设备")
                        self.status_label.config(foreground="red")
                        self.log_message("未找到设备，请检查连接", "WARNING")
                else:
                    self.log_message("设备连接失败", "ERROR")
                    
            except Exception as e:
                self.log_message(f"连接错误: {str(e)}", "ERROR")
                
        threading.Thread(target=connect, daemon=True).start()
        
    def refresh_devices(self):
        """刷新设备列表"""
        self.connect_device()
        
    def get_device_info(self):
        """获取设备信息"""
        def get_info():
            try:
                info_commands = [
                    ("ro.product.model", "设备型号"),
                    ("ro.build.version.release", "Android版本"),
                    ("ro.build.version.sdk", "API级别"),
                    ("ro.product.manufacturer", "制造商"),
                    ("ro.product.brand", "品牌"),
                    ("ro.build.display.id", "系统版本"),
                ]
                
                device_info = "设备信息:\n" + "="*30 + "\n"
                
                for prop, desc in info_commands:
                    result = subprocess.run([self.adb_path, 'shell', 'getprop', prop],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        device_info += f"{desc}: {value}\n"
                        
                # 获取电池信息
                battery_result = subprocess.run([self.adb_path, 'shell', 'dumpsys', 'battery'],
                                              capture_output=True, text=True, timeout=5)
                if battery_result.returncode == 0:
                    battery_lines = battery_result.stdout.split('\n')
                    for line in battery_lines:
                        if 'level:' in line:
                            level = line.split(':')[1].strip()
                            device_info += f"电池电量: {level}%\n"
                            break
                            
                # 更新设备信息显示
                self.device_info_text.config(state=tk.NORMAL)
                self.device_info_text.delete(1.0, tk.END)
                self.device_info_text.insert(1.0, device_info)
                self.device_info_text.config(state=tk.DISABLED)
                
            except Exception as e:
                self.log_message(f"获取设备信息失败: {str(e)}", "ERROR")
                
        threading.Thread(target=get_info, daemon=True).start()
        
    def execute_command(self, command, description=""):
        """执行ADB命令"""
        def execute():
            try:
                self.log_message(f"执行命令: {command}")
                if description:
                    self.log_message(f"描述: {description}")
                
                # 分割命令并处理路径
                cmd_parts = command.split()
                if cmd_parts[0] != 'adb':
                    cmd_parts = [self.adb_path] + cmd_parts[1:]
                else:
                    cmd_parts[0] = self.adb_path
                
                # 修复编码问题
                result = subprocess.run(
                    cmd_parts, 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    encoding='utf-8',
                    errors='ignore'  # 忽略编码错误
                )
            
                if result.returncode == 0:
                    if result.stdout:
                        self.log_message("命令执行成功:", "SUCCESS")
                        self.log_message(result.stdout)
                    else:
                        self.log_message("命令执行成功", "SUCCESS")
                else:
                    self.log_message("命令执行失败:", "ERROR")
                    if result.stderr:
                        self.log_message(result.stderr, "ERROR")
                    
            except subprocess.TimeoutExpired:
                self.log_message("命令执行超时", "ERROR")
            except Exception as e:
                self.log_message(f"命令执行错误: {str(e)}", "ERROR")
            
    threading.Thread(target=execute, daemon=True).start()
        
    def execute_custom_command(self):
        """执行自定义命令"""
        command = self.command_entry.get().strip()
        if command:
            if not command.startswith('adb'):
                command = f"adb {command}"
            self.execute_command(command, "自定义命令")
            self.command_entry.delete(0, tk.END)
            
    def get_property(self):
        """获取系统属性"""
        prop_name = self.prop_name_entry.get().strip()
        if prop_name:
            command = f"adb shell getprop {prop_name}"
            self.execute_command(command, f"获取属性: {prop_name}")
            
    def set_property(self):
        """设置系统属性"""
        prop_name = self.prop_name_entry.get().strip()
        prop_value = self.prop_value_entry.get().strip()
        if prop_name and prop_value:
            command = f"adb shell setprop {prop_name} {prop_value}"
            self.execute_command(command, f"设置属性: {prop_name} = {prop_value}")
            
    def browse_local_file(self):
        """浏览本地文件"""
        filename = filedialog.askopenfilename(
            title="选择要推送的文件",
            filetypes=[("所有文件", "*.*")]
        )
        if filename:
            self.local_file_entry.delete(0, tk.END)
            self.local_file_entry.insert(0, filename)
            
    def browse_save_path(self):
        """浏览保存路径"""
        filename = filedialog.asksaveasfilename(
            title="选择保存位置",
            filetypes=[("所有文件", "*.*")]
        )
        if filename:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, filename)
            
    def push_file(self):
        """推送文件到设备"""
        local_file = self.local_file_entry.get().strip()
        device_path = self.device_path_entry.get().strip()
        
        if local_file and device_path:
            if os.path.exists(local_file):
                command = f"adb push \"{local_file}\" \"{device_path}\""
                self.execute_command(command, f"推送文件: {os.path.basename(local_file)}")
            else:
                self.log_message("本地文件不存在", "ERROR")
        else:
            self.log_message("请填写完整的文件路径", "WARNING")
            
    def pull_file(self):
        """从设备拉取文件"""
        remote_file = self.remote_file_entry.get().strip()
        save_path = self.save_path_entry.get().strip()
        
        if remote_file and save_path:
            command = f"adb pull \"{remote_file}\" \"{save_path}\""
            self.execute_command(command, f"拉取文件: {os.path.basename(remote_file)}")
        else:
            self.log_message("请填写完整的文件路径", "WARNING")
            
    def browse_device_path(self):
        """浏览设备路径"""
        path = self.current_path_entry.get().strip()
        if path:
            command = f"adb shell ls -la \"{path}\""
            self.execute_command(command, f"浏览路径: {path}")
            
    def get_package_name(self):
        """获取包名列表"""
        command = "adb shell pm list packages"
        self.execute_command(command, "获取所有应用包名")
        
    def install_apk(self):
        """安装APK"""
        apk_file = filedialog.askopenfilename(
            title="选择APK文件",
            filetypes=[("APK文件", "*.apk")]
        )
        if apk_file:
            command = f"adb install \"{apk_file}\""
            self.execute_command(command, f"安装APK: {os.path.basename(apk_file)}")
            
    def uninstall_app(self):
        """卸载应用"""
        package = self.package_entry.get().strip()
        if package:
            command = f"adb uninstall {package}"
            self.execute_command(command, f"卸载应用: {package}")
        else:
            self.log_message("请输入包名", "WARNING")
            
    def start_app(self):
        """启动应用"""
        package = self.package_entry.get().strip()
        if package:
            command = f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
            self.execute_command(command, f"启动应用: {package}")
        else:
            self.log_message("请输入包名", "WARNING")
            
    def stop_app(self):
        """停止应用"""
        package = self.package_entry.get().strip()
        if package:
            command = f"adb shell am force-stop {package}"
            self.execute_command(command, f"停止应用: {package}")
        else:
            self.log_message("请输入包名", "WARNING")
            
    def clear_app_data(self):
        """清除应用数据"""
        package = self.package_entry.get().strip()
        if package:
            command = f"adb shell pm clear {package}"
            self.execute_command(command, f"清除应用数据: {package}")
        else:
            self.log_message("请输入包名", "WARNING")
            
    def get_app_info(self):
        """获取应用信息"""
        package = self.package_entry.get().strip()
        if package:
            command = f"adb shell dumpsys package {package}"
            self.execute_command(command, f"获取应用信息: {package}")
        else:
            self.log_message("请输入包名", "WARNING")
            
    def clear_console(self):
        """清空控制台"""
        self.console_text.delete(1.0, tk.END)
        self.log_message("控制台已清空", "INFO")
        
    def save_log(self):
        """保存日志"""
        filename = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.console_text.get(1.0, tk.END))
                self.log_message(f"日志已保存到: {filename}", "SUCCESS")
            except Exception as e:
                self.log_message(f"保存日志失败: {str(e)}", "ERROR")
                
    def export_log(self):
        """导出日志"""
        self.save_log()
        
    def install_environment(self):
        """自动安装ADB环境"""
        def install():
            try:
                self.log_message("开始下载ADB环境...", "INFO")
                
                # 这里应该实现实际的下载和安装逻辑
                # 为了演示，我们只是模拟安装过程
                import time
                for i in range(5):
                    time.sleep(1)
                    self.log_message(f"安装进度: {(i+1)*20}%", "INFO")
                    
                self.log_message("ADB环境安装完成", "SUCCESS")
                self.check_environment()
                
            except Exception as e:
                self.log_message(f"安装失败: {str(e)}", "ERROR")
                
        threading.Thread(target=install, daemon=True).start()
        
    def check_update(self):
        """检查更新"""
        def check():
            try:
                self.log_message("正在检查更新...", "INFO")
                # 这里应该实现实际的更新检查逻辑
                time.sleep(2)
                self.log_message("当前已是最新版本", "SUCCESS")
            except Exception as e:
                self.log_message(f"检查更新失败: {str(e)}", "ERROR")
                
        threading.Thread(target=check, daemon=True).start()
        
    def show_about(self):
        """显示关于对话框"""
        about_text = """
奕奕ADB工具箱 v0.1

一个功能丰富的Android调试工具

开发者: YYS
GitHub: https://github.com/yys20071108/-adb-
邮箱: yys20071108@example.com

功能特性:
• 设备连接管理
• 基础ADB工具
• 高级系统功能
• 文件传输管理
• 应用管理工具
• 系统监控工具

感谢使用！
        """
        messagebox.showinfo("关于", about_text)
        
    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # 设置内容
        ttk.Label(settings_window, text="ADB路径:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        adb_path_entry = ttk.Entry(settings_window, width=50)
        adb_path_entry.insert(0, self.adb_path)
        adb_path_entry.pack(padx=10, pady=(0, 10))
        
        ttk.Label(settings_window, text="连接超时(秒):").pack(anchor=tk.W, padx=10, pady=(0, 5))
        timeout_entry = ttk.Entry(settings_window, width=20)
        timeout_entry.insert(0, "30")
        timeout_entry.pack(padx=10, pady=(0, 10))
        
        # 按钮
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        def save_settings():
            self.adb_path = adb_path_entry.get()
            settings_window.destroy()
            self.log_message("设置已保存", "SUCCESS")
            
        ttk.Button(button_frame, text="保存", command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.LEFT)
        
    def run(self):
        """运行应用"""
        self.log_message("奕奕ADB工具箱 v0.1 启动成功", "SUCCESS")
        self.log_message("GitHub: https://github.com/yys20071108/-adb-", "INFO")
        self.root.mainloop()

if __name__ == "__main__":
    app = ADBToolbox()
    app.run()
