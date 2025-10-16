param(
  [switch]$Status,
  [switch]$Tree
)
if ($Status) { git status -sb; exit 0 }
if ($Tree)   { git log --oneline -n 15; exit 0 }

Write-Host 'Dev.ps1 helpers:' -ForegroundColor Cyan
Write-Host '  - .\tools\Dev.ps1 -Status   # git status court'
Write-Host '  - .\tools\Dev.ps1 -Tree     # dernier log'
