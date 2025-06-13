#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱版本更新脚本
用于自动更新项目中的版本号
"""

import os
import re
import sys
from pathlib import Path

def update_version(new_version):
    """更新项目中的版本号"""
    print(f"🔄 正在更新版本号到 {new_version}...")
    
    # 检查版本号格式
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("❌ 版本号格式错误，应为 x.y.z 格式")
        return False
    
    # 获取项目根目录
    project_root = Path.cwd()
    
    # 需要更新的文件和对应的正则表达式
    files_to_update = {
        "main.py": [
            (r'奕奕ADB工具箱 v\d+\.\d+\.\d+', f'奕奕ADB工具箱 v{new_version}'),
            (r'self\.root\.title$$"奕奕ADB工具箱 v\d+\.\d+\.\d+"$$', f'self.root.title("奕奕ADB工具箱 v{new_version}")'),
            (r'version_label = ttk\.Label\(title_frame, text="v\d+\.\d+\.\d+"', f'version_label = ttk.Label(title_frame, text="v{new_version}"')
        ],
        "setup.py": [
            (r'version="\d+\.\d+\.\d+"', f'version="{new_version}"')
        ],
        "installer.nsi": [
            (r'!define APP_VERSION "\d+\.\d+\.\d+"', f'!define APP_VERSION "{new_version}"'),
            (r'VIProductVersion "\d+\.\d+\.\d+\.\d+"', f'VIProductVersion "{new_version}.0"')
        ],
        "build_and_package.py": [
            (r'self\.version = "\d+\.\d+\.\d+"', f'self.version = "{new_version}"'),
            (r'print$$"🚀 奕奕ADB工具箱 v\d+\.\d+\.\d+ 完整构建脚本"$$', f'print("🚀 奕奕ADB工具箱 v{new_version} 完整构建脚本")')
        ],
        "README.md": [
            (r'# 奕奕ADB工具箱 v\d+\.\d+\.\d+', f'# 奕奕ADB工具箱 v{new_version}'),
            (r'<h1>奕奕ADB工具箱</h1>', f'<h1>奕奕ADB工具箱</h1>'),
            (r'### v\d+\.\d+\.\d+ $$\d{4}-\d{2}-\d{2}$$', f'### v{new_version} ({os.popen("date /t").read().strip()})')
        ]
    }
    
    # 更新文件
    for file_name, patterns in files_to_update.items():
        file_path = project_root / file_name
        if not file_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue
            
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 应用所有替换模式
            updated_content = content
            for pattern, replacement in patterns:
                updated_content = re.sub(pattern, replacement, updated_content)
                
            # 如果内容有变化，写回文件
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ 已更新: {file_path}")
            else:
                print(f"ℹ️  无需更新: {file_path}")
                
        except Exception as e:
            print(f"❌ 更新文件失败: {file_path} - {str(e)}")
            
    print("✅ 版本号更新完成")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 奕奕ADB工具箱版本更新工具")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("❌ 请提供新版本号")
        print("用法: python update_version.py 新版本号")
        print("例如: python update_version.py 0.2.0")
        return False
        
    new_version = sys.argv[1]
    return update_version(new_version)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
