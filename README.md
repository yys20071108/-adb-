# 奕奕ADB工具箱 v0.1

<div align="center">
  <img src="assets/icon.png" alt="奕奕ADB工具箱" width="128" height="128">
  
  <h1>奕奕ADB工具箱</h1>
  <p>专业的Android调试工具集</p>
  
  [![GitHub release](https://img.shields.io/github/release/yys20071108/-adb-.svg)](https://github.com/yys20071108/-adb-/releases)
  [![GitHub downloads](https://img.shields.io/github/downloads/yys20071108/-adb-/total.svg)](https://github.com/yys20071108/-adb-/releases)
  [![License](https://img.shields.io/github/license/yys20071108/-adb-.svg)](LICENSE)
</div>

## 📋 项目简介

奕奕ADB工具箱是一个功能丰富、界面现代的Android调试工具集，为Android开发者和爱好者提供便捷的设备管理和调试功能。

## ✨ 主要特性

### 🔌 设备连接管理
- USB连接支持
- WiFi无线连接
- 设备状态实时监控
- 多设备管理

### 🛠️ 基础工具 (12项)
- 设备重启控制
- 屏幕截图/录制
- 设备信息获取
- 应用列表查看
- 系统进程监控
- 内存/CPU信息
- 存储空间查看
- 网络连接状态

### 🚀 高级功能
- Root权限管理
- 系统属性操作
- 性能监控工具
- 电池信息查看

### 📁 文件管理
- 双向文件传输
- 图形化文件浏览
- 批量文件操作

### 📱 应用管理
- APK安装/卸载
- 应用启动/停止
- 应用数据清除
- 包名查询

### ⚙️ 系统工具
- 系统服务控制
- 开发者选项管理
- 系统设置调整

## 🖥️ 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.9+ (开发环境)
- **内存**: 最少 2GB RAM
- **存储**: 100MB 可用空间
- **其他**: USB调试驱动

## 📦 安装方法

### 方法一：下载安装包 (推荐)
1. 前往 [Releases](https://github.com/yys20071108/-adb-/releases) 页面
2. 下载最新版本的 `YysADBToolbox_v*_Setup.exe`
3. 以管理员身份运行安装程序
4. 按照安装向导完成安装

### 方法二：源码运行
\`\`\`bash
# 克隆项目
git clone https://github.com/yys20071108/-adb-.git
cd -adb-

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
\`\`\`

## 🚀 快速开始

1. **连接设备**
   - 启用手机的USB调试模式
   - 使用USB线连接电脑和手机
   - 点击"连接设备"按钮

2. **WiFi连接** (可选)
   - 确保手机和电脑在同一网络
   - 输入手机IP地址和端口(默认5555)
   - 点击连接

3. **使用工具**
   - 选择相应的功能选项卡
   - 点击对应的工具按钮
   - 在控制台查看执行结果

## 📸 界面预览

### 主界面
- 现代化的GUI设计
- 直观的选项卡布局
- 实时的设备状态显示

### 功能模块
- **基础工具**: 常用ADB命令的图形化操作
- **高级功能**: Root管理、系统属性等高级操作
- **文件管理**: 可视化的文件传输界面
- **系统工具**: 应用管理和系统设置
- **控制台**: 实时命令执行和日志输出

## 🔧 开发构建

### 环境准备
\`\`\`bash
# 安装构建依赖
pip install cx_Freeze

# 构建可执行文件
python setup.py build

# 安装NSIS (Windows)
choco install nsis

# 创建安装程序
makensis installer.nsi
\`\`\`

### 项目结构
\`\`\`
-adb-/
├── main.py              # 主程序入口
├── setup.py             # 构建脚本
├── installer.nsi        # 安装程序脚本
├── requirements.txt     # 依赖包列表
├── assets/              # 资源文件
│   └── icon.ico        # 应用图标
├── .github/             # GitHub Actions
│   └── workflows/
│       └── build.yml   # 自动构建配置
└── README.md           # 项目说明
\`\`\`

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交Issue
- 详细描述问题或建议
- 提供复现步骤
- 附上系统环境信息

### 提交代码
1. Fork本项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- 感谢所有贡献者的支持
- 感谢开源社区提供的工具和库
- 特别感谢Android开发团队提供ADB工具

## 📞 联系方式

- **GitHub**: [@yys20071108](https://github.com/yys20071108)
- **项目地址**: https://github.com/yys20071108/-adb-
- **问题反馈**: [GitHub Issues](https://github.com/yys20071108/-adb-/issues)

## 🔄 更新日志

### v0.1 (2024-12-06)
- 🎉 首次发布
- ✅ 基础ADB工具集成
- ✅ 现代化GUI界面
- ✅ 设备连接管理
- ✅ 文件传输功能
- ✅ 应用管理工具
- ✅ 自动构建和发布

---

<div align="center">
  <p>如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！</p>
  <p>Made with ❤️ by YYS</p>
</div>
