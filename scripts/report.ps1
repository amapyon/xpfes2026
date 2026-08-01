[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Continue'
$root=$env:UIAP_DEVKIT_ROOT
$logs=Join-Path $root 'logs\win'; New-Item -ItemType Directory -Path $logs -Force | Out-Null
$out=Join-Path $logs ("report-{0}.txt" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$lines=[System.Collections.Generic.List[string]]::new()
$lines.Add("Generated: $(Get-Date -Format 'o')")
$lines.Add("Root: $root")
$lines.Add("OS: $([Environment]::OSVersion.VersionString)")
$lines.Add("64-bit OS: $([Environment]::Is64BitOperatingSystem)")
$lines.Add("Architecture: $env:PROCESSOR_ARCHITECTURE")
$lines.Add('')
$lines.Add((Get-Content -LiteralPath (Join-Path $root 'VERSION') -Raw))
$lines.Add('Download cache:')
Get-ChildItem -LiteralPath (Join-Path $env:UIAP_RUNTIME 'downloads') -File -ErrorAction SilentlyContinue | ForEach-Object {
    $lines.Add("  $($_.Name) $($_.Length) bytes")
}
$lines.Add('Recent setup logs:')
Get-ChildItem -LiteralPath $logs -Filter 'setup-*.log' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object {
    $lines.Add("--- $($_.Name) ---")
    foreach($line in (Get-Content -LiteralPath $_.FullName -Tail 80)){ $lines.Add($line) }
}
$lines | Set-Content -LiteralPath $out -Encoding UTF8
Write-Host "[PASS] 診断レポートを作成しました: $out"
exit 0
