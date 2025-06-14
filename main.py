#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱 v0.1.1
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
import re
import tempfile
import shutil
import urllib.request
import ctypes
from functools import partial

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

# 尝试导入ttkthemes
try:
    from ttkthemes import ThemedTk, ThemedStyle
    THEMED_TK_AVAILABLE = True
except ImportError:
    THEMED_TK_AVAILABLE = False
    print("警告: ttkthemes未安装，将使用默认主题")

# 尝试导入ttkbootstrap
try:
    import ttkbootstrap as ttb
    from ttkbootstrap.constants import *
    BOOTSTRAP_AVAILABLE = True
except ImportError:
    BOOTSTRAP_AVAILABLE = False
    print("警告: ttkbootstrap未安装，将使用默认主题")

class ADBToolbox:
    def __init__(self):
        # 初始化主窗口
        if BOOTSTRAP_AVAILABLE:
            self.root = ttb.Window(
                title="奕奕ADB工具箱 v0.1.1",
                themename="cosmo",
                size=(1200, 800),
                minsize=(1000, 600),
                resizable=(True, True)
            )
            self.style = self.root.style
        elif THEMED_TK_AVAILABLE:
            self.root = ThemedTk(theme="arc")
            self.root.title("奕奕ADB工具箱 v0.1.1")
            self.root.geometry("1200x800")
            self.root.minsize(1000, 600)
            self.style = ThemedStyle(self.root)
        else:
            self.root = tk.Tk()
            self.root.title("奕奕ADB工具箱 v0.1.1")
            self.root.geometry("1200x800")
            self.root.minsize(1000, 600)
            self.style = ttk.Style()
            
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.check_environment()
        
    def setup_window(self):
        """设置主窗口"""
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
        
        # 设置样式
        if not BOOTSTRAP_AVAILABLE and not THEMED_TK_AVAILABLE:
            self.style.configure('TButton', font=('Arial', 10))
            self.style.configure('TLabel', font=('Arial', 10))
            self.style.configure('TFrame', background='#f0f0f0')
            
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
        self.platform_tools_dir = None
        self.is_admin = self.check_admin()
        self.connection_type = tk.StringVar(value="USB连接")
        self.auto_refresh = tk.BooleanVar(value=False)
        self.auto_refresh_thread = None
        self.auto_refresh_running = False
        self.device_info_cache = {}
        self.last_command = None
        self.command_history = []
        self.history_index = 0
        self.settings = self.load_settings()
        
    def check_admin(self):
        """检查是否以管理员权限运行"""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
        
    def load_settings(self):
        """加载设置"""
        settings_file = os.path.join(os.path.expanduser("~"), ".yys_adb_toolbox.json")
        default_settings = {
            "adb_path": "adb",
            "timeout": 30,
            "theme": "cosmo" if BOOTSTRAP_AVAILABLE else "arc" if THEMED_TK_AVAILABLE else "default",
            "auto_check_update": True,
            "auto_connect": True,
            "last_wifi_ip": "192.168.1.100",
            "last_wifi_port": "5555",
            "recent_devices": [],
            "recent_files": [],
            "custom_commands": []
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 合并默认设置和加载的设置
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception as e:
            print(f"加载设置失败: {e}")
            
        return default_settings
    
    def save_settings(self):
        """保存设置"""
        settings_file = os.path.join(os.path.expanduser("~"), ".yys_adb_toolbox.json")
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
            
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
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        """关闭窗口时的处理"""
        # 停止自动刷新线程
        self.auto_refresh_running = False
        if self.auto_refresh_thread and self.auto_refresh_thread.is_alive():
            self.auto_refresh_thread.join(1)
            
        # 保存设置
        self.save_settings()
        
        # 关闭窗口
        self.root.destroy()
        
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 标题和版本
        title_frame = ttk.Frame(toolbar)
        title_frame.pack(side=tk.LEFT)
        
        # 加载logo
        try:
            logo_path = self.resource_path("assets/logo.png")
            if os.path.exists(logo_path) and PIL_AVAILABLE:
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((32, 32), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(title_frame, image=logo_photo)
                logo_label.image = logo_photo
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"加载logo失败: {e}")
        
        title_label = ttk.Label(title_frame, text="奕奕ADB工具箱", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(title_frame, text="v0.1.1", font=('Arial', 10))
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 右侧按钮
        button_frame = ttk.Frame(toolbar)
        button_frame.pack(side=tk.RIGHT)
        
        # 使用更现代的按钮样式
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="检查更新", bootstyle="info-outline", command=self.check_update).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="关于", bootstyle="secondary-outline", command=self.show_about).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="设置", bootstyle="primary-outline", command=self.show_settings).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="帮助", bootstyle="success-outline", command=self.show_help).pack(side=tk.RIGHT, padx=(5, 0))
        else:
            ttk.Button(button_frame, text="检查更新", command=self.check_update).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="关于", command=self.show_about).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="设置", command=self.show_settings).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="帮助", command=self.show_help).pack(side=tk.RIGHT, padx=(5, 0))
        
    def setup_left_panel(self, parent):
        """设置左侧面板"""
        # 设备连接区域
        connection_frame = ttk.LabelFrame(parent, text="设备连接", padding=10)
        connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接方式选择
        ttk.Label(connection_frame, text="连接方式:").pack(anchor=tk.W)
        connection_type_combo = ttk.Combobox(connection_frame, textvariable=self.connection_type, 
                                           values=["USB连接", "WiFi连接"], state="readonly")
        connection_type_combo.pack(fill=tk.X, pady=(5, 10))
        connection_type_combo.bind("<<ComboboxSelected>>", self.on_connection_type_changed)
        
        # WiFi连接设置
        self.wifi_frame = ttk.Frame(connection_frame)
        
        ttk.Label(self.wifi_frame, text="IP地址:").pack(anchor=tk.W)
        self.ip_entry = ttk.Entry(self.wifi_frame)
        self.ip_entry.insert(0, self.settings.get("last_wifi_ip", "192.168.1.100"))
        self.ip_entry.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(self.wifi_frame, text="端口:").pack(anchor=tk.W)
        self.port_entry = ttk.Entry(self.wifi_frame)
        self.port_entry.insert(0, self.settings.get("last_wifi_port", "5555"))
        self.port_entry.pack(fill=tk.X, pady=(2, 10))
        
        # 设备选择下拉框
        ttk.Label(connection_frame, text="设备选择:").pack(anchor=tk.W)
        self.device_combo = ttk.Combobox(connection_frame, textvariable=self.current_device, state="readonly")
        self.device_combo.pack(fill=tk.X, pady=(5, 10))
        self.device_combo.bind("<<ComboboxSelected>>", self.on_device_selected)
        
        # 自动刷新选项
        auto_refresh_frame = ttk.Frame(connection_frame)
        auto_refresh_frame.pack(fill=tk.X, pady=(0, 10))
        
        auto_refresh_check = ttk.Checkbutton(auto_refresh_frame, text="自动刷新设备列表", 
                                           variable=self.auto_refresh, command=self.toggle_auto_refresh)
        auto_refresh_check.pack(side=tk.LEFT)
        
        # 连接按钮
        button_frame = ttk.Frame(connection_frame)
        button_frame.pack(fill=tk.X)
        
        if BOOTSTRAP_AVAILABLE:
            self.connect_btn = ttk.Button(button_frame, text="连接设备", bootstyle="success", 
                                        command=self.connect_device)
            self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            ttk.Button(button_frame, text="刷新", bootstyle="info", 
                     command=self.refresh_devices).pack(side=tk.RIGHT)
        else:
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
        
        # 安装环境按钮
        button_frame = ttk.Frame(env_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="自动安装环境", bootstyle="warning", 
                     command=self.install_environment).pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(button_frame, text="修复ADB", bootstyle="danger", 
                     command=self.fix_adb).pack(side=tk.RIGHT, padx=(5, 0))
        else:
            ttk.Button(button_frame, text="自动安装环境", 
                     command=self.install_environment).pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(button_frame, text="修复ADB", 
                     command=self.fix_adb).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 初始隐藏WiFi设置
        if self.connection_type.get() == "USB连接":
            self.wifi_frame.pack_forget()
        else:
            self.wifi_frame.pack(fill=tk.X, pady=(0, 10))
        
    def on_connection_type_changed(self, event):
        """连接方式改变时的处理"""
        if self.connection_type.get() == "USB连接":
            self.wifi_frame.pack_forget()
        else:
            self.wifi_frame.pack(fill=tk.X, pady=(0, 10))
            
    def on_device_selected(self, event):
        """设备选择改变时的处理"""
        selected_device = self.current_device.get()
        if selected_device:
            self.get_device_info()
            
    def toggle_auto_refresh(self):
        """切换自动刷新状态"""
        if self.auto_refresh.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
            
    def start_auto_refresh(self):
        """开始自动刷新"""
        if not self.auto_refresh_running:
            self.auto_refresh_running = True
            self.auto_refresh_thread = threading.Thread(target=self.auto_refresh_task, daemon=True)
            self.auto_refresh_thread.start()
            
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.auto_refresh_running = False
        
    def auto_refresh_task(self):
        """自动刷新任务"""
        while self.auto_refresh_running:
            self.refresh_devices()
            time.sleep(5)  # 每5秒刷新一次
        
    def setup_right_panel(self, parent):
        """设置右侧面板"""
        # 创建选项卡
        if BOOTSTRAP_AVAILABLE:
            notebook = ttb.Notebook(parent)
        else:
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
        
        # 快捷命令选项卡
        quick_frame = ttk.Frame(notebook)
        notebook.add(quick_frame, text="快捷命令")
        self.setup_quick_commands(quick_frame)
        
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
            ("截取屏幕", "adb shell screencap -p /sdcard/screenshot.png && adb pull /sdcard/screenshot.png", "截取设备屏幕"),
            ("录制屏幕", "adb shell screenrecord /sdcard/screenrecord.mp4", "录制设备屏幕"),
            ("获取设备信息", "adb shell getprop", "获取设备详细信息"),
            ("查看已安装应用", "adb shell pm list packages", "列出所有已安装应用"),
            ("查看系统进程", "adb shell ps", "查看当前运行进程"),
            ("查看内存使用", "adb shell cat /proc/meminfo", "查看内存使用情况"),
            ("查看CPU信息", "adb shell cat /proc/cpuinfo", "查看CPU信息"),
            ("查看存储空间", "adb shell df", "查看存储空间使用情况"),
            ("查看网络连接", "adb shell netstat", "查看网络连接状态"),
            ("查看电池信息", "adb shell dumpsys battery", "查看电池信息"),
            ("查看WiFi信息", "adb shell dumpsys wifi", "查看WiFi信息"),
            ("查看蓝牙信息", "adb shell dumpsys bluetooth_manager", "查看蓝牙信息")
        ]
        
        # 创建按钮网格
        row = 0
        col = 0
        for tool_name, command, description in tools:
            if BOOTSTRAP_AVAILABLE:
                btn = ttb.Button(
                    scrollable_frame, 
                    text=tool_name,
                    command=lambda cmd=command, desc=description: self.execute_command(cmd, desc),
                    width=20,
                    bootstyle="info-outline"
                )
            else:
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(root_buttons, text="检测Root状态", bootstyle="info-outline",
                     command=lambda: self.execute_command("adb shell su -c 'id'", "检测Root状态")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(root_buttons, text="获取Root权限", bootstyle="warning-outline",
                     command=lambda: self.execute_command("adb shell su", "获取Root权限")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(root_buttons, text="Root权限测试", bootstyle="success-outline",
                     command=lambda: self.execute_command("adb shell su -c 'whoami'", "Root权限测试")).pack(side=tk.LEFT)
        else:
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(prop_buttons, text="获取属性", bootstyle="info", 
                     command=self.get_property).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(prop_buttons, text="设置属性", bootstyle="warning", 
                     command=self.set_property).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(prop_buttons, text="获取所有属性", bootstyle="secondary", 
                     command=lambda: self.execute_command("adb shell getprop", "获取所有系统属性")).pack(side=tk.LEFT)
        else:
            ttk.Button(prop_buttons, text="获取属性", 
                     command=self.get_property).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(prop_buttons, text="设置属性", 
                     command=self.set_property).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(prop_buttons, text="获取所有属性", 
                     command=lambda: self.execute_command("adb shell getprop", "获取所有系统属性")).pack(side=tk.LEFT)
        
        # 性能监控区域
        perf_frame = ttk.LabelFrame(parent, text="性能监控", padding=10)
        perf_frame.pack(fill=tk.X)
        
        perf_buttons = ttk.Frame(perf_frame)
        perf_buttons.pack(fill=tk.X)
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(perf_buttons, text="CPU使用率", bootstyle="info-outline",
                     command=lambda: self.execute_command("adb shell top -n 1", "查看CPU使用率")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(perf_buttons, text="内存详情", bootstyle="info-outline",
                     command=lambda: self.execute_command("adb shell dumpsys meminfo", "查看内存详情")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(perf_buttons, text="电池信息", bootstyle="info-outline",
                     command=lambda: self.execute_command("adb shell dumpsys battery", "查看电池信息")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(perf_buttons, text="温度信息", bootstyle="info-outline",
                     command=lambda: self.execute_command("adb shell cat /sys/class/thermal/thermal_zone*/temp", "查看温度信息")).pack(side=tk.LEFT)
        else:
            ttk.Button(perf_buttons, text="CPU使用率", 
                     command=lambda: self.execute_command("adb shell top -n 1", "查看CPU使用率")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(perf_buttons, text="内存详情", 
                     command=lambda: self.execute_command("adb shell dumpsys meminfo", "查看内存详情")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(perf_buttons, text="电池信息", 
                     command=lambda: self.execute_command("adb shell dumpsys battery", "查看电池信息")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(perf_buttons, text="温度信息", 
                     command=lambda: self.execute_command("adb shell cat /sys/class/thermal/thermal_zone*/temp", "查看温度信息")).pack(side=tk.LEFT)
        
        # 无线调试区域
        wireless_frame = ttk.LabelFrame(parent, text="无线调试", padding=10)
        wireless_frame.pack(fill=tk.X, pady=(10, 0))
        
        wireless_buttons = ttk.Frame(wireless_frame)
        wireless_buttons.pack(fill=tk.X)
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(wireless_buttons, text="启用无线调试", bootstyle="success-outline",
                     command=self.enable_wireless_debug).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(wireless_buttons, text="配对设备", bootstyle="info-outline",
                     command=self.pair_wireless_device).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(wireless_buttons, text="断开无线连接", bootstyle="danger-outline",
                     command=self.disconnect_wireless).pack(side=tk.LEFT)
        else:
            ttk.Button(wireless_buttons, text="启用无线调试", 
                     command=self.enable_wireless_debug).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(wireless_buttons, text="配对设备", 
                     command=self.pair_wireless_device).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(wireless_buttons, text="断开无线连接", 
                     command=self.disconnect_wireless).pack(side=tk.LEFT)
        
    def enable_wireless_debug(self):
        """启用无线调试"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先通过USB连接设备")
            return
            
        # 获取设备IP地址
        self.log_message("正在获取设备IP地址...")
        result = subprocess.run([self.adb_path, 'shell', 'ip', 'addr', 'show', 'wlan0'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            # 使用正则表达式提取IP地址
            ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if ip_match:
                ip_address = ip_match.group(1)
                self.log_message(f"设备IP地址: {ip_address}", "INFO")
                
                # 设置端口
                port = "5555"
                
                # 启用TCP/IP模式
                self.execute_command(f"adb tcpip {port}", "启用TCP/IP模式")
                
                # 更新WiFi连接设置
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, ip_address)
                self.port_entry.delete(0, tk.END)
                self.port_entry.insert(0, port)
                
                # 保存设置
                self.settings["last_wifi_ip"] = ip_address
                self.settings["last_wifi_port"] = port
                
                # 提示用户
                self.log_message(f"无线调试已启用，可以断开USB线并使用WiFi连接", "SUCCESS")
                self.log_message(f"连接命令: adb connect {ip_address}:{port}", "INFO")
                
                # 切换到WiFi连接模式
                self.connection_type.set("WiFi连接")
                self.on_connection_type_changed(None)
            else:
                self.log_message("未能获取设备IP地址", "ERROR")
        else:
            self.log_message("获取设备IP地址失败", "ERROR")
            
    def pair_wireless_device(self):
        """配对无线设备"""
        # 创建配对对话框
        pair_dialog = tk.Toplevel(self.root)
        pair_dialog.title("无线配对")
        pair_dialog.geometry("400x300")
        pair_dialog.resizable(False, False)
        pair_dialog.transient(self.root)
        pair_dialog.grab_set()
        
        # 配对说明
        ttk.Label(pair_dialog, text="Android 11+无线调试配对", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        ttk.Label(pair_dialog, text="请在设备上启用开发者选项中的无线调试功能").pack(pady=(0, 5))
        ttk.Label(pair_dialog, text="然后点击'使用配对码配对设备'选项").pack(pady=(0, 10))
        
        # 配对信息输入
        input_frame = ttk.Frame(pair_dialog)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(input_frame, text="IP地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ip_entry = ttk.Entry(input_frame, width=30)
        ip_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        ip_entry.insert(0, self.ip_entry.get())
        
        ttk.Label(input_frame, text="端口:").grid(row=1, column=0, sticky=tk.W, pady=5)
        port_entry = ttk.Entry(input_frame, width=30)
        port_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(input_frame, text="配对码:").grid(row=2, column=0, sticky=tk.W, pady=5)
        code_entry = ttk.Entry(input_frame, width=30)
        code_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 配对按钮
        button_frame = ttk.Frame(pair_dialog)
        button_frame.pack(pady=20)
        
        def do_pair():
            ip = ip_entry.get().strip()
            port = port_entry.get().strip()
            code = code_entry.get().strip()
            
            if not ip or not port or not code:
                messagebox.showwarning("警告", "请填写完整的配对信息", parent=pair_dialog)
                return
                
            # 执行配对命令
            try:
                self.log_message(f"正在配对设备: {ip}:{port} 配对码: {code}")
                result = subprocess.run([self.adb_path, 'pair', f"{ip}:{port}", code], 
                                      capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if "Successfully paired" in result.stdout:
                    self.log_message("设备配对成功", "SUCCESS")
                    messagebox.showinfo("成功", "设备配对成功！\n现在可以使用WiFi连接设备", parent=pair_dialog)
                    pair_dialog.destroy()
                else:
                    self.log_message(f"配对失败: {result.stdout}", "ERROR")
                    messagebox.showerror("错误", f"配对失败: {result.stdout}", parent=pair_dialog)
            except Exception as e:
                self.log_message(f"配对错误: {str(e)}", "ERROR")
                messagebox.showerror("错误", f"配对错误: {str(e)}", parent=pair_dialog)
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="配对", bootstyle="success", command=do_pair).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", bootstyle="secondary", command=pair_dialog.destroy).pack(side=tk.LEFT)
        else:
            ttk.Button(button_frame, text="配对", command=do_pair).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", command=pair_dialog.destroy).pack(side=tk.LEFT)
            
    def disconnect_wireless(self):
        """断开无线连接"""
        if self.connection_type.get() == "WiFi连接":
            ip = self.ip_entry.get().strip()
            port = self.port_entry.get().strip()
            
            if ip and port:
                self.execute_command(f"adb disconnect {ip}:{port}", "断开无线连接")
                self.refresh_devices()
            else:
                self.log_message("请输入有效的IP地址和端口", "WARNING")
        else:
            self.log_message("当前不是WiFi连接模式", "WARNING")
        
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(push_frame, text="推送文件到设备", bootstyle="success", 
                     command=self.push_file).pack(fill=tk.X)
        else:
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(pull_frame, text="从设备拉取文件", bootstyle="info", 
                     command=self.pull_file).pack(fill=tk.X)
        else:
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(path_frame, text="浏览", bootstyle="info-outline", 
                     command=self.browse_device_path).pack(side=tk.RIGHT)
        else:
            ttk.Button(path_frame, text="浏览", command=self.browse_device_path).pack(side=tk.RIGHT)
        
        # 文件列表
        file_frame = ttk.Frame(browser_frame)
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_tree = ttk.Treeview(file_frame, columns=("size", "date", "permissions"), show="tree headings")
        self.file_tree.heading("#0", text="文件名")
        self.file_tree.heading("size", text="大小")
        self.file_tree.heading("date", text="修改时间")
        self.file_tree.heading("permissions", text="权限")
        
        self.file_tree.column("#0", width=250)
        self.file_tree.column("size", width=100)
        self.file_tree.column("date", width=150)
        self.file_tree.column("permissions", width=100)
        
        file_scrollbar_y = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        file_scrollbar_x = ttk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=file_scrollbar_y.set, xscrollcommand=file_scrollbar_x.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        file_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 文件操作按钮
        file_buttons = ttk.Frame(browser_frame)
        file_buttons.pack(fill=tk.X, pady=(10, 0))
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(file_buttons, text="刷新", bootstyle="info-outline", 
                     command=self.refresh_file_list).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(file_buttons, text="新建文件夹", bootstyle="success-outline", 
                     command=self.create_folder).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(file_buttons, text="删除", bootstyle="danger-outline", 
                     command=self.delete_file).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(file_buttons, text="重命名", bootstyle="warning-outline", 
                     command=self.rename_file).pack(side=tk.LEFT)
        else:
            ttk.Button(file_buttons, text="刷新", command=self.refresh_file_list).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(file_buttons, text="新建文件夹", command=self.create_folder).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(file_buttons, text="删除", command=self.delete_file).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(file_buttons, text="重命名", command=self.rename_file).pack(side=tk.LEFT)
        
        # 绑定双击事件
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        
        # 绑定右键菜单
        self.create_file_context_menu()
        
    def create_file_context_menu(self):
        """创建文件右键菜单"""
        self.file_menu = tk.Menu(self.root, tearoff=0)
        self.file_menu.add_command(label="打开", command=self.open_file)
        self.file_menu.add_command(label="下载", command=self.download_file)
        self.file_menu.add_command(label="删除", command=self.delete_file)
        self.file_menu.add_command(label="重命名", command=self.rename_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="属性", command=self.show_file_properties)
        
        self.file_tree.bind("<Button-3>", self.show_file_menu)
        
    def show_file_menu(self, event):
        """显示文件右键菜单"""
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.file_menu.post(event.x_root, event.y_root)
            
    def on_file_double_click(self, event):
        """文件双击事件"""
        item = self.file_tree.selection()[0]
        item_text = self.file_tree.item(item, "text")
        current_path = self.current_path_entry.get().strip()
        
        # 如果是目录，则进入该目录
        if item_text.endswith("/"):
            new_path = os.path.join(current_path, item_text).replace("\\", "/")
            self.current_path_entry.delete(0, tk.END)
            self.current_path_entry.insert(0, new_path)
            self.browse_device_path()
        else:
            # 如果是文件，则显示文件属性
            self.show_file_properties()
            
    def refresh_file_list(self):
        """刷新文件列表"""
        self.browse_device_path()
        
    def create_folder(self):
        """创建文件夹"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 创建对话框
        folder_name = tk.simpledialog.askstring("新建文件夹", "请输入文件夹名称:")
        if folder_name:
            current_path = self.current_path_entry.get().strip()
            folder_path = os.path.join(current_path, folder_name).replace("\\", "/")
            
            self.execute_command(f"adb shell mkdir -p \"{folder_path}\"", f"创建文件夹: {folder_name}")
            self.refresh_file_list()
            
    def delete_file(self):
        """删除文件"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 获取选中的文件
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的文件或文件夹")
            return
            
        item_text = self.file_tree.item(selected[0], "text")
        current_path = self.current_path_entry.get().strip()
        file_path = os.path.join(current_path, item_text).replace("\\", "/")
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除 {item_text} 吗？"):
            return
            
        # 执行删除命令
        if item_text.endswith("/"):
            self.execute_command(f"adb shell rm -rf \"{file_path}\"", f"删除文件夹: {item_text}")
        else:
            self.execute_command(f"adb shell rm -f \"{file_path}\"", f"删除文件: {item_text}")
            
        self.refresh_file_list()
        
    def rename_file(self):
        """重命名文件"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 获取选中的文件
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要重命名的文件或文件夹")
            return
            
        item_text = self.file_tree.item(selected[0], "text")
        current_path = self.current_path_entry.get().strip()
        file_path = os.path.join(current_path, item_text).replace("\\", "/")
        
        # 获取新名称
        new_name = tk.simpledialog.askstring("重命名", "请输入新名称:", initialvalue=item_text)
        if new_name and new_name != item_text:
            new_path = os.path.join(current_path, new_name).replace("\\", "/")
            self.execute_command(f"adb shell mv \"{file_path}\" \"{new_path}\"", f"重命名: {item_text} -> {new_name}")
            self.refresh_file_list()
            
    def open_file(self):
        """打开文件"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 获取选中的文件
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要打开的文件")
            return
            
        item_text = self.file_tree.item(selected[0], "text")
        if item_text.endswith("/"):
            # 如果是目录，则进入该目录
            current_path = self.current_path_entry.get().strip()
            new_path = os.path.join(current_path, item_text).replace("\\", "/")
            self.current_path_entry.delete(0, tk.END)
            self.current_path_entry.insert(0, new_path)
            self.browse_device_path()
        else:
            # 如果是文件，则下载并打开
            self.download_and_open_file()
            
    def download_file(self):
        """下载文件"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 获取选中的文件
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要下载的文件")
            return
            
        item_text = self.file_tree.item(selected[0], "text")
        if item_text.endswith("/"):
            messagebox.showwarning("警告", "不能直接下载文件夹，请选择文件")
            return
            
        # 获取保存路径
        save_path = filedialog.asksaveasfilename(
            title="保存文件",
            initialfile=item_text,
            filetypes=[("所有文件", "*.*")]
        )
        
        if save_path:
            current_path = self.current_path_entry.get().strip()
            file_path = os.path.join(current_path, item_text).replace("\\", "/")
            self.execute_command(f"adb pull \"{file_path}\" \"{save_path}\"", f"下载文件: {item_text}")
            
    def download_and_open_file(self):
        """下载并打开文件"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 获取选中的文件
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要打开的文件")
            return
            
        item_text = self.file_tree.item(selected[0], "text")
        if item_text.endswith("/"):
            messagebox.showwarning("警告", "不能打开文件夹")
            return
            
        # 创建临时目录
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, item_text)
        
        # 下载文件
        current_path = self.current_path_entry.get().strip()
        file_path = os.path.join(current_path, item_text).replace("\\", "/")
        
        self.log_message(f"正在下载文件到临时目录: {temp_file}")
        result = subprocess.run([self.adb_path, 'pull', file_path, temp_file], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            self.log_message("文件下载成功，正在打开...", "SUCCESS")
            try:
                if platform.system() == "Windows":
                    os.startfile(temp_file)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(['open', temp_file])
                else:  # Linux
                    subprocess.run(['xdg-open', temp_file])
            except Exception as e:
                self.log_message(f"打开文件失败: {str(e)}", "ERROR")
        else:
            self.log_message("文件下载失败", "ERROR")
            
    def show_file_properties(self):
        """显示文件属性"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 获取选中的文件
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择文件或文件夹")
            return
            
        item_text = self.file_tree.item(selected[0], "text")
        current_path = self.current_path_entry.get().strip()
        file_path = os.path.join(current_path, item_text).replace("\\", "/")
        
        # 获取文件属性
        self.log_message(f"正在获取文件属性: {file_path}")
        result = subprocess.run([self.adb_path, 'shell', 'ls', '-la', file_path], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0: 
            # 创建属性对话框
            prop_dialog = tk.Toplevel(self.root)
            prop_dialog.title(f"文件属性: {item_text}")
            prop_dialog.geometry("400x300")
            prop_dialog.resizable(False, False)
            prop_dialog.transient(self.root)
            prop_dialog.grab_set()
            
            # 文件信息
            info_frame = ttk.Frame(prop_dialog, padding=10)
            info_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(info_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=item_text).grid(row=0, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(info_frame, text="路径:").grid(row=1, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=file_path).grid(row=1, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(info_frame, text="类型:").grid(row=2, column=0, sticky=tk.W, pady=5)
            file_type = "文件夹" if item_text.endswith("/") else "文件"
            ttk.Label(info_frame, text=file_type).grid(row=2, column=1, sticky=tk.W, pady=5)
            
            # 解析ls -la输出
            lines = result.stdout.strip().split('\n')
            if len(lines) > 0:
                parts = lines[0].split()
                if len(parts) >= 5:
                    permissions = parts[0]
                    owner = parts[2]
                    size = parts[3]
                    date = ' '.join(parts[4:7])
                    
                    ttk.Label(info_frame, text="权限:").grid(row=3, column=0, sticky=tk.W, pady=5)
                    ttk.Label(info_frame, text=permissions).grid(row=3, column=1, sticky=tk.W, pady=5)
                    
                    ttk.Label(info_frame, text="所有者:").grid(row=4, column=0, sticky=tk.W, pady=5)
                    ttk.Label(info_frame, text=owner).grid(row=4, column=1, sticky=tk.W, pady=5)
                    
                    ttk.Label(info_frame, text="大小:").grid(row=5, column=0, sticky=tk.W, pady=5)
                    ttk.Label(info_frame, text=size).grid(row=5, column=1, sticky=tk.W, pady=5)
                    
                    ttk.Label(info_frame, text="修改时间:").grid(row=6, column=0, sticky=tk.W, pady=5)
                    ttk.Label(info_frame, text=date).grid(row=6, column=1, sticky=tk.W, pady=5)
            
            # 关闭按钮
            ttk.Button(prop_dialog, text="关闭", command=prop_dialog.destroy).pack(pady=10)
        else:
            self.log_message("获取文件属性失败", "ERROR")
        
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(app_input_frame, text="获取包名", bootstyle="info-outline", 
                     command=self.get_package_name).pack(side=tk.LEFT)
        else:
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
            if BOOTSTRAP_AVAILABLE:
                ttk.Button(app_buttons, text=text, bootstyle="info-outline", 
                         command=command).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
            else:
                ttk.Button(app_buttons, text=text, 
                         command=command).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
            
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
            if BOOTSTRAP_AVAILABLE:
                btn = ttk.Button(service_buttons, text=name, bootstyle="secondary-outline",
                               command=lambda cmd=command, d=desc: self.execute_command(cmd, d))
            else:
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
            if BOOTSTRAP_AVAILABLE:
                btn = ttk.Button(settings_buttons, text=name, bootstyle="success-outline",
                               command=lambda cmd=command, d=desc: self.execute_command(cmd, d))
            else:
                btn = ttk.Button(settings_buttons, text=name,
                               command=lambda cmd=command, d=desc: self.execute_command(cmd, d))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
        settings_buttons.columnconfigure(0, weight=1)
        settings_buttons.columnconfigure(1, weight=1)
        
        # 高级系统工具
        advanced_frame = ttk.LabelFrame(parent, text="高级系统工具", padding=10)
        advanced_frame.pack(fill=tk.X, pady=(10, 0))
        
        advanced_buttons = ttk.Frame(advanced_frame)
        advanced_buttons.pack(fill=tk.X)
        
        advanced_tools = [
            ("刷入Recovery", self.flash_recovery),
            ("刷入Boot", self.flash_boot),
            ("刷入系统", self.flash_system),
            ("备份系统", self.backup_system)
        ]
        
        for i, (name, command) in enumerate(advanced_tools):
            if BOOTSTRAP_AVAILABLE:
                ttk.Button(advanced_buttons, text=name, bootstyle="danger-outline", 
                         command=command).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            else:
                ttk.Button(advanced_buttons, text=name, 
                         command=command).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
        advanced_buttons.columnconfigure(0, weight=1)
        advanced_buttons.columnconfigure(1, weight=1)
        
    def flash_recovery(self):
        """刷入Recovery"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 选择Recovery镜像
        recovery_file = filedialog.askopenfilename(
            title="选择Recovery镜像",
            filetypes=[("镜像文件", "*.img"), ("所有文件", "*.*")]
        )
        
        if recovery_file:
            # 确认刷入
            if not messagebox.askyesno("警告", "刷入Recovery可能导致设备无法启动！\n确定要继续吗？"):
                return
                
            # 重启到Bootloader
            self.execute_command("adb reboot bootloader", "重启到Bootloader")
            time.sleep(5)  # 等待设备重启
            
            # 刷入Recovery
            self.execute_command(f"fastboot flash recovery \"{recovery_file}\"", "刷入Recovery")
            
            # 重启设备
            if messagebox.askyesno("完成", "Recovery刷入完成，是否重启设备？"):
                self.execute_command("fastboot reboot", "重启设备")
                
    def flash_boot(self):
        """刷入Boot"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 选择Boot镜像
        boot_file = filedialog.askopenfilename(
            title="选择Boot镜像",
            filetypes=[("镜像文件", "*.img"), ("所有文件", "*.*")]
        )
        
        if boot_file:
            # 确认刷入
            if not messagebox.askyesno("警告", "刷入Boot可能导致设备无法启动！\n确定要继续吗？"):
                return
                
            # 重启到Bootloader
            self.execute_command("adb reboot bootloader", "重启到Bootloader")
            time.sleep(5)  # 等待设备重启
            
            # 刷入Boot
            self.execute_command(f"fastboot flash boot \"{boot_file}\"", "刷入Boot")
            
            # 重启设备
            if messagebox.askyesno("完成", "Boot刷入完成，是否重启设备？"):
                self.execute_command("fastboot reboot", "重启设备")
                
    def flash_system(self):
        """刷入系统"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 选择系统镜像
        system_file = filedialog.askopenfilename(
            title="选择系统镜像",
            filetypes=[("镜像文件", "*.img"), ("所有文件", "*.*")]
        )
        
        if system_file:
            # 确认刷入
            if not messagebox.askyesno("警告", "刷入系统将清除所有数据！\n确定要继续吗？"):
                return
                
            # 重启到Bootloader
            self.execute_command("adb reboot bootloader", "重启到Bootloader")
            time.sleep(5)  # 等待设备重启
            
            # 刷入系统
            self.execute_command(f"fastboot flash system \"{system_file}\"", "刷入系统")
            
            # 重启设备
            if messagebox.askyesno("完成", "系统刷入完成，是否重启设备？"):
                self.execute_command("fastboot reboot", "重启设备")
                
    def backup_system(self):
        """备份系统"""
        # 检查设备连接
        if not self.current_device.get():
            messagebox.showwarning("警告", "请先连接设备")
            return
            
        # 选择备份目录
        backup_dir = filedialog.askdirectory(title="选择备份目录")
        if not backup_dir:
            return
            
        # 创建备份对话框
        backup_dialog = tk.Toplevel(self.root)
        backup_dialog.title("系统备份")
        backup_dialog.geometry("400x300")
        backup_dialog.resizable(False, False)
        backup_dialog.transient(self.root)
        backup_dialog.grab_set()
        
        # 备份选项
        ttk.Label(backup_dialog, text="系统备份选项", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        options_frame = ttk.Frame(backup_dialog, padding=10)
        options_frame.pack(fill=tk.X)
        
        backup_system = tk.BooleanVar(value=True)
        backup_data = tk.BooleanVar(value=True)
        backup_cache = tk.BooleanVar(value=False)
        backup_boot = tk.BooleanVar(value=True)
        backup_recovery = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="系统分区", variable=backup_system).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="数据分区", variable=backup_data).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="缓存分区", variable=backup_cache).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Boot分区", variable=backup_boot).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Recovery分区", variable=backup_recovery).pack(anchor=tk.W)
        
        # 备份按钮
        button_frame = ttk.Frame(backup_dialog)
        button_frame.pack(pady=20)
        
        def do_backup():
            # 创建备份命令
            backup_name = f"backup_{time.strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            # 构建备份命令
            backup_cmd = "adb backup -f"
            if backup_system.get():
                self.execute_command(f"adb pull /system {os.path.join(backup_path, 'system')}", "备份系统分区")
            if backup_data.get():
                self.execute_command(f"adb backup -f {os.path.join(backup_path, 'data.ab')} -all -apk -shared", "备份数据分区")
            if backup_cache.get():
                self.execute_command(f"adb pull /cache {os.path.join(backup_path, 'cache')}", "备份缓存分区")
            if backup_boot.get():
                self.execute_command("adb reboot bootloader", "重启到Bootloader")
                time.sleep(5)
                self.execute_command(f"fastboot dump boot {os.path.join(backup_path, 'boot.img')}", "备份Boot分区")
                self.execute_command("fastboot reboot", "重启设备")
            if backup_recovery.get():
                self.execute_command("adb reboot bootloader", "重启到Bootloader")
                time.sleep(5)
                self.execute_command(f"fastboot dump recovery {os.path.join(backup_path, 'recovery.img')}", "备份Recovery分区")
                self.execute_command("fastboot reboot", "重启设备")
                
            messagebox.showinfo("完成", f"系统备份完成！\n备份保存在: {backup_path}", parent=backup_dialog)
            backup_dialog.destroy()
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="开始备份", bootstyle="success", command=do_backup).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", bootstyle="secondary", command=backup_dialog.destroy).pack(side=tk.LEFT)
        else:
            ttk.Button(button_frame, text="开始备份", command=do_backup).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", command=backup_dialog.destroy).pack(side=tk.LEFT)
        
    def setup_console(self, parent):
        """设置控制台"""
        # 命令输入区域
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="ADB命令:").pack(side=tk.LEFT)
        self.command_entry = ttk.Entry(input_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.command_entry.bind('<Return>', lambda e: self.execute_custom_command())
        self.command_entry.bind('<Up>', self.show_previous_command)
        self.command_entry.bind('<Down>', self.show_next_command)
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(input_frame, text="执行", bootstyle="success", 
                     command=self.execute_custom_command).pack(side=tk.RIGHT)
        else:
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
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(console_buttons, text="清空控制台", bootstyle="secondary", 
                     command=self.clear_console).pack(side=tk.LEFT)
            ttk.Button(console_buttons, text="保存日志", bootstyle="info", 
                     command=self.save_log).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Button(console_buttons, text="导出日志", bootstyle="primary", 
                     command=self.export_log).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Button(console_buttons, text="重复上次命令", bootstyle="warning", 
                     command=self.repeat_last_command).pack(side=tk.LEFT, padx=(5, 0))
        else:
            ttk.Button(console_buttons, text="清空控制台", 
                     command=self.clear_console).pack(side=tk.LEFT)
            ttk.Button(console_buttons, text="保存日志", 
                     command=self.save_log).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Button(console_buttons, text="导出日志", 
                     command=self.export_log).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Button(console_buttons, text="重复上次命令", 
                     command=self.repeat_last_command).pack(side=tk.LEFT, padx=(5, 0))
        
    def show_previous_command(self, event):
        """显示上一条命令"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        return "break"
        
    def show_next_command(self, event):
        """显示下一条命令"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
        return "break"
        
    def repeat_last_command(self):
        """重复上次命令"""
        if self.last_command:
            self.execute_command(self.last_command, "重复上次命令")
        else:
            self.log_message("没有可重复的命令", "WARNING")
            
    def setup_quick_commands(self, parent):
        """设置快捷命令"""
        # 快捷命令列表
        commands_frame = ttk.Frame(parent)
        commands_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建列表
        columns = ("name", "command", "description")
        self.commands_tree = ttk.Treeview(commands_frame, columns=columns, show="headings")
        self.commands_tree.heading("name", text="名称")
        self.commands_tree.heading("command", text="命令")
        self.commands_tree.heading("description", text="描述")
        
        self.commands_tree.column("name", width=150)
        self.commands_tree.column("command", width=300)
        self.commands_tree.column("description", width=200)
        
        commands_scrollbar = ttk.Scrollbar(commands_frame, orient=tk.VERTICAL, command=self.commands_tree.yview)
        self.commands_tree.configure(yscrollcommand=commands_scrollbar.set)
        
        self.commands_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commands_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(buttons_frame, text="添加命令", bootstyle="success", 
                     command=self.add_quick_command).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="编辑命令", bootstyle="info", 
                     command=self.edit_quick_command).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="删除命令", bootstyle="danger", 
                     command=self.delete_quick_command).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="执行命令", bootstyle="warning", 
                     command=self.run_quick_command).pack(side=tk.LEFT)
        else:
            ttk.Button(buttons_frame, text="添加命令", 
                     command=self.add_quick_command).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="编辑命令", 
                     command=self.edit_quick_command).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="删除命令", 
                     command=self.delete_quick_command).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="执行命令", 
                     command=self.run_quick_command).pack(side=tk.LEFT)
        
        # 绑定双击事件
        self.commands_tree.bind("<Double-1>", lambda e: self.run_quick_command())
        
        # 加载快捷命令
        self.load_quick_commands()
        
    def load_quick_commands(self):
        """加载快捷命令"""
        # 清空列表
        for item in self.commands_tree.get_children():
            self.commands_tree.delete(item)
            
        # 加载命令
        commands = self.settings.get("custom_commands", [])
        for cmd in commands:
            self.commands_tree.insert("", tk.END, values=(cmd["name"], cmd["command"], cmd["description"]))
            
        # 添加默认命令
        if not commands:
            default_commands = [
                {"name": "重启设备", "command": "adb reboot", "description": "重启Android设备"},
                {"name": "截取屏幕", "command": "adb shell screencap -p /sdcard/screenshot.png && adb pull /sdcard/screenshot.png", "description": "截取设备屏幕"},
                {"name": "查看电池信息", "command": "adb shell dumpsys battery", "description": "查看电池信息"}
            ]
            
            for cmd in default_commands:
                self.commands_tree.insert("", tk.END, values=(cmd["name"], cmd["command"], cmd["description"]))
                
            self.settings["custom_commands"] = default_commands
            self.save_settings()
            
    def add_quick_command(self):
        """添加快捷命令"""
        # 创建对话框
        command_dialog = tk.Toplevel(self.root)
        command_dialog.title("添加快捷命令")
        command_dialog.geometry("500x250")
        command_dialog.resizable(False, False)
        command_dialog.transient(self.root)
        command_dialog.grab_set()
        
        # 命令信息
        info_frame = ttk.Frame(command_dialog, padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="命令名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(info_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="ADB命令:").grid(row=1, column=0, sticky=tk.W, pady=5)
        command_entry = ttk.Entry(info_frame, width=40)
        command_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, pady=5)
        description_entry = ttk.Entry(info_frame, width=40)
        description_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(command_dialog)
        button_frame.pack(pady=10)
        
        def save_command():
            name = name_entry.get().strip()
            command = command_entry.get().strip()
            description = description_entry.get().strip()
            
            if not name or not command:
                messagebox.showwarning("警告", "请填写命令名称和ADB命令", parent=command_dialog)
                return
                
            # 添加到列表
            self.commands_tree.insert("", tk.END, values=(name, command, description))
            
            # 保存到设置
            commands = self.settings.get("custom_commands", [])
            commands.append({"name": name, "command": command, "description": description})
            self.settings["custom_commands"] = commands
            self.save_settings()
            
            command_dialog.destroy()
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="保存", bootstyle="success", 
                     command=save_command).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", bootstyle="secondary", 
                     command=command_dialog.destroy).pack(side=tk.LEFT)
        else:
            ttk.Button(button_frame, text="保存", 
                     command=save_command).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", 
                     command=command_dialog.destroy).pack(side=tk.LEFT)
            
    def edit_quick_command(self):
        """编辑快捷命令"""
        # 获取选中的命令
        selected = self.commands_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的命令")
            return
            
        item = selected[0]
        values = self.commands_tree.item(item, "values")
        
        # 创建对话框
        command_dialog = tk.Toplevel(self.root)
        command_dialog.title("编辑快捷命令")
        command_dialog.geometry("500x250")
        command_dialog.resizable(False, False)
        command_dialog.transient(self.root)
        command_dialog.grab_set()
        
        # 命令信息
        info_frame = ttk.Frame(command_dialog, padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="命令名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(info_frame, width=40)
        name_entry.insert(0, values[0])
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="ADB命令:").grid(row=1, column=0, sticky=tk.W, pady=5)
        command_entry = ttk.Entry(info_frame, width=40)
        command_entry.insert(0, values[1])
        command_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, pady=5)
        description_entry = ttk.Entry(info_frame, width=40)
        description_entry.insert(0, values[2])
        description_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(command_dialog)
        button_frame.pack(pady=10)
        
        def save_command():
            name = name_entry.get().strip()
            command = command_entry.get().strip()
            description = description_entry.get().strip()
            
            if not name or not command:
                messagebox.showwarning("警告", "请填写命令名称和ADB命令", parent=command_dialog)
                return
                
            # 更新列表
            self.commands_tree.item(item, values=(name, command, description))
            
            # 保存到设置
            commands = self.settings.get("custom_commands", [])
            index = self.commands_tree.index(item)
            if index < len(commands):
                commands[index] = {"name": name, "command": command, "description": description}
                self.settings["custom_commands"] = commands
                self.save_settings()
            
            command_dialog.destroy()
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="保存", bootstyle="success", 
                     command=save_command).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", bootstyle="secondary", 
                     command=command_dialog.destroy).pack(side=tk.LEFT)
        else:
            ttk.Button(button_frame, text="保存", 
                     command=save_command).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", 
                     command=command_dialog.destroy).pack(side=tk.LEFT)
            
    def delete_quick_command(self):
        """删除快捷命令"""
        # 获取选中的命令
        selected = self.commands_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的命令")
            return
            
        # 确认删除
        if not messagebox.askyesno("确认删除", "确定要删除选中的命令吗？"):
            return
            
        # 删除命令
        for item in selected:
            index = self.commands_tree.index(item)
            self.commands_tree.delete(item)
            
            # 从设置中删除
            commands = self.settings.get("custom_commands", [])
            if index < len(commands):
                commands.pop(index)
                self.settings["custom_commands"] = commands
                self.save_settings()
                
    def run_quick_command(self):
        """运行快捷命令"""
        # 获取选中的命令
        selected = self.commands_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要执行的命令")
            return
            
        # 执行命令
        item = selected[0]
        values = self.commands_tree.item(item, "values")
        command = values[1]
        description = values[2]
        
        self.execute_command(command, description)
        
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
        
        # 管理员状态
        admin_text = "管理员模式" if self.is_admin else "普通模式"
        admin_color = "green" if self.is_admin else "red"
        ttk.Label(status_frame, text="权限:").pack(side=tk.LEFT)
        ttk.Label(status_frame, text=admin_text, foreground=admin_color).pack(side=tk.LEFT, padx=(5, 20))
        
        # 版本信息
        ttk.Label(status_frame, text="奕奕ADB工具箱 v0.1.1 | GitHub: yys20071108").pack(side=tk.RIGHT)
        
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
            
            # 添加可能的路径
            if platform.system() == "Windows":
                # 添加常见的ADB路径
                possible_paths = [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Android', 'Sdk', 'platform-tools'),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), 'Android', 'platform-tools'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Android', 'platform-tools'),
                    os.path.dirname(os.path.abspath(sys.argv[0])),
                    os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'platform-tools'),
                    os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'adb'),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        adb_path = os.path.join(path, 'adb.exe')
                        if os.path.exists(adb_path):
                            adb_commands.insert(0, adb_path)
                            self.platform_tools_dir = path
                
                # 添加当前目录和子目录
                for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(sys.argv[0]))):
                    for file in files:
                        if file.lower() == 'adb.exe':
                            adb_commands.insert(0, os.path.join(root, file))
                            self.platform_tools_dir = root
                            break
            else:
                # Linux/macOS路径
                possible_paths = [
                    os.path.join(os.path.expanduser('~'), 'Android', 'Sdk', 'platform-tools'),
                    '/usr/local/bin',
                    '/usr/bin',
                    os.path.dirname(os.path.abspath(sys.argv[0])),
                    os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'platform-tools'),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        adb_path = os.path.join(path, 'adb')
                        if os.path.exists(adb_path):
                            adb_commands.insert(0, adb_path)
                            self.platform_tools_dir = path
        
            adb_found = False
            for adb_cmd in adb_commands:
                try:
                    result = subprocess.run([adb_cmd, 'version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.adb_path = adb_cmd
                        adb_found = True
                        self.log_message(f"找到ADB: {adb_cmd}", "SUCCESS")
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue
                
            if adb_found:
                self.env_status['adb_status'].config(text="已安装", foreground="green")
                self.log_message("ADB环境检测成功", "SUCCESS")
                
                # 获取ADB版本
                try:
                    result = subprocess.run([self.adb_path, 'version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version_match = re.search(r'Android Debug Bridge version (\d+\.\d+\.\d+)', result.stdout)
                        if version_match:
                            version = version_match.group(1)
                            self.env_status['tools_status'].config(text=f"v{version}", foreground="green")
                            self.log_message(f"Platform-tools版本: {version}", "SUCCESS")
                except Exception as e:
                    self.log_message(f"获取ADB版本失败: {str(e)}", "ERROR")
            else:
                self.env_status['adb_status'].config(text="未安装", foreground="red")
                self.log_message("ADB环境检测失败，请安装ADB工具", "ERROR")
                self.env_status['tools_status'].config(text="未安装", foreground="red")
                
            # 检查USB驱动
            try:
                if platform.system() == "Windows":
                    # 检查是否有Android设备驱动
                    result = subprocess.run(['wmic', 'path', 'Win32_PnPEntity', 'get', 'Caption'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        if "Android" in result.stdout or "ADB" in result.stdout:
                            self.env_status['driver_status'].config(text="已安装", foreground="green")
                            self.log_message("USB驱动检测成功", "SUCCESS")
                        else:
                            self.env_status['driver_status'].config(text="未检测到", foreground="orange")
                            self.log_message("未检测到Android USB驱动", "WARNING")
                    else:
                        self.env_status['driver_status'].config(text="检测失败", foreground="orange")
                else:
                    # Linux/macOS不需要额外驱动
                    self.env_status['driver_status'].config(text="不需要", foreground="green")
            except Exception as e:
                self.log_message(f"USB驱动检测失败: {str(e)}", "WARNING")
                self.env_status['driver_status'].config(text="检测失败", foreground="orange")
                
            # 如果设置了自动连接，则尝试连接设备
            if self.settings.get("auto_connect", True):
                self.refresh_devices()
            
        threading.Thread(target=check, daemon=True).start()
        
    def connect_device(self):
        """连接设备"""
        def connect():
            try:
                self.log_message("正在扫描设备...")
                
                # 根据连接方式执行不同的连接命令
                if self.connection_type.get() == "WiFi连接":
                    ip = self.ip_entry.get().strip()
                    port = self.port_entry.get().strip()
                    
                    if not ip or not port:
                        self.log_message("请输入有效的IP地址和端口", "WARNING")
                        return
                        
                    # 保存设置
                    self.settings["last_wifi_ip"] = ip
                    self.settings["last_wifi_port"] = port
                    
                    # 执行连接命令
                    self.log_message(f"正在连接到 {ip}:{port}...")
                    result = subprocess.run([self.adb_path, 'connect', f"{ip}:{port}"], 
                                          capture_output=True, text=True, timeout=10)
                    
                    if "connected" in result.stdout.lower():
                        self.log_message(f"WiFi连接成功: {ip}:{port}", "SUCCESS")
                    else:
                        self.log_message(f"WiFi连接失败: {result.stdout}", "ERROR")
                
                # 获取设备列表
                result = subprocess.run([self.adb_path, 'devices'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    devices = []
                    lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
                    
                    for line in lines:
                        if line.strip() and '\t' in line:
                            device_id, status = line.split('\t')
                            if status.lower() == 'device':
                                devices.append(device_id)
                            else:
                                self.log_message(f"设备 {device_id} 状态: {status}", "WARNING")
                            
                    if devices:
                        self.connected_devices = devices
                        self.device_combo['values'] = devices
                        
                        # 如果当前没有选择设备，则选择第一个
                        if not self.current_device.get() or self.current_device.get() not in devices:
                            self.current_device.set(devices[0])
                            
                        self.connection_status.set("已连接")
                        self.status_label.config(foreground="green")
                        self.log_message(f"设备连接成功: {self.current_device.get()}", "SUCCESS")
                        self.get_device_info()
                    else:
                        self.connected_devices = []
                        self.device_combo['values'] = []
                        self.current_device.set("")
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
                device_id = self.current_device.get()
                if not device_id:
                    return
                    
                # 检查缓存
                if device_id in self.device_info_cache:
                    # 更新设备信息显示
                    self.device_info_text.config(state=tk.NORMAL)
                    self.device_info_text.delete(1.0, tk.END)
                    self.device_info_text.insert(1.0, self.device_info_cache[device_id])
                    self.device_info_text.config(state=tk.DISABLED)
                    return
                
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
                    result = subprocess.run([self.adb_path, '-s', device_id, 'shell', 'getprop', prop],
                                          capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore')
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        device_info += f"{desc}: {value}\n"
                        
                # 获取电池信息
                battery_result = subprocess.run([self.adb_path, '-s', device_id, 'shell', 'dumpsys', 'battery'],
                                              capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore')
                if battery_result.returncode == 0:
                    battery_lines = battery_result.stdout.split('\n')
                    for line in battery_lines:
                        if 'level:' in line:
                            level = line.split(':')[1].strip()
                            device_info += f"电池电量: {level}%\n"
                            break
                            
                # 获取存储信息
                storage_result = subprocess.run([self.adb_path, '-s', device_id, 'shell', 'df', '/sdcard'],
                                              capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore')
                if storage_result.returncode == 0:
                    storage_lines = storage_result.stdout.split('\n')
                    if len(storage_lines) > 1:
                        parts = storage_lines[1].split()
                        if len(parts) >= 4:
                            total = int(parts[1]) // 1024  # KB to MB
                            used = int(parts[2]) // 1024   # KB to MB
                            free = int(parts[3]) // 1024   # KB to MB
                            device_info += f"存储空间: 总计 {total}MB, 已用 {used}MB, 可用 {free}MB\n"
                
                # 获取内存信息
                mem_result = subprocess.run([self.adb_path, '-s', device_id, 'shell', 'cat', '/proc/meminfo'],
                                          capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore')
                if mem_result.returncode == 0:
                    mem_lines = mem_result.stdout.split('\n')
                    total_mem = 0
                    free_mem = 0
                    
                    for line in mem_lines:
                        if 'MemTotal:' in line:
                            total_mem = int(line.split()[1]) // 1024  # KB to MB
                        elif 'MemFree:' in line:
                            free_mem = int(line.split()[1]) // 1024   # KB to MB
                            
                    if total_mem > 0:
                        used_mem = total_mem - free_mem
                        device_info += f"内存: 总计 {total_mem}MB, 已用 {used_mem}MB, 可用 {free_mem}MB\n"
                
                # 缓存设备信息
                self.device_info_cache[device_id] = device_info
                            
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
                
                # 保存最后执行的命令
                self.last_command = command
                
                # 添加到命令历史
                if command not in self.command_history:
                    self.command_history.append(command)
                    self.history_index = len(self.command_history)
                
                # 分割命令并处理路径
                cmd_parts = command.split()
                if cmd_parts[0] != 'adb':
                    cmd_parts = [self.adb_path] + cmd_parts
                else:
                    cmd_parts[0] = self.adb_path
                
                # 如果有选择设备且命令不包含 -s 参数，则添加设备参数
                device_id = self.current_device.get()
                if device_id and '-s' not in cmd_parts and cmd_parts[1] != 'connect' and cmd_parts[1] != 'disconnect':
                    cmd_parts.insert(1, '-s')
                    cmd_parts.insert(2, device_id)
                
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
            # 清空文件列表
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
                
            # 获取文件列表
            self.log_message(f"正在浏览路径: {path}")
            result = subprocess.run([self.adb_path, 'shell', 'ls', '-la', path], 
                                  capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # 添加返回上级目录
                if path != "/" and path != "/sdcard":
                    self.file_tree.insert("", tk.END, text="../", values=("", "", ""))
                
                # 解析文件列表
                for line in lines:
                    if line.startswith('total') or not line.strip():
                        continue
                        
                    parts = line.split()
                    if len(parts) >= 8:
                        permissions = parts[0]
                        size = parts[4]
                        date = ' '.join(parts[5:8])
                        name = ' '.join(parts[8:])
                        
                        # 处理目录和文件
                        if permissions.startswith('d'):
                            self.file_tree.insert("", tk.END, text=f"{name}/", values=(size, date, permissions))
                        else:
                            self.file_tree.insert("", tk.END, text=name, values=(size, date, permissions))
            else:
                self.log_message(f"浏览路径失败: {result.stderr}", "ERROR")
        else:
            self.log_message("请输入有效的路径", "WARNING")
            
    def get_package_name(self):
        """获取包名列表"""
        # 创建包名选择对话框
        package_dialog = tk.Toplevel(self.root)
        package_dialog.title("应用包名列表")
        package_dialog.geometry("600x400")
        package_dialog.transient(self.root)
        package_dialog.grab_set()
        
        # 创建搜索框
        search_frame = ttk.Frame(package_dialog, padding=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, width=40)
        search_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        # 创建包名列表
        list_frame = ttk.Frame(package_dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("package", "app")
        package_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        package_tree.heading("package", text="包名")
        package_tree.heading("app", text="应用名")
        
        package_tree.column("package", width=300)
        package_tree.column("app", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=package_tree.yview)
        package_tree.configure(yscrollcommand=scrollbar.set)
        
        package_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮
        button_frame = ttk.Frame(package_dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def select_package():
            selected = package_tree.selection()
            if selected:
                package = package_tree.item(selected[0], "values")[0]
                self.package_entry.delete(0, tk.END)
                self.package_entry.insert(0, package)
                package_dialog.destroy()
                
        def filter_packages(event=None):
            search_text = search_entry.get().lower()
            for item in package_tree.get_children():
                package_tree.delete(item)
                
            for package, app in packages:
                if search_text in package.lower() or search_text in app.lower():
                    package_tree.insert("", tk.END, values=(package, app))
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="选择", bootstyle="success", 
                     command=select_package).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", bootstyle="secondary", 
                     command=package_dialog.destroy).pack(side=tk.LEFT)
        else:
            ttk.Button(button_frame, text="选择", 
                     command=select_package).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", 
                     command=package_dialog.destroy).pack(side=tk.LEFT)
        
        # 绑定双击事件
        package_tree.bind("<Double-1>", lambda e: select_package())
        
        # 绑定搜索事件
        search_entry.bind("<KeyRelease>", filter_packages)
        
        # 获取包名列表
        self.log_message("正在获取应用包名列表...")
        packages = []
        
        def get_packages():
            try:
                # 获取包名列表
                result = subprocess.run([self.adb_path, 'shell', 'pm', 'list', 'packages', '-f'], 
                                      capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    
                    for line in lines:
                        if line.startswith('package:'):
                            # 解析包名和APK路径
                            parts = line[8:].split('=')
                            if len(parts) == 2:
                                apk_path = parts[0]
                                package = parts[1]
                                
                                # 获取应用名称
                                app_name = package.split('.')[-1]  # 默认使用包名最后一部分
                                
                                # 尝试获取应用标签
                                try:
                                    label_result = subprocess.run([self.adb_path, 'shell', 'dumpsys', 'package', package, '|', 'grep', 'labelRes'], 
                                                               capture_output=True, text=True, encoding='utf-8', errors='ignore')
                                    if "labelRes" in label_result.stdout:
                                        app_name = label_result.stdout.strip().split('=')[1]
                                except:
                                    pass
                                
                                packages.append((package, app_name))
                    
                    # 更新列表
                    for package, app in packages:
                        package_tree.insert("", tk.END, values=(package, app))
                        
                    self.log_message(f"找到 {len(packages)} 个应用", "SUCCESS")
                else:
                    self.log_message("获取包名列表失败", "ERROR")
            except Exception as e:
                self.log_message(f"获取包名列表错误: {str(e)}", "ERROR")
                
        threading.Thread(target=get_packages, daemon=True).start()
        
    def install_apk(self):
        """安装APK"""
        apk_file = filedialog.askopenfilename(
            title="选择APK文件",
            filetypes=[("APK文件", "*.apk")]
        )
        if apk_file:
            command = f"adb install -r \"{apk_file}\""
            self.execute_command(command, f"安装APK: {os.path.basename(apk_file)}")
            
    def uninstall_app(self):
        """卸载应用"""
        package = self.package_entry.get().strip()
        if package:
            # 确认卸载
            if messagebox.askyesno("确认卸载", f"确定要卸载 {package} 吗？"):
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
            # 确认清除
            if messagebox.askyesno("确认清除", f"确定要清除 {package} 的所有数据吗？"):
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
                
                # 创建临时目录
                temp_dir = tempfile.mkdtemp()
                self.log_message(f"临时目录: {temp_dir}", "INFO")
                
                # 下载platform-tools
                platform_tools_url = ""
                if platform.system() == "Windows":
                    platform_tools_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
                elif platform.system() == "Darwin":  # macOS
                    platform_tools_url = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
                else:  # Linux
                    platform_tools_url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
                
                if not platform_tools_url:
                    self.log_message("不支持的操作系统", "ERROR")
                    return
                
                # 下载文件
                self.log_message(f"正在下载 platform-tools: {platform_tools_url}", "INFO")
                
                try:
                    if REQUESTS_AVAILABLE:
                        response = requests.get(platform_tools_url, stream=True)
                        total_size = int(response.headers.get('content-length', 0))
                        zip_path = os.path.join(temp_dir, "platform-tools.zip")
                        
                        with open(zip_path, 'wb') as f:
                            downloaded = 0
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress = int(downloaded / total_size * 100)
                                    if progress % 10 == 0:
                                        self.log_message(f"下载进度: {progress}%", "INFO")
                    else:
                        zip_path = os.path.join(temp_dir, "platform-tools.zip")
                        urllib.request.urlretrieve(platform_tools_url, zip_path)
                        self.log_message("下载完成", "SUCCESS")
                except Exception as e:
                    self.log_message(f"下载失败: {str(e)}", "ERROR")
                    return
                
                # 解压文件
                self.log_message("正在解压文件...", "INFO")
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    self.log_message("解压完成", "SUCCESS")
                except Exception as e:
                    self.log_message(f"解压失败: {str(e)}", "ERROR")
                    return
                
                # 安装到程序目录
                install_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                platform_tools_dir = os.path.join(temp_dir, "platform-tools")
                
                self.log_message(f"正在安装到: {install_dir}", "INFO")
                try:
                    # 如果目标目录已存在platform-tools，先备份
                    target_dir = os.path.join(install_dir, "platform-tools")
                    if os.path.exists(target_dir):
                        backup_dir = os.path.join(install_dir, "platform-tools.bak")
                        if os.path.exists(backup_dir):
                            shutil.rmtree(backup_dir)
                        shutil.move(target_dir, backup_dir)
                        self.log_message(f"已备份原有platform-tools到: {backup_dir}", "INFO")
                    
                    # 复制新的platform-tools
                    shutil.copytree(platform_tools_dir, target_dir)
                    self.log_message("安装完成", "SUCCESS")
                    
                    # 更新ADB路径
                    if platform.system() == "Windows":
                        self.adb_path = os.path.join(target_dir, "adb.exe")
                    else:
                        self.adb_path = os.path.join(target_dir, "adb")
                    
                    # 更新环境变量
                    self.platform_tools_dir = target_dir
                    
                    # 检查环境
                    self.check_environment()
                except Exception as e:
                    self.log_message(f"安装失败: {str(e)}", "ERROR")
                    return
                
                # 清理临时文件
                try:
                    shutil.rmtree(temp_dir)
                    self.log_message("清理临时文件完成", "INFO")
                except:
                    pass
                
                self.log_message("ADB环境安装完成", "SUCCESS")
                messagebox.showinfo("安装成功", "ADB环境安装成功！\n请重新启动程序以确保所有功能正常工作。")
                
            except Exception as e:
                self.log_message(f"安装失败: {str(e)}", "ERROR")
                
        threading.Thread(target=install, daemon=True).start()
        
    def fix_adb(self):
        """修复ADB"""
        def fix():
            try:
                self.log_message("正在修复ADB...", "INFO")
                
                # 杀死ADB服务
                if platform.system() == "Windows":
                    subprocess.run(['taskkill', '/F', '/IM', 'adb.exe'], 
                                 capture_output=True, text=True)
                else:
                    subprocess.run(['killall', 'adb'], 
                                 capture_output=True, text=True)
                
                # 重启ADB服务
                subprocess.run([self.adb_path, 'kill-server'], 
                             capture_output=True, text=True)
                time.sleep(1)
                subprocess.run([self.adb_path, 'start-server'], 
                             capture_output=True, text=True)
                
                self.log_message("ADB服务已重启", "SUCCESS")
                
                # 刷新设备列表
                self.refresh_devices()
                
            except Exception as e:
                self.log_message(f"修复ADB失败: {str(e)}", "ERROR")
                
        threading.Thread(target=fix, daemon=True).start()
        
    def check_update(self):
        """检查更新"""
        def check():
            try:
                self.log_message("正在检查更新...", "INFO")
                
                # 这里应该实现实际的更新检查逻辑
                # 为了演示，我们只是模拟检查过程
                if REQUESTS_AVAILABLE:
                    try:
                        response = requests.get("https://api.github.com/repos/yys20071108/-adb-/releases/latest", timeout=5)
                        if response.status_code == 200:
                            release_info = response.json()
                            latest_version = release_info.get("tag_name", "").replace("v", "")
                            
                            if latest_version and latest_version > "0.1.1":
                                self.log_message(f"发现新版本: {latest_version}", "SUCCESS")
                                
                                # 显示更新对话框
                                if messagebox.askyesno("更新可用", f"发现新版本: {latest_version}\n当前版本: 0.1.1\n\n是否前往下载页面？"):
                                    webbrowser.open(release_info.get("html_url", "https://github.com/yys20071108/-adb-/releases"))
                            else:
                                self.log_message("当前已是最新版本", "SUCCESS")
                        else:
                            self.log_message("检查更新失败，无法连接到GitHub", "ERROR")
                    except Exception as e:
                        self.log_message(f"检查更新失败: {str(e)}", "ERROR")
                else:
                    time.sleep(1)
                    self.log_message("当前已是最新版本", "SUCCESS")
            except Exception as e:
                self.log_message(f"检查更新失败: {str(e)}", "ERROR")
                
        threading.Thread(target=check, daemon=True).start()
        
    def show_about(self):
        """显示关于对话框"""
        about_text = """
奕奕ADB工具箱 v0.1.1

一个功能丰富的Android调试工具

开发者: YYS
GitHub: https://github.com/yys20071108/-adb-
邮箱: 1450788363@qq.com

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
        
    def show_help(self):
        """显示帮助对话框"""
        help_text = """
奕奕ADB工具箱使用帮助

1. 设备连接
   • USB连接: 确保手机已开启USB调试模式
   • WiFi连接: 先通过USB连接，然后启用无线调试

2. 基础工具
   • 提供常用ADB命令的快捷操作
   • 点击按钮即可执行相应功能

3. 高级功能
   • Root管理: 检测和使用Root权限
   • 系统属性: 查看和修改系统属性
   • 性能监控: 查看设备性能数据

4. 文件管理
   • 文件传输: 在设备和电脑之间传输文件
   • 文件浏览器: 浏览和管理设备文件系统

5. 系统工具
   • 应用管理: 安装、卸载和管理应用
   • 系统服务: 控制WiFi、蓝牙等系统服务
   • 系统设置: 修改系统设置

6. 控制台
   • 执行自定义ADB命令
   • 查看命令执行结果和日志

7. 快捷命令
   • 保存和管理常用命令
   • 快速执行保存的命令

如需更多帮助，请访问GitHub页面或联系开发者。
        """
        
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        # 帮助内容
        help_frame = ttk.Frame(help_window, padding=10)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text_widget = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD, font=('Arial', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
        # 关闭按钮
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)
        
    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 创建选项卡
        if BOOTSTRAP_AVAILABLE:
            notebook = ttb.Notebook(settings_window)
        else:
            notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 常规设置选项卡
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text="常规设置")
        
        # ADB路径
        ttk.Label(general_frame, text="ADB路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        adb_path_entry = ttk.Entry(general_frame, width=40)
        adb_path_entry.insert(0, self.adb_path)
        adb_path_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        def browse_adb():
            path = filedialog.askopenfilename(
                title="选择ADB可执行文件",
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if path:
                adb_path_entry.delete(0, tk.END)
                adb_path_entry.insert(0, path)
                
        ttk.Button(general_frame, text="浏览", command=browse_adb).grid(row=0, column=2, padx=5)
        
        # 连接超时
        ttk.Label(general_frame, text="连接超时(秒):").grid(row=1, column=0, sticky=tk.W, pady=5)
        timeout_entry = ttk.Entry(general_frame, width=10)
        timeout_entry.insert(0, str(self.settings.get("timeout", 30)))
        timeout_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 自动检查更新
        auto_update = tk.BooleanVar(value=self.settings.get("auto_check_update", True))
        ttk.Checkbutton(general_frame, text="启动时自动检查更新", 
                       variable=auto_update).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 自动连接设备
        auto_connect = tk.BooleanVar(value=self.settings.get("auto_connect", True))
        ttk.Checkbutton(general_frame, text="启动时自动连接设备", 
                       variable=auto_connect).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 外观设置选项卡
        appearance_frame = ttk.Frame(notebook, padding=10)
        notebook.add(appearance_frame, text="外观设置")
        
        # 主题选择
        ttk.Label(appearance_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        if BOOTSTRAP_AVAILABLE:
            themes = ttb.Style().theme_names()
            theme_var = tk.StringVar(value=self.settings.get("theme", "cosmo"))
        elif THEMED_TK_AVAILABLE:
            themes = self.style.theme_names()
            theme_var = tk.StringVar(value=self.settings.get("theme", "arc"))
        else:
            themes = self.style.theme_names()
            theme_var = tk.StringVar(value=self.settings.get("theme", "default"))
            
        theme_combo = ttk.Combobox(appearance_frame, textvariable=theme_var, values=themes, state="readonly")
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 字体大小
        ttk.Label(appearance_frame, text="控制台字体大小:").grid(row=1, column=0, sticky=tk.W, pady=5)
        font_size = tk.StringVar(value=str(self.settings.get("console_font_size", 10)))
        font_combo = ttk.Combobox(appearance_frame, textvariable=font_size, values=["8", "9", "10", "11", "12", "14"], width=5)
        font_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 高级设置选项卡
        advanced_frame = ttk.Frame(notebook, padding=10)
        notebook.add(advanced_frame, text="高级设置")
        
        # 日志级别
        ttk.Label(advanced_frame, text="日志级别:").grid(row=0, column=0, sticky=tk.W, pady=5)
        log_level = tk.StringVar(value=self.settings.get("log_level", "INFO"))
        log_combo = ttk.Combobox(advanced_frame, textvariable=log_level, 
                               values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 启用调试模式
        debug_mode = tk.BooleanVar(value=self.settings.get("debug_mode", False))
        ttk.Checkbutton(advanced_frame, text="启用调试模式", 
                       variable=debug_mode).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 保存设置按钮
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=10)
        
        def save_settings():
            # 保存设置
            self.settings["adb_path"] = adb_path_entry.get()
            self.settings["timeout"] = int(timeout_entry.get())
            self.settings["auto_check_update"] = auto_update.get()
            self.settings["auto_connect"] = auto_connect.get()
            self.settings["theme"] = theme_var.get()
            self.settings["console_font_size"] = int(font_size.get())
            self.settings["log_level"] = log_level.get()
            self.settings["debug_mode"] = debug_mode.get()
            
            # 应用设置
            self.adb_path = self.settings["adb_path"]
            
            # 应用主题
            if BOOTSTRAP_AVAILABLE:
                self.style.theme_use(self.settings["theme"])
            elif THEMED_TK_AVAILABLE:
                self.style.set_theme(self.settings["theme"])
                
            # 应用字体大小
            self.console_text.config(font=('Consolas', self.settings["console_font_size"]))
            
            # 保存设置到文件
            self.save_settings()
            
            settings_window.destroy()
            self.log_message("设置已保存", "SUCCESS")
            
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(button_frame, text="保存", bootstyle="success", 
                     command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", bootstyle="secondary", 
                     command=settings_window.destroy).pack(side=tk.LEFT)
        else:
            ttk.Button(button_frame, text="保存", 
                     command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="取消", 
                     command=settings_window.destroy).pack(side=tk.LEFT)
        
    def run(self):
        """运行应用"""
        self.log_message("奕奕ADB工具箱 v0.1.1 启动成功", "SUCCESS")
        self.log_message("GitHub: https://github.com/yys20071108/-adb-", "INFO")
        
        # 检查管理员权限
        if not self.is_admin:
            self.log_message("警告: 程序未以管理员权限运行，部分功能可能受限", "WARNING")
            
        self.root.mainloop()

if __name__ == "__main__":
    app = ADBToolbox()
    app.run()
