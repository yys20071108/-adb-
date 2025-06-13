; 奕奕ADB工具箱安装程序脚本
; 使用NSIS编译器生成安装程序

!define APP_NAME "奕奕ADB工具箱"
!define APP_VERSION "0.1.1"
!define APP_PUBLISHER "YYS"
!define APP_URL "https://github.com/yys20071108/-adb-"
!define APP_EXE "YysADBToolbox.exe"

; 安装程序属性
Name "${APP_NAME}"
OutFile "YysADBToolbox_v${APP_VERSION}_Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallDir"
RequestExecutionLevel admin

; 现代UI
!include "MUI2.nsh"

; UI设置
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\installer-welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; 版本信息
VIProductVersion "0.1.1.0"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "Comments" "专业的Android调试工具"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "LegalTrademarks" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "LegalCopyright" "© 2024 ${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "FileDescription" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "ProductVersion" "${APP_VERSION}"

; 安装组件
Section "主程序" SecMain
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    ; 复制文件
    File /r "build\exe\*.*"
    
    ; 写入注册表
    WriteRegStr HKLM "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
    
    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; 添加到控制面板程序列表
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
SectionEnd

Section "桌面快捷方式" SecDesktop
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

Section "开始菜单快捷方式" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\卸载${APP_NAME}.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "安装ADB驱动" SecDriver
    ; 创建临时目录
    CreateDirectory "$TEMP\ADBDriver"
    SetOutPath "$TEMP\ADBDriver"
    
    ; 解压驱动安装程序
    File "drivers\android_winusb.inf"
    File "drivers\usb_driver_installer.exe"
    
    ; 运行驱动安装程序
    ExecWait '"$TEMP\ADBDriver\usb_driver_installer.exe" /S'
    
    ; 清理临时文件
    RMDir /r "$TEMP\ADBDriver"
SectionEnd

; 组件描述
LangString DESC_SecMain ${LANG_SIMPCHINESE} "安装${APP_NAME}主程序文件"
LangString DESC_SecDesktop ${LANG_SIMPCHINESE} "在桌面创建快捷方式"
LangString DESC_SecStartMenu ${LANG_SIMPCHINESE} "在开始菜单创建快捷方式"
LangString DESC_SecDriver ${LANG_SIMPCHINESE} "安装Android设备USB驱动"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDriver} $(DESC_SecDriver)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; 卸载程序
Section "Uninstall"
    ; 删除文件
    RMDir /r "$INSTDIR"
    
    ; 删除快捷方式
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; 删除注册表项
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd

; 安装完成后运行程序
Function .onInstSuccess
    MessageBox MB_YESNO "安装已完成。是否立即运行${APP_NAME}？" IDNO NoRun
    Exec "$INSTDIR\${APP_EXE}"
    NoRun:
FunctionEnd
