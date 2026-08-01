[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Root,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

try {
    $fullPath = [System.IO.Path]::GetFullPath($Root).TrimEnd([char]'\')
} catch {
    Write-Host '[UIAP-E103] 開発キットの展開先フォルダーを解決できません。' -ForegroundColor Red
    exit 103
}

$problems = [System.Collections.Generic.List[string]]::new()

if ($fullPath.StartsWith('\\')) {
    $problems.Add('ネットワーク共有またはUNCパスです。')
} elseif ($fullPath -notmatch '^[A-Za-z]:\\') {
    $problems.Add('ローカルドライブの絶対パスではありません。')
} else {
    $relative = $fullPath.Substring(3)
    if ([string]::IsNullOrWhiteSpace($relative)) {
        $problems.Add('ドライブ直下へ展開しないでください。')
    } else {
        foreach ($segment in ($relative -split '\\')) {
            if ($segment -notmatch '^[A-Za-z0-9._-]+$') {
                $problems.Add("使用できないフォルダー名があります: $segment")
            }
        }
    }
}

if ($problems.Count -gt 0) {
    Write-Host '[UIAP-E103] 開発キットの展開先フォルダーを使用できません。' -ForegroundColor Red
    Write-Host "現在の場所: $fullPath"
    Write-Host ''
    Write-Host 'このWindows版では、次の場所を使用できません。'
    Write-Host '  - 親フォルダーを含め、名前に空白がある場所'
    Write-Host '  - 日本語・全角文字など、ASCII以外の文字を含む場所'
    Write-Host '  - ネットワーク共有またはUNCパス'
    Write-Host ''
    foreach ($problem in $problems) { Write-Host "確認結果: $problem" }
    Write-Host ''
    Write-Host '推奨移動先: C:\uiap\uiap-devkit-win64'
    Write-Host '移動後、現在のコンソールを閉じ、新しい場所のstart-uiap.cmdから起動してください。'
    exit 103
}

if (-not $Quiet) {
    Write-Host "[PASS] Devkit path: $fullPath"
}
exit 0
