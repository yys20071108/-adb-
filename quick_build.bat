@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 奕奕ADB工具箱快速构建脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)

:: 检查主程序文件
if not exist "main.py" (
    echo ❌ 未找到main.py文件
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

:: 升级pip
echo 📦 升级pip...
python -m pip install --upgrade pip

:: 安装构建依赖
echo 📦 安装构建依赖...
python -m pip install cx_Freeze Pillow requests psutil

:: 执行构建
echo.
echo 🔨 开始构建...
echo.
python build_and_package.py

:: 检查构建结果
if exist "dist\" (
    echo.
    echo ✅ 构建完成！
    echo 📁 生成的文件位于 dist\ 目录
    echo.
    dir /b dist\
    echo.
    echo 🎉 构建成功！可以开始测试了
) else (
    echo.
    echo ❌ 构建失败，请检查错误信息
)

echo.
pause
