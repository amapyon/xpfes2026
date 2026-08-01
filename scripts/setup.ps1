[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($env:UIAP_DEVKIT_ROOT)) {
    Write-Host '[UIAP-E101] UIAP_DEVKIT_ROOTが設定されていません。start-uiap.cmdから起動してください。' -ForegroundColor Red
    exit 101
}

$root = $env:UIAP_DEVKIT_ROOT
$windowsPowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $windowsPowerShell -PathType Leaf)) {
    Write-Host "[UIAP-E104] Windows PowerShell 5.1が見つかりません: $windowsPowerShell" -ForegroundColor Red
    exit 104
}
& $windowsPowerShell -NoLogo -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'scripts\path-check.ps1') -Root $root -Quiet
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

. (Join-Path $root 'scripts\download-file.ps1')
Add-Type -AssemblyName System.IO.Compression.FileSystem

$runtime = $env:UIAP_RUNTIME
$downloads = Join-Path $runtime 'downloads'
$state = Join-Path $root '.state\win'
$logs = Join-Path $root 'logs\win'
New-Item -ItemType Directory -Path $downloads, $state, $logs -Force | Out-Null
$logPath = Join-Path $logs ("setup-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
"UIAP setup log $(Get-Date -Format 'o')" | Set-Content -LiteralPath $logPath -Encoding UTF8

function Expand-UiapZip {
    param([string]$Archive, [string]$Destination)
    if (Test-Path -LiteralPath $Destination) { Remove-Item -LiteralPath $Destination -Recurse -Force }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    [System.IO.Compression.ZipFile]::ExtractToDirectory($Archive, $Destination)
}

function Get-UiapContentRoot {
    param([string]$ExpandedPath)
    $entries = @(Get-ChildItem -LiteralPath $ExpandedPath -Force)
    if ($entries.Count -eq 1 -and $entries[0].PSIsContainer) { return $entries[0].FullName }
    return $ExpandedPath
}

function Test-UiapInstallMarker {
    param([string]$Destination, [string]$Sha256)
    $marker = Join-Path $Destination '.uiap-component.sha256'
    return (Test-Path -LiteralPath $marker -PathType Leaf) -and ((Get-Content -LiteralPath $marker -Raw).Trim() -eq $Sha256)
}

function Set-UiapInstallMarker {
    param([string]$Destination, [string]$Sha256)
    $Sha256 | Set-Content -LiteralPath (Join-Path $Destination '.uiap-component.sha256') -Encoding ASCII
}

function Install-UiapXpack {
    param($Component, [string]$Archive)
    $destination = Join-Path $root ($Component.destination -replace '/', '\\')
    if (Test-UiapInstallMarker $destination $Component.sha256) {
        Write-Host "[PASS] インストール済み: $($Component.name)"
        return
    }
    $stage = Join-Path $state ("stage-{0}" -f $Component.id)
    Expand-UiapZip $Archive $stage
    $contentRoot = Get-UiapContentRoot $stage
    if (Test-Path -LiteralPath $destination) { Remove-Item -LiteralPath $destination -Recurse -Force }
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-Item -Path (Join-Path $contentRoot '*') -Destination $destination -Recurse -Force
    Set-UiapInstallMarker $destination $Component.sha256
    Remove-Item -LiteralPath $stage -Recurse -Force
    Write-Host "[PASS] 展開完了: $($Component.name)"
}

function Install-UiapPython {
    param($Component, [string]$Archive)
    $destination = Join-Path $root ($Component.destination -replace '/', '\\')
    if (Test-UiapInstallMarker $destination $Component.sha256) {
        Write-Host "[PASS] インストール済み: $($Component.name)"
        return
    }
    Expand-UiapZip $Archive $destination
    $pth = Get-ChildItem -LiteralPath $destination -Filter 'python*._pth' | Select-Object -First 1
    if ($null -eq $pth) { throw '[UIAP-E130] Pythonの._pthファイルが見つかりません。' }
    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in (Get-Content -LiteralPath $pth.FullName)) {
        if ($line.Trim() -eq '#import site') { continue }
        $lines.Add($line)
    }
    if (-not ($lines -contains 'Lib\site-packages')) { $lines.Add('Lib\site-packages') }
    $lines.Add('import site')
    Set-Content -LiteralPath $pth.FullName -Value $lines -Encoding ASCII
    New-Item -ItemType Directory -Path (Join-Path $destination 'Lib\site-packages') -Force | Out-Null
    Set-UiapInstallMarker $destination $Component.sha256
    Write-Host "[PASS] 展開完了: $($Component.name)"
}

function Install-UiapPythonWheel {
    param($Component, [string]$Archive)
    $destination = Join-Path $root ($Component.destination -replace '/', '\\')
    $marker = Join-Path $destination (".uiap-{0}.sha256" -f $Component.id)
    if ((Test-Path -LiteralPath $marker) -and ((Get-Content -LiteralPath $marker -Raw).Trim() -eq $Component.sha256)) {
        Write-Host "[PASS] インストール済み: $($Component.name)"
        return
    }
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    $stage = Join-Path $state ("stage-{0}" -f $Component.id)
    Expand-UiapZip $Archive $stage
    Copy-Item -Path (Join-Path $stage '*') -Destination $destination -Recurse -Force
    $Component.sha256 | Set-Content -LiteralPath $marker -Encoding ASCII
    Remove-Item -LiteralPath $stage -Recurse -Force
    Write-Host "[PASS] 配置完了: $($Component.name)"
}

function Install-UiapCh32funTestSubset {
    param($Component, [string]$Archive)
    $destination = Join-Path $root ($Component.destination -replace '/', '\\')
    if (Test-UiapInstallMarker $destination $Component.sha256) {
        Write-Host "[PASS] インストール済み: $($Component.name)"
        return
    }
    $stage = Join-Path $state ("stage-{0}" -f $Component.id)
    Expand-UiapZip $Archive $stage
    $source = Get-UiapContentRoot $stage
    if (Test-Path -LiteralPath $destination) { Remove-Item -LiteralPath $destination -Recurse -Force }
    New-Item -ItemType Directory -Path $destination -Force | Out-Null

    foreach ($name in @('LICENSE','README.md')) {
        $sourceFile = Join-Path $source $name
        if (Test-Path -LiteralPath $sourceFile) { Copy-Item -LiteralPath $sourceFile -Destination $destination -Force }
    }
    foreach ($name in @('ch32fun','minichlink','misc','extralibs')) {
        $sourceDir = Join-Path $source $name
        if (Test-Path -LiteralPath $sourceDir) { Copy-Item -LiteralPath $sourceDir -Destination $destination -Recurse -Force }
    }

    $mk = Join-Path $destination 'ch32fun\ch32fun.mk'
    if (-not (Test-Path -LiteralPath $mk)) { throw '[UIAP-E131] ch32fun.mkがサブセットにありません。' }
    $mkText = Get-Content -LiteralPath $mk -Raw
    $mkText = $mkText.Replace('-I$(NEWLIB)', '')
    Set-Content -LiteralPath $mk -Value $mkText -Encoding UTF8

    @"
# ch32fun test subset

This is a host-generated test subset for uiap-devkit-win64 0.6.2-test19.
It is not the final reviewed participant allowlist subset.
Upstream commit: $($Component.upstream_commit)
Input SHA-256: $($Component.sha256)
Local change: removed the effective -I`$(NEWLIB) option from ch32fun.mk.
"@ | Set-Content -LiteralPath (Join-Path $destination 'SUBSET.md') -Encoding UTF8
    $Component.upstream_commit | Set-Content -LiteralPath (Join-Path $destination 'UPSTREAM_COMMIT') -Encoding ASCII
    @('LICENSE','README.md','ch32fun/**','minichlink/**','misc/**','extralibs/**') | Set-Content -LiteralPath (Join-Path $destination 'ALLOWLIST.txt') -Encoding ASCII

    $runtimeBin = Join-Path $runtime 'bin'
    New-Item -ItemType Directory -Path $runtimeBin -Force | Out-Null
    $miniExe = Join-Path $destination 'minichlink\minichlink.exe'
    if (Test-Path -LiteralPath $miniExe) {
        Copy-Item -LiteralPath $miniExe -Destination (Join-Path $runtimeBin 'minichlink.exe') -Force
        Copy-Item -LiteralPath $miniExe -Destination (Join-Path $runtimeBin 'minichlink') -Force
        Get-ChildItem -LiteralPath (Split-Path -Parent $miniExe) -Filter '*.dll' -ErrorAction SilentlyContinue | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $runtimeBin -Force
        }
    } else {
        Write-Host '[WARN] 上流アーカイブにminichlink.exeがありません。make flashは使用できません。' -ForegroundColor Yellow
    }

    Set-UiapInstallMarker $destination $Component.sha256
    Remove-Item -LiteralPath $stage -Recurse -Force
    Write-Host '[WARN] ch32funは最終レビュー済み許可リストではなく、テスト用サブセットです。' -ForegroundColor Yellow
}

function Install-UiapRv003usbPinnedFiles {
    param($Component)

    $destination = Join-Path $root ($Component.destination -replace '/', '\\')
    $marker = Join-Path $destination '.uiap-component.commit'
    $required = @($Component.files | ForEach-Object { Join-Path $destination ($_.path -replace '/', '\\') })
    $complete = (Test-Path -LiteralPath $marker -PathType Leaf) -and ((Get-Content -LiteralPath $marker -Raw).Trim() -eq $Component.upstream_commit)
    if ($complete) {
        foreach ($requiredFile in $required) {
            if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) { $complete = $false; break }
        }
    }
    if ($complete) {
        Write-Host "[PASS] インストール済み: $($Component.name)"
        return
    }

    $curl = Join-Path $env:SystemRoot 'System32\curl.exe'
    if (-not (Test-Path -LiteralPath $curl -PathType Leaf)) {
        throw "[UIAP-E120] Windows標準curl.exeが見つかりません: $curl"
    }

    $stage = Join-Path $state ("stage-{0}" -f $Component.id)
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    $hashLines = [System.Collections.Generic.List[string]]::new()

    foreach ($sourceFile in $Component.files) {
        if (-not $sourceFile.url.Contains($Component.upstream_commit)) {
            throw "[UIAP-E136] rv003usb URLが固定コミットを含みません: $($sourceFile.path)"
        }
        $target = Join-Path $stage ($sourceFile.path -replace '/', '\\')
        $part = "$target.part"
        New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
        Write-Host "[UIAP] rv003usb: $($sourceFile.path)"
        & $curl --fail --location --retry 3 --retry-delay 2 --connect-timeout 30 --progress-bar --output $part $sourceFile.url
        if ($LASTEXITCODE -ne 0) {
            throw "[UIAP-E121] rv003usb取得失敗: $($sourceFile.path) curl=$LASTEXITCODE"
        }
        Move-Item -LiteralPath $part -Destination $target -Force
        $hash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        $hashLines.Add("$hash  $($sourceFile.path)")
        Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format 'o') RV003USB-FILE $hash $($sourceFile.path)" -Encoding UTF8
    }

    $Component.upstream_commit | Set-Content -LiteralPath (Join-Path $stage 'UPSTREAM_COMMIT') -Encoding ASCII
    $hashLines | Set-Content -LiteralPath (Join-Path $stage 'SOURCE_FILES.sha256') -Encoding ASCII
    @"
# rv003usb source subset

Upstream: cnlohr/rv003usb
Commit: $($Component.upstream_commit)
Files: rv003usb.S, rv003usb.c, rv003usb.h, LICENSE
Transport: commit-pinned raw.githubusercontent.com URLs
Status: organizer test subset; final per-file SHA-256 lock and offline packaging are pending.
"@ | Set-Content -LiteralPath (Join-Path $stage 'README.md') -Encoding UTF8
    $Component.upstream_commit | Set-Content -LiteralPath (Join-Path $stage '.uiap-component.commit') -Encoding ASCII

    if (Test-Path -LiteralPath $destination) { Remove-Item -LiteralPath $destination -Recurse -Force }
    Move-Item -LiteralPath $stage -Destination $destination
    Write-Host '[WARN] rv003usbは固定コミットURLから取得しました。最終リリース用のファイル単位SHA-256固定は未完了です。' -ForegroundColor Yellow
}

try {
    $lockPath = Join-Path $root 'config\win\bootstrap.lock.json'
    $lock = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json

    $versionLine = Get-Content -LiteralPath (Join-Path $root 'VERSION') | Where-Object { $_ -like 'Version:*' } | Select-Object -First 1
    $packageVersion = if ($null -ne $versionLine) { ($versionLine -split ':', 2)[1].Trim() } else { '' }
    if ($lock.devkit_version -ne $packageVersion) {
        throw "[UIAP-E133] VERSIONとbootstrap lockのバージョンが一致しません。VERSION=$packageVersion lock=$($lock.devkit_version)"
    }

    foreach ($component in $lock.components) {
        if ($component.install_type -eq 'rv003usb-pinned-files') {
            if ([string]::IsNullOrWhiteSpace($component.upstream_commit) -or @($component.files).Count -lt 4) {
                throw '[UIAP-E136] rv003usb固定ソース定義が不完全です。'
            }
            foreach ($sourceFile in $component.files) {
                if (-not $sourceFile.url.Contains($component.upstream_commit)) {
                    throw "[UIAP-E136] rv003usb URLが固定コミットを含みません: $($sourceFile.path)"
                }
            }
            continue
        }
        if ($component.sha256_scope -ne 'exact-downloaded-file') {
            throw "[UIAP-E134] SHA-256の対象種別が不明です: $($component.id)"
        }
        if ($component.id -eq 'ch32fun') {
            if ($component.archive_format -ne 'zip' -or -not $component.file.EndsWith('.zip') -or -not $component.url.EndsWith('.zip')) {
                throw '[UIAP-E135] ch32funのアーカイブ形式、ファイル名、URLが一致しません。'
            }
        }
    }

    Write-Host 'UIAP Devkit online setup' -ForegroundColor Cyan
    Write-Host '大容量ファイルではcurl.exeの進捗バーを表示します。'

    foreach ($component in $lock.components) {
        if ($component.install_type -eq 'rv003usb-pinned-files') {
            Install-UiapRv003usbPinnedFiles $component
            continue
        }

        $archive = Join-Path $downloads $component.file
        Invoke-UiapDownload -Name $component.name -Uri $component.url -Destination $archive -ExpectedSha256 $component.sha256 -LogPath $logPath | Out-Null

        switch ($component.install_type) {
            'xpack' { Install-UiapXpack $component $archive }
            'python' { Install-UiapPython $component $archive }
            'python-wheel' { Install-UiapPythonWheel $component $archive }
            'ch32fun-test-subset' { Install-UiapCh32funTestSubset $component $archive }
            default { throw "[UIAP-E132] 未対応のinstall_typeです: $($component.install_type)" }
        }
    }

    $python = Join-Path $runtime 'python\python.exe'
    if (Test-Path -LiteralPath $python) {
        & $python (Join-Path $root 'scripts\python\hidapi_probe.py')
        if ($LASTEXITCODE -ne 0) { throw '[UIAP-E207] 同梱Pythonがhidapiを読み込めません。' }
    }

    @{ version = $lock.devkit_version; completed_at = (Get-Date -Format 'o') } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $state 'setup.json') -Encoding UTF8

    Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format 'o') SETUP-PASS" -Encoding UTF8
    Write-Host ''
    Write-Host '[PASS] setupが完了しました。次にdoctorを実行してください。' -ForegroundColor Green
    exit 0
} catch {
    Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format 'o') SETUP-FAIL $($_.Exception.Message)" -Encoding UTF8
    Write-Host ''
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "ログ: $logPath"
    exit 199
}
