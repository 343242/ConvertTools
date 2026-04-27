!include "MUI2.nsh"

!define APP_NAME "ConvertTools"
!define APP_VERSION "0.1.0"
!define APP_PUBLISHER "ConvertTools"
!define APP_EXE "ConvertTools.exe"
!define APP_DIR "dist\ConvertTools"
!define APP_UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

Name "${APP_NAME}"
OutFile "dist\ConvertTools-Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" ""
RequestExecutionLevel admin

InstType "完整安装"
InstType "最小安装"
InstType "自定义安装"

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "SimpChinese"

Section "!核心文件" SecCore
  SectionIn RO 1 2 3
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  File /r "${APP_DIR}\*"

  WriteRegStr HKLM "Software\${APP_NAME}" "" $INSTDIR
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

SectionGroup /e "快捷方式" SecShortcuts
Section "开始菜单快捷方式" SecStartMenu
  SectionIn 1 3
  SetShellVarContext all
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\卸载 ${APP_NAME}.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "桌面快捷方式" SecDesktop
  SectionIn 1 3
  SetShellVarContext all
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
SectionEnd
SectionGroupEnd

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "程序核心文件。必须安装。"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} "可选快捷方式组件。"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "创建开始菜单中的程序和卸载快捷方式。"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "在桌面创建程序快捷方式。"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
  SetShellVarContext all
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\卸载 ${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR"

  DeleteRegKey HKLM "Software\${APP_NAME}"
  DeleteRegKey HKLM "${APP_UNINSTALL_KEY}"
SectionEnd
