@echo off
if not defined UIAP_DEVKIT_ROOT (
  echo [UIAP-E101] start-uiap.cmdから起動してください。
  exit /b 101
)
set "UIAP_POWERSHELL=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%UIAP_POWERSHELL%" (
  echo [UIAP-E104] Windows PowerShell 5.1が見つかりません: %UIAP_POWERSHELL%
  exit /b 104
)
"%UIAP_POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%UIAP_DEVKIT_ROOT%\scripts\versions.ps1"
exit /b %ERRORLEVEL%
