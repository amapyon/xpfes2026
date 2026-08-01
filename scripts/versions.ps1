[CmdletBinding()]
param()
$ErrorActionPreference='Continue'
$root=$env:UIAP_DEVKIT_ROOT
Write-Host (Get-Content -LiteralPath (Join-Path $root 'VERSION') -Raw)
Write-Host 'curl:'
& (Join-Path $env:SystemRoot 'System32\curl.exe') --version | Select-Object -First 1
Write-Host 'make:'
& (Join-Path $env:UIAP_RUNTIME 'build-tools\bin\make.exe') --version | Select-Object -First 1
Write-Host 'gcc:'
& (Join-Path $env:UIAP_RUNTIME 'toolchain\bin\riscv-none-elf-gcc.exe') --version | Select-Object -First 1
Write-Host 'python:'
& (Join-Path $env:UIAP_RUNTIME 'python\python.exe') --version
exit 0
