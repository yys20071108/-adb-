#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱自动构建脚本
用于本地构建和测试
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """执行命令并输出结果"""
    print(f"\n{'='*50}")
    print(f"执行: {description or command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print("输出:")
            print(result.stdout)
        print("✅ 执行成功")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 执行失败")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False

def create_assets():
    """创建资源文件夹和占位文件"""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # 创建占位图标文件
    icon_path = assets_dir / "icon.ico"
    if not icon_path.exists():
        print("创建占位图标文件...")
        # 这里应该放置实际的图标文件
        icon_path.write_bytes(b"")  # 占位符
        
def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除: {dir_name}")

def install_dependencies():
    """安装依赖包"""
    print("安装Python依赖包...")
    return run_command("pip install -r requirements.txt", "安装依赖包")

def build_executable():
    """构建可执行文件"""
    print("构建可执行文件...")
    return run_command("python setup.py build", "构建EXE文件")

def create_installer():
    """创建安装程序"""
    print("创建安装程序...")
    
    # 检查NSIS是否安装
    try:
        subprocess.run("makensis", shell=True, check=True, 
                      capture_output=True, text=True)
    except subprocess.CalledProcessError:
        print("❌ NSIS未安装，请先安装NSIS")
        print("下载地址: https://nsis.sourceforge.io/Download")
        return False
        
    return run_command("makensis installer.nsi", "创建安装程序")

def main():
    """主函数"""
    print("🚀 奕奕ADB工具箱构建脚本 v0.1")
    print("作者: YYS")
    print("GitHub: https://github.com/yys20071108/-adb-")
    
    # 检查Python版本
    if sys.version_info < (3, 9):
        print("❌ 需要Python 3.9或更高版本")
        sys.exit(1)
        
    # 构建步骤
    steps = [
        ("清理构建文件", clean_build),
        ("创建资源文件", create_assets),
        ("安装依赖包", install_dependencies),
        ("构建可执行文件", build_executable),
        ("创建安装程序", create_installer)
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n🔄 步骤 {success_count + 1}/{total_steps}: {step_name}")
        
        if callable(step_func):
            if step_func():
                success_count += 1
            else:
                print(f"❌ 步骤失败: {step_name}")
                break
        else:
            success_count += 1
            
    # 构建结果
    print(f"\n{'='*60}")
    print(f"构建完成: {success_count}/{total_steps} 步骤成功")
    
    if success_count == total_steps:
        print("🎉 构建成功！")
        print("\n生成的文件:")
        print("- build/exe/ (可执行文件)")
        print("- YysADBToolbox_v0.1_Setup.exe (安装程序)")
        
        print("\n下一步:")
        print("1. 测试可执行文件")
        print("2. 运行安装程序测试")
        print("3. 提交代码到GitHub")
        print("4. 创建Release标签触发自动构建")
    else:
        print("❌ 构建失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
