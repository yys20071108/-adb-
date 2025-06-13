#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建结果测试脚本
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def test_executable():
    """测试可执行文件"""
    print("🧪 测试可执行文件...")
    
    exe_path = Path("build/exe/YysADBToolbox.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"✅ 可执行文件存在: {exe_path}")
    print(f"📏 文件大小: {exe_path.stat().st_size / (1024*1024):.2f} MB")
    
    # 尝试运行程序（非阻塞）
    try:
        print("🚀 尝试启动程序...")
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待2秒看是否能正常启动
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ 程序启动成功")
            process.terminate()  # 终止测试进程
            return True
        else:
            print("❌ 程序启动失败")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"错误信息: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_installer():
    """测试安装程序"""
    print("\n🧪 测试安装程序...")
    
    installer_path = Path("dist").glob("*_Setup.exe")
    installer_files = list(installer_path)
    
    if not installer_files:
        print("⚠️  安装程序不存在（可能NSIS未安装）")
        return True  # 不算失败
    
    installer = installer_files[0]
    print(f"✅ 安装程序存在: {installer}")
    print(f"📏 文件大小: {installer.stat().st_size / (1024*1024):.2f} MB")
    
    return True

def test_portable():
    """测试便携版"""
    print("\n🧪 测试便携版...")
    
    portable_path = Path("dist").glob("*_Portable.zip")
    portable_files = list(portable_path)
    
    if not portable_files:
        print("❌ 便携版不存在")
        return False
    
    portable = portable_files[0]
    print(f"✅ 便携版存在: {portable}")
    print(f"📏 文件大小: {portable.stat().st_size / (1024*1024):.2f} MB")
    
    return True

def main():
    """主测试函数"""
    print("🧪 奕奕ADB工具箱构建结果测试")
    print("=" * 50)
    
    tests = [
        ("可执行文件测试", test_executable),
        ("安装程序测试", test_installer),
        ("便携版测试", test_portable)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！构建成功！")
        return True
    else:
        print("⚠️  部分测试失败，请检查构建过程")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
