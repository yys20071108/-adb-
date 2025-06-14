#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱构建脚本
"""

import sys
from cx_Freeze import setup, Executable
import os

# 构建选项
build_exe_options = {
    "packages": [
        "tkinter", "tkinter.ttk", "tkinter.messagebox", "tkinter.filedialog", "tkinter.scrolledtext",
        "subprocess", "threading", "time", "os", "sys", "json", "zipfile", "pathlib", 
        "webbrowser", "queue", "platform", "re", "tempfile", "shutil", "urllib.request", "ctypes",
        "PIL", "requests", "ttkthemes", "ttkbootstrap"
    ],
    "excludes": ["unittest", "email", "html", "http", "urllib.error", "urllib.parse", "xml", 
                "pydoc", "doctest", "argparse", "difflib", "inspect", "pdb", "profile", "pstats", "timeit"],
    "include_files": [
        ("assets/", "assets/"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE")
    ],
    "optimize": 2,
    "build_exe": "build/exe"
}

# 基础信息
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# 可执行文件配置
executables = [
    Executable(
        "main.py",
        base=base,
        target_name="YysADBToolbox.exe",
        icon="assets/icon.ico",
        shortcut_name="奕奕ADB工具箱",
        shortcut_dir="DesktopFolder"
    )
]

# 设置配置
setup(
    name="YysADBToolbox",
    version="1.0.2",
    description="奕奕ADB工具箱 - 专业的Android调试工具",
    author="YYS",
    author_email="yys20071108@example.com",
    url="https://github.com/yys20071108/-adb-",
    options={"build_exe": build_exe_options},
    executables=executables
)
