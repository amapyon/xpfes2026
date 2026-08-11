[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

$root = $env:UIAP_DEVKIT_ROOT
$runtime = $env:UIAP_RUNTIME
$workspace = $env:UIAP_WORKSPACE
$pass = 0; $warn = 0; $fail = 0
function Pass([string]$message) { $script:pass++; Write-Host "[PASS] $message" -ForegroundColor Green }
function Warn([string]$message) { $script:warn++; Write-Host "[WARN] $message" -ForegroundColor Yellow }
function Fail([string]$message) { $script:fail++; Write-Host "[FAIL] $message" -ForegroundColor Red }
function CheckFile([string]$path, [string]$name) { if (Test-Path -LiteralPath $path -PathType Leaf) { Pass $name } else { Fail "$name がありません: $path" } }

Write-Host 'UIAP unified repository doctor (Windows)' -ForegroundColor Cyan
if ($env:UIAP_PLATFORM -eq 'win') { Pass 'UIAP_PLATFORM=win' } else { Fail "UIAP_PLATFORM=$env:UIAP_PLATFORM" }
if ([Environment]::Is64BitOperatingSystem) { Pass '64bit Windows' } else { Fail '64bit Windowsではありません' }
CheckFile (Join-Path $root 'VERSION') 'VERSION'
CheckFile (Join-Path $root 'config\win\bootstrap.lock.json') 'Windows bootstrap lock'
CheckFile (Join-Path $runtime 'build-tools\bin\make.exe') 'GNU Make'
CheckFile (Join-Path $runtime 'toolchain\bin\riscv-none-elf-gcc.exe') 'RISC-V GCC'
CheckFile (Join-Path $runtime 'python\python.exe') 'Python'
CheckFile (Join-Path $workspace 'deps\ch32fun\ch32fun\ch32fun.mk') 'ch32fun'
CheckFile (Join-Path $workspace 'deps\rv003usb\rv003usb\rv003usb.c') 'rv003usb'
CheckFile (Join-Path $runtime 'bin\minichlink.exe') 'minichlink'

$exerciseNames = @('00_onboard_led_blink', '01_macro_keyboard', '02_rotary_cursor_size', '03_rotary_cursor_haptic')
foreach ($name in $exerciseNames) {
    $exercise = Join-Path $workspace "exercises\$name"
    CheckFile (Join-Path $exercise 'Makefile') "$name Makefile"
    $sourceName = switch ($name) {
        '00_onboard_led_blink' { 'onboard_led_blink.c' }
        '01_macro_keyboard' { 'macro_keyboard.c' }
        '02_rotary_cursor_size' { 'rotary_cursor_size.c' }
        '03_rotary_cursor_haptic' { 'rotary_cursor_size.c' }
    }
    CheckFile (Join-Path $exercise $sourceName) "$name common firmware"
    if ($name -ne '00_onboard_led_blink') { CheckFile (Join-Path $exercise 'usb_config.h') "$name common USB configuration" }
}

$make = Join-Path $runtime 'build-tools\bin\make.exe'
if (Test-Path -LiteralPath $make -PathType Leaf) {
    foreach ($name in $exerciseNames) {
        $exercise = Join-Path $workspace "exercises\$name"
        Push-Location $exercise
        try {
            & $make -n all *> $null
            if ($LASTEXITCODE -eq 0) { Pass "$name make -n" } else { Fail "$name make -n" }
            & $make -n flash *> $null
            if ($LASTEXITCODE -eq 0) { Pass "$name make -n flash" } else { Fail "$name make -n flash" }
        } finally { Pop-Location }
    }
}

$python = Join-Path $runtime 'python\python.exe'
if (Test-Path -LiteralPath $python -PathType Leaf) {
    & $python (Join-Path $workspace 'exercises\01_macro_keyboard\host\hidcheck.py') --self-test
    if ($LASTEXITCODE -eq 0) { Pass 'Macro keyboard host self-test' } else { Fail 'Macro keyboard host self-test' }
    & $python (Join-Path $workspace 'exercises\02_rotary_cursor_size\host\cursor_size_host.py') self-test
    if ($LASTEXITCODE -eq 0) { Pass 'Rotary cursor host self-test' } else { Fail 'Rotary cursor host self-test' }
    & $python (Join-Path $workspace 'exercises\03_rotary_cursor_haptic\host\cursor_size_host.py') self-test
    if ($LASTEXITCODE -eq 0) { Pass 'Rotary haptic host self-test' } else { Fail 'Rotary haptic host self-test' }
}

Warn '実機書き込みとHID動作は、接続したUIAPduinoでmake flash、make appを実行して確認してください。'
Write-Host "PASS=$pass WARN=$warn FAIL=$fail"
if ($fail -gt 0) { exit 299 }
exit 0
