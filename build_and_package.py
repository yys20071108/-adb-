#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱完整构建和打包脚本
作者: YYS
GitHub: https://github.com/yys20071108/-adb-
"""

import os
import sys
import subprocess
import shutil
import zipfile
import hashlib
import time
from pathlib import Path
import platform

class ADBToolboxBuilder:
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.assets_dir = self.project_root / "assets"
        self.version = "0.1.1"
        self.app_name = "YysADBToolbox"
        
        # 构建统计
        self.start_time = time.time()
        self.steps_completed = 0
        self.total_steps = 10
        
    def print_header(self):
        """打印构建头部信息"""
        print("=" * 80)
        print("🚀 奕奕ADB工具箱 v0.1.1 完整构建脚本")
        print("=" * 80)
        print(f"📁 项目目录: {self.project_root}")
        print(f"🖥️  操作系统: {platform.system()} {platform.release()}")
        print(f"🐍 Python版本: {sys.version}")
        print(f"⏰ 构建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
    def run_command(self, command, description="", shell=True):
        """执行命令并输出结果"""
        print(f"\n🔄 {description or command}")
        print("-" * 60)
        
        try:
            if isinstance(command, list):
                result = subprocess.run(command, check=True, capture_output=True, 
                                      text=True, shell=shell, encoding='utf-8', errors='ignore')
            else:
                result = subprocess.run(command, shell=shell, check=True, 
                                      capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.stdout:
                print("📤 输出:")
                print(result.stdout)
            
            print("✅ 执行成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print("❌ 执行失败")
            if e.stdout:
                print("📤 标准输出:")
                print(e.stdout)
            if e.stderr:
                print("📤 错误输出:")
                print(e.stderr)
            return False
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
            return False
    
    def update_progress(self, step_name):
        """更新进度"""
        self.steps_completed += 1
        progress = (self.steps_completed / self.total_steps) * 100
        elapsed = time.time() - self.start_time
        
        print(f"\n📊 进度: {self.steps_completed}/{self.total_steps} ({progress:.1f}%)")
        print(f"⏱️  已用时间: {elapsed:.1f}秒")
        print(f"✨ 完成步骤: {step_name}")
        
    def clean_build_dirs(self):
        """清理构建目录"""
        print("\n🧹 清理构建目录...")
        
        dirs_to_clean = [
            self.build_dir,
            self.dist_dir,
            self.project_root / "__pycache__",
            self.project_root / "*.egg-info"
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                if dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    print(f"🗑️  已删除目录: {dir_path}")
                else:
                    # 处理通配符
                    for file_path in self.project_root.glob(dir_path.name):
                        if file_path.is_dir():
                            shutil.rmtree(file_path)
                        else:
                            file_path.unlink()
                        print(f"🗑️  已删除: {file_path}")
        
        self.update_progress("清理构建目录")
        
    def create_assets(self):
        """创建资源文件"""
        print("\n🎨 创建资源文件...")
        
        # 创建assets目录
        self.assets_dir.mkdir(exist_ok=True)
        
        # 创建简单的ICO图标文件（占位符）
        icon_path = self.assets_dir / "icon.ico"
        if not icon_path.exists():
            print("📝 创建占位图标文件...")
            # 创建一个最小的ICO文件头
            ico_header = b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00\x16\x00\x00\x00'
            ico_data = ico_header + b'\x00' * (0x568 - len(ico_header))
            
            with open(icon_path, 'wb') as f:
                f.write(ico_data)
            print(f"✅ 图标文件已创建: {icon_path}")
            
        # 创建logo文件
        logo_path = self.assets_dir / "logo.png"
        if not logo_path.exists():
            print("📝 创建占位logo文件...")
            # 创建一个简单的PNG文件头
            png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4'
            with open(logo_path, 'wb') as f:
                f.write(png_header + b'\x00' * 100)  # 简化的PNG文件
            print(f"✅ Logo文件已创建: {logo_path}")
            
        # 创建安装程序图片
        installer_welcome = self.assets_dir / "installer-welcome.bmp"
        installer_header = self.assets_dir / "installer-header.bmp"
        
        if not installer_welcome.exists():
            print("📝 创建安装程序欢迎图片...")
            # 创建一个简单的BMP文件头
            bmp_header = b'BM'
            with open(installer_welcome, 'wb') as f:
                f.write(bmp_header + b'\x00' * 100)  # 简化的BMP文件
            print(f"✅ 安装程序欢迎图片已创建: {installer_welcome}")
            
        if not installer_header.exists():
            print("📝 创建安装程序头部图片...")
            with open(installer_header, 'wb') as f:
                f.write(bmp_header + b'\x00' * 100)  # 简化的BMP文件
            print(f"✅ 安装程序头部图片已创建: {installer_header}")
        
        # 创建其他必要的资源文件
        readme_path = self.assets_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""
奕奕ADB工具箱 v0.1.1
==================

感谢使用奕奕ADB工具箱！

使用说明:
1. 确保已安装ADB驱动
2. 启用手机USB调试模式
3. 连接手机到电脑
4. 运行程序开始使用

更多信息请访问:
GitHub: https://github.com/yys20071108/-adb-

如有问题请提交Issue反馈。
            """)
        
        self.update_progress("创建资源文件")
        
    def check_dependencies(self):
        """检查和安装依赖"""
        print("\n📦 检查Python依赖...")
        
        # 检查requirements.txt是否存在
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            print("❌ requirements.txt文件不存在")
            return False
        
        # 安装依赖
        if not self.run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                               "安装Python依赖包", shell=False):
            print("❌ 依赖安装失败")
            return False
        
        # 检查关键依赖
        critical_packages = ['cx_Freeze', 'tkinter', 'PIL', 'requests']
        for package in critical_packages:
            try:
                if package == 'tkinter':
                    import tkinter
                elif package == 'cx_Freeze':
                    import cx_Freeze
                elif package == 'PIL':
                    from PIL import Image
                elif package == 'requests':
                    import requests
                print(f"✅ {package} 已安装")
            except ImportError:
                print(f"❌ {package} 未安装")
                return False
        
        self.update_progress("检查依赖")
        return True
        
    def create_setup_script(self):
        """创建setup.py脚本"""
        print("\n📝 创建构建脚本...")
        
        setup_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奕奕ADB工具箱构建脚本 - 自动生成
"""

import sys
from cx_Freeze import setup, Executable
import os

# 构建选项
build_exe_options = {{
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
    "build_exe": "build/exe",
    "silent": True
}}

# 基础信息
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# 可执行文件配置
executables = [
    Executable(
        "main.py",
        base=base,
        target_name="{self.app_name}.exe",
        icon="assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
        shortcut_name="奕奕ADB工具箱",
        shortcut_dir="DesktopFolder"
    )
]

# 设置配置
setup(
    name="{self.app_name}",
    version="{self.version}",
    description="奕奕ADB工具箱 - 专业的Android调试工具",
    author="YYS",
    author_email="yys20071108@example.com",
    url="https://github.com/yys20071108/-adb-",
    options={{"build_exe": build_exe_options}},
    executables=executables
)
'''
        
        setup_path = self.project_root / "setup_auto.py"
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        
        print(f"✅ 构建脚本已创建: {setup_path}")
        self.update_progress("创建构建脚本")
        return True
        
    def build_executable(self):
        """构建可执行文件"""
        print("\n🔨 构建可执行文件...")
        
        if not self.run_command([sys.executable, "setup_auto.py", "build"], 
                               "使用cx_Freeze构建EXE", shell=False):
            return False
        
        # 检查构建结果
        exe_path = self.build_dir / "exe" / f"{self.app_name}.exe"
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ EXE文件构建成功: {exe_path}")
            print(f"📏 文件大小: {file_size:.2f} MB")
        else:
            print("❌ EXE文件构建失败")
            return False
        
        self.update_progress("构建可执行文件")
        return True
        
    def create_installer_script(self):
        """创建NSIS安装脚本"""
        print("\n📜 创建安装程序脚本...")
        
        nsis_content = f'''
; 奕奕ADB工具箱安装程序脚本 - 自动生成
!define APP_NAME "奕奕ADB工具箱"
!define APP_VERSION "{self.version}"
!define APP_PUBLISHER "YYS"
!define APP_URL "https://github.com/yys20071108/-adb-"
!define APP_EXE "{self.app_name}.exe"

Name "${{APP_NAME}}"
OutFile "dist\\{self.app_name}_v{self.version}_Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
RequestExecutionLevel admin

!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\\installer-welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "SimpChinese"

Section "主程序" SecMain
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /r "build\\exe\\*.*"
    
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "InstallDir" "$INSTDIR"
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
SectionEnd

Section "Uninstall"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\${{APP_NAME}}"
SectionEnd

Function .onInstSuccess
    MessageBox MB_YESNO "安装已完成。是否立即运行${{APP_NAME}}？" IDNO NoRun
    Exec "$INSTDIR\\${{APP_EXE}}"
    NoRun:
FunctionEnd
'''
        
        nsis_path = self.project_root / "installer_auto.nsi"
        with open(nsis_path, 'w', encoding='utf-8') as f:
            f.write(nsis_content)
        
        print(f"✅ NSIS脚本已创建: {nsis_path}")
        self.update_progress("创建安装脚本")
        return True
        
    def create_installer(self):
        """创建安装程序"""
        print("\n📦 创建安装程序...")
        
        # 创建dist目录
        self.dist_dir.mkdir(exist_ok=True)
        
        # 检查NSIS是否可用
        nsis_commands = ['makensis', 'makensis.exe']
        nsis_found = False
        
        for cmd in nsis_commands:
            try:
                result = subprocess.run([cmd, '/VERSION'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    nsis_found = True
                    print(f"✅ 找到NSIS: {cmd}")
                    if self.run_command([cmd, "installer_auto.nsi"], "创建NSIS安装程序", shell=False):
                        installer_path = self.dist_dir / f"{self.app_name}_v{self.version}_Setup.exe"
                        if installer_path.exists():
                            file_size = installer_path.stat().st_size / (1024 * 1024)  # MB
                            print(f"✅ 安装程序创建成功: {installer_path}")
                            print(f"📏 文件大小: {file_size:.2f} MB")
                            self.update_progress("创建安装程序")
                            return True
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        if not nsis_found:
            print("⚠️  NSIS未安装，跳过安装程序创建")
            print("💡 可以从 https://nsis.sourceforge.io/Download 下载NSIS")
            self.update_progress("跳过安装程序")
            return True
        
        return False
        
    def create_portable_version(self):
        """创建便携版"""
        print("\n📁 创建便携版...")
        
        exe_dir = self.build_dir / "exe"
        if not exe_dir.exists():
            print("❌ 可执行文件目录不存在")
            return False
        
        # 创建便携版ZIP
        portable_zip = self.dist_dir / f"{self.app_name}_v{self.version}_Portable.zip"
        
        with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加所有exe目录下的文件
            for file_path in exe_dir.rglob('*'):
                if file_path.is_file():
                    arc_name = file_path.relative_to(exe_dir)
                    zf.write(file_path, arc_name)
                    print(f"📄 添加文件: {arc_name}")
            
            # 添加说明文件
            readme_content = f"""
奕奕ADB工具箱 v{self.version} 便携版
=====================================

使用说明:
1. 解压到任意目录
2. 双击 {self.app_name}.exe 运行
3. 首次运行会自动检测ADB环境

注意事项:
- 需要安装ADB驱动
- 建议以管理员身份运行
- 支持Windows 10/11

更多信息:
GitHub: https://github.com/yys20071108/-adb-

版本: {self.version}
构建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            zf.writestr("使用说明.txt", readme_content.encode('utf-8'))
        
        if portable_zip.exists():
            file_size = portable_zip.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 便携版创建成功: {portable_zip}")
            print(f"📏 文件大小: {file_size:.2f} MB")
        
        self.update_progress("创建便携版")
        return True
        
    def calculate_checksums(self):
        """计算文件校验和"""
        print("\n🔐 计算文件校验和...")
        
        checksum_file = self.dist_dir / "checksums.txt"
        checksums = []
        
        # 计算所有dist目录下文件的校验和
        for file_path in self.dist_dir.glob('*'):
            if file_path.is_file() and file_path.name != "checksums.txt":
                # 计算SHA256
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                
                checksum = sha256_hash.hexdigest()
                file_size = file_path.stat().st_size
                checksums.append(f"{checksum}  {file_path.name}  ({file_size} bytes)")
                print(f"🔑 {file_path.name}: {checksum[:16]}...")
        
        # 写入校验和文件
        with open(checksum_file, 'w', encoding='utf-8') as f:
            f.write(f"奕奕ADB工具箱 v{self.version} 文件校验和\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            for checksum in checksums:
                f.write(checksum + "\n")
        
        print(f"✅ 校验和文件已创建: {checksum_file}")
        self.update_progress("计算校验和")
        return True
        
    def cleanup_temp_files(self):
        """清理临时文件"""
        print("\n🧹 清理临时文件...")
        
        temp_files = [
            "setup_auto.py",
            "installer_auto.nsi"
        ]
        
        for temp_file in temp_files:
            temp_path = self.project_root / temp_file
            if temp_path.exists():
                temp_path.unlink()
                print(f"🗑️  已删除: {temp_file}")
        
        self.update_progress("清理临时文件")
        
    def print_summary(self):
        """打印构建总结"""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("🎉 构建完成总结")
        print("=" * 80)
        print(f"⏱️  总用时: {elapsed_time:.1f}秒")
        print(f"📊 完成步骤: {self.steps_completed}/{self.total_steps}")
        
        print("\n📁 生成的文件:")
        if self.dist_dir.exists():
            for file_path in self.dist_dir.glob('*'):
                if file_path.is_file():
                    file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                    print(f"  📄 {file_path.name} ({file_size:.2f} MB)")
        
        print(f"\n📂 构建目录: {self.build_dir}")
        print(f"📂 发布目录: {self.dist_dir}")
        
        print("\n🚀 下一步操作:")
        print("1. 测试生成的可执行文件")
        print("2. 运行安装程序进行测试")
        print("3. 提交代码到GitHub")
        print("4. 创建Release发布")
        
        print("\n💡 使用建议:")
        print("- 在不同Windows版本上测试")
        print("- 检查ADB功能是否正常")
        print("- 验证文件传输功能")
        print("- 测试应用管理功能")
        
        print("=" * 80)
        
    def build(self):
        """执行完整构建流程"""
        try:
            self.print_header()
            
            # 构建步骤
            steps = [
                ("清理构建目录", self.clean_build_dirs),
                ("创建资源文件", self.create_assets),
                ("检查依赖", self.check_dependencies),
                ("创建构建脚本", self.create_setup_script),
                ("构建可执行文件", self.build_executable),
                ("创建安装脚本", self.create_installer_script),
                ("创建安装程序", self.create_installer),
                ("创建便携版", self.create_portable_version),
                ("计算校验和", self.calculate_checksums),
                ("清理临时文件", self.cleanup_temp_files)
            ]
            
            success_count = 0
            for step_name, step_func in steps:
                print(f"\n{'='*20} 步骤 {success_count + 1}/{len(steps)}: {step_name} {'='*20}")
                
                if step_func():
                    success_count += 1
                else:
                    print(f"❌ 步骤失败: {step_name}")
                    break
            
            # 构建结果
            if success_count == len(steps):
                print(f"\n🎉 构建成功！所有 {len(steps)} 个步骤都已完成")
                self.print_summary()
                return True
            else:
                print(f"\n❌ 构建失败！完成了 {success_count}/{len(steps)} 个步骤")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️  构建被用户中断")
            return False
        except Exception as e:
            print(f"\n❌ 构建过程中发生异常: {str(e)}")
            return False

def main():
    """主函数"""
    print("🚀 启动奕奕ADB工具箱构建程序...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        sys.exit(1)
    
    # 检查是否在项目根目录
    if not Path("main.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 创建构建器并执行构建
    builder = ADBToolboxBuilder()
    success = builder.build()
    
    if success:
        print("\n🎊 恭喜！奕奕ADB工具箱构建成功！")
        sys.exit(0)
    else:
        print("\n😞 构建失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
