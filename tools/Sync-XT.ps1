# tools\Sync-XT.ps1
param(
  [switch]$Publish,     # copie le rapport dans docs/status/ (versionné)
  [switch]$AutoPush     # git add/commit/push automatique si -Publish
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location "D:\V13\workspace_v13"

# 1) exécute le scanner XT pour (re)générer dist\*.md
.\tools\sync_and_scan_xt.ps1

$srcMd = "dist\git_scan_report.md"
if (-not (Test-Path $srcMd)) {
  Write-Error "Rapport introuvable: $srcMd"
  exit 1
}

if ($Publish) {
  $dstDir = "docs\status"
  New-Item -ItemType Directory -Force -Path $dstDir | Out-Null

  $stamp = Get-Date -Format "yyyyMMdd_HHmm"
  $dstMd = Join-Path $dstDir ("git_scan_report_{0}.md" -f $stamp)
  Copy-Item $srcMd $dstMd -Force

  # met aussi à jour un alias stable
  Copy-Item $srcMd (Join-Path $dstDir "LATEST.md") -Force

  Write-Host "📦 Rapport publié -> $dstMd"
  Write-Host "📌 Alias mis à jour -> docs/status/LATEST.md"

  if ($AutoPush) {
    git add $dstMd "docs/status/LATEST.md" 2>$null
    git commit -m ("chore: publish scan report {0}" -f $stamp)
    git push origin dev
    Write-Host "🚀 Rapport publié & poussé"
  }
} else {
  Write-Host "ℹ️ Publication désactivée (utilise -Publish pour versionner le rapport)."
}
