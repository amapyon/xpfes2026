@echo off
setlocal EnableExtensions

set "UIAP_SYSTEM32=%SystemRoot%\System32"
set "UIAP_CMD=%UIAP_SYSTEM32%\cmd.exe"
set "UIAP_POWERSHELL=%UIAP_SYSTEM32%\WindowsPowerShell\v1.0\powershell.exe"
set "UIAP_CHCP=%UIAP_SYSTEM32%\chcp.com"

if not exist "%UIAP_CMD%" (
  echo [UIAP-E104] Windows Command Promptが見つかりません: %UIAP_CMD%
  echo Windows 11 x64のシステムファイルを確認してください。
  echo.
  pause
  exit /b 104
)

if not exist "%UIAP_POWERSHELL%" (
  echo [UIAP-E104] Windows PowerShell 5.1が見つかりません: %UIAP_POWERSHELL%
  echo Windows 11 x64のシステムファイルを確認してください。
  echo.
  pause
  exit /b 104
)

if exist "%UIAP_CHCP%" "%UIAP_CHCP%" 65001 >nul 2>&1

for %%I in ("%~dp0.") do set "UIAP_DEVKIT_ROOT=%%~fI"
set "UIAP_PLATFORM=win"

"%UIAP_POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%UIAP_DEVKIT_ROOT%\scripts\path-check.ps1" -Root "%UIAP_DEVKIT_ROOT%"
if errorlevel 1 (
  echo.
  pause
  exit /b 1
)

set "UIAP_WORKSPACE=%UIAP_DEVKIT_ROOT%\workspace"
set "UIAP_RUNTIME=%UIAP_DEVKIT_ROOT%\runtime\win"
set "UIAP_TOOLCHAIN_BIN=%UIAP_RUNTIME%\toolchain\bin"
set "UIAP_PYTHON=%UIAP_RUNTIME%\python\python.exe"

rem Devkit tools take precedence, but Windows system tools must remain reachable.
set "PATH=%UIAP_DEVKIT_ROOT%\scripts\cmd;%UIAP_RUNTIME%\build-tools\bin;%UIAP_TOOLCHAIN_BIN%;%UIAP_RUNTIME%\python;%UIAP_SYSTEM32%;%SystemRoot%;%UIAP_SYSTEM32%\Wbem;%UIAP_SYSTEM32%\WindowsPowerShell\v1.0;%PATH%"

cd /d "%UIAP_WORKSPACE%"
if errorlevel 1 (
  echo [UIAP-E106] workspaceへ移動できません: %UIAP_WORKSPACE%
  echo.
  pause
  exit /b 106
)

call "%UIAP_DEVKIT_ROOT%\scripts\cmd\welcome.cmd"

"%UIAP_CMD%" /D /E:ON /K
set "UIAP_EXIT_CODE=%ERRORLEVEL%"
if not "%UIAP_EXIT_CODE%"=="0" (
  echo.
  echo [UIAP-E105] 専用Command Promptを起動できませんでした。終了コード: %UIAP_EXIT_CODE%
  echo 実行ファイル: %UIAP_CMD%
  echo.
  pause
)
endlocal & exit /b %UIAP_EXIT_CODE%
