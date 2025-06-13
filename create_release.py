#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱发布脚本
用于创建GitHub发布版本
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
import re

def get_current_version():
    """从main.py获取当前版本号"""
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'奕奕ADB工具箱 v(\d+\.\d+\.\d+)', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"❌ 获取版本号失败: {str(e)}")
    return None

def create_release_notes(version):
    """创建发布说明"""
    release_notes = f"""## 奕奕ADB工具箱 v{version}

### 新功能
- 现代化UI界面升级
- 无线调试支持增强
- 文件管理功能优化
- 快捷命令系统
- 连接问题修复
- ADB环境自动检测和安装
- 主题支持

### 修复问题
- 修复ADB连接稳定性问题
- 修复文件传输中文路径问题
- 修复环境检测逻辑
- 修复WiFi连接问题

### 安装说明
1. 下载 `YysADBToolbox_v{version}_Setup.exe`
2. 以管理员身份运行安装程序
3. 按照向导完成安装
4. 启动程序开始使用

### 系统要求
- Windows 10/11
- .NET Framework 4.7.2+
- USB调试驱动

### 问题反馈
如有问题或建议，请在GitHub Issues中提交

感谢使用奕奕ADB工具箱！
"""
    
    # 保存发布说明到文件
    release_notes_path = Path("dist") / "release_notes.md"
    os.makedirs("dist", exist_ok=True)
    
    with open(release_notes_path, "w", encoding="utf-8") as f:
        f.write(release_notes)
        
    print(f"✅ 发布说明已保存到: {release_notes_path}")
    return release_notes_path

def create_github_release(version, release_notes_path):
    """创建GitHub发布版本"""
    print(f"🚀 正在创建GitHub发布版本 v{version}...")
    
    # 检查是否已登录GitHub CLI
    try:
        result = subprocess.run(["gh", "auth", "status"], 
                              capture_output=True, text=True)
        if "Logged in to" not in result.stdout:
            print("❌ 未登录GitHub CLI，请先运行 'gh auth login'")
            return False
    except FileNotFoundError:
        print("❌ 未安装GitHub CLI，请先安装: https://cli.github.com/")
        return False
        
    # 检查发布文件是否存在
    installer_path = Path("dist") / f"YysADBToolbox_v{version}_Setup.exe"
    portable_path = Path("dist") / f"YysADBToolbox_v{version}_Portable.zip"
    
    if not installer_path.exists() or not portable_path.exists():
        print("❌ 发布文件不存在，请先运行构建脚本")
        return False
        
    # 创建发布标签
    try:
        # 检查标签是否已存在
        result = subprocess.run(["git", "tag"], capture_output=True, text=True)
        if f"v{version}" in result.stdout.split():
            print(f"⚠️  标签 v{version} 已存在，将被覆盖")
            subprocess.run(["git", "tag", "-d", f"v{version}"], check=True)
            
        # 创建新标签
        subprocess.run(["git", "tag", f"v{version}"], check=True)
        print(f"✅ 已创建标签: v{version}")
        
        # 推送标签
        subprocess.run(["git", "push", "origin", f"v{version}"], check=True)
        print(f"✅ 已推送标签到远程仓库")
        
        # 创建发布版本
        with open(release_notes_path, "r", encoding="utf-8") as f:
            release_notes = f.read()
            
        cmd = [
            "gh", "release", "create", f"v{version}",
            "--title", f"奕奕ADB工具箱 v{version}",
            "--notes", release_notes,
            str(installer_path),
            str(portable_path)
        ]
        
        subprocess.run(cmd, check=True)
        print(f"✅ 已创建GitHub发布版本: v{version}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建发布版本失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 创建发布版本时发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 奕奕ADB工具箱发布工具")
    print("=" * 60)
    
    # 获取当前版本
    version = get_current_version()
    if not version:
        print("❌ 无法获取版本号")
        return False
        
    print(f"📦 当前版本: v{version}")
    
    # 确认是否继续
    if input(f"是否创建发布版本 v{version}? (y/n): ").lower() != 'y':
        print("❌ 已取消发布")
        return False
        
    # 创建发布说明
    release_notes_path = create_release_notes(version)
    
    # 创建GitHub发布版本
    if create_github_release(version, release_notes_path):
        print(f"🎉 发布版本 v{version} 创建成功！")
        return True
    else:
        print(f"❌ 发布版本 v{version} 创建失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
