Set-StrictMode -Version Latest

function Write-UiapDownloadLog {
    param([string]$LogPath, [string]$Message)
    if (-not [string]::IsNullOrWhiteSpace($LogPath)) {
        $timestamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'
        Add-Content -LiteralPath $LogPath -Value "$timestamp $Message" -Encoding UTF8
    }
}

function Get-UiapCurlPath {
    $systemCurl = Join-Path $env:SystemRoot 'System32\curl.exe'
    if (Test-Path -LiteralPath $systemCurl -PathType Leaf) { return $systemCurl }
    $command = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($null -ne $command) { return $command.Source }
    throw '[UIAP-E120] Windows標準のcurl.exeが見つかりません。Windows Updateを適用し、doctorを実行してください。'
}

function Test-UiapSha256 {
    param([string]$Path, [string]$ExpectedSha256)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    return $actual -eq $ExpectedSha256.ToLowerInvariant()
}

function Move-UiapInvalidDownload {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $badPath = "$Path.bad-$stamp"
    Move-Item -LiteralPath $Path -Destination $badPath -Force
    Write-Host "[WARN] SHA-256不一致ファイルを隔離しました: $badPath" -ForegroundColor Yellow
}

function Invoke-UiapCurl {
    param(
        [string]$CurlPath,
        [string]$Uri,
        [string]$PartPath,
        [bool]$Resume
    )

    $arguments = @(
        '--fail',
        '--location',
        '--retry', '3',
        '--retry-delay', '2',
        '--connect-timeout', '30',
        '--progress-bar'
    )
    if ($Resume) { $arguments += @('--continue-at', '-') }
    $arguments += @('--output', $PartPath, '--url', $Uri)

    & $CurlPath @arguments
    return $LASTEXITCODE
}

function Invoke-UiapDownload {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-fA-F]{64}$')][string]$ExpectedSha256,
        [string]$LogPath
    )

    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $partPath = "$Destination.part"

    Write-Host ''
    Write-Host "[UIAP] $Name" -ForegroundColor Cyan
    Write-Host "保存先: $Destination"

    # A previous validation build may have quarantined a file only because its
    # lock value was wrong. Reuse it only after checking it against the current
    # exact expected SHA-256. Never accept a quarantined file by name alone.
    $quarantineCandidates = @(
        Get-ChildItem -LiteralPath $parent -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -like "$Destination.part.bad-*" -or
                $_.FullName -like "$Destination.bad-*"
            } |
            Sort-Object LastWriteTime -Descending
    )
    foreach ($candidate in $quarantineCandidates) {
        if (Test-UiapSha256 -Path $candidate.FullName -ExpectedSha256 $ExpectedSha256) {
            Move-Item -LiteralPath $candidate.FullName -Destination $Destination -Force
            Write-Host "[PASS] 隔離済みファイルを現在のSHA-256で再検証して採用しました: $($candidate.Name)" -ForegroundColor Green
            Write-UiapDownloadLog $LogPath "QUARANTINE-RECOVER name=[$Name] source=[$($candidate.FullName)] file=[$Destination] sha256=[$ExpectedSha256]"
            return $Destination
        }
    }

    if (Test-UiapSha256 -Path $Destination -ExpectedSha256 $ExpectedSha256) {
        Write-Host '[PASS] 検証済みキャッシュを再利用します。'
        Write-UiapDownloadLog $LogPath "CACHE-HIT name=[$Name] file=[$Destination] sha256=[$ExpectedSha256]"
        return $Destination
    }
    if (Test-Path -LiteralPath $Destination -PathType Leaf) {
        Move-UiapInvalidDownload -Path $Destination
    }

    if (Test-UiapSha256 -Path $partPath -ExpectedSha256 $ExpectedSha256) {
        Move-Item -LiteralPath $partPath -Destination $Destination -Force
        Write-Host '[PASS] 完了済み.partファイルを採用しました。'
        Write-UiapDownloadLog $LogPath "PART-COMPLETE name=[$Name] file=[$Destination] sha256=[$ExpectedSha256]"
        return $Destination
    }

    $curlPath = Get-UiapCurlPath
    $resume = (Test-Path -LiteralPath $partPath -PathType Leaf) -and ((Get-Item -LiteralPath $partPath).Length -gt 0)
    if ($resume) {
        $size = (Get-Item -LiteralPath $partPath).Length
        Write-Host "既存の未完了ファイルから再開します: $size bytes"
    } else {
        Write-Host 'ダウンロードを開始します。Ctrl+Cで中止できます。'
    }
    Write-UiapDownloadLog $LogPath "DOWNLOAD-START name=[$Name] uri=[$Uri] resume=[$resume]"

    $exitCode = Invoke-UiapCurl -CurlPath $curlPath -Uri $Uri -PartPath $partPath -Resume $resume

    if ($exitCode -eq 33 -and $resume) {
        Write-Host '[WARN] 配布元が再開に対応していないため、先頭から取得し直します。' -ForegroundColor Yellow
        Remove-Item -LiteralPath $partPath -Force -ErrorAction SilentlyContinue
        $exitCode = Invoke-UiapCurl -CurlPath $curlPath -Uri $Uri -PartPath $partPath -Resume $false
    }

    if ($exitCode -ne 0) {
        Write-UiapDownloadLog $LogPath "DOWNLOAD-FAIL name=[$Name] curl_exit=[$exitCode] part=[$partPath]"
        throw "[UIAP-E121] ダウンロードに失敗しました。curl終了コード: $exitCode。未完了ファイルは再開用に保持します: $partPath"
    }

    Write-Host 'SHA-256を検証しています...'
    if (-not (Test-UiapSha256 -Path $partPath -ExpectedSha256 $ExpectedSha256)) {
        $actual = (Get-FileHash -LiteralPath $partPath -Algorithm SHA256).Hash.ToLowerInvariant()
        Move-UiapInvalidDownload -Path $partPath
        Write-UiapDownloadLog $LogPath "HASH-FAIL name=[$Name] expected=[$ExpectedSha256] actual=[$actual]"
        throw "[UIAP-E122] SHA-256が一致しません。期待値: $ExpectedSha256 実測値: $actual"
    }

    Move-Item -LiteralPath $partPath -Destination $Destination -Force
    Write-Host '[PASS] ダウンロードとSHA-256検証が完了しました。' -ForegroundColor Green
    Write-UiapDownloadLog $LogPath "DOWNLOAD-PASS name=[$Name] file=[$Destination] sha256=[$ExpectedSha256]"
    return $Destination
}
