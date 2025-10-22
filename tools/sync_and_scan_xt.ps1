# tools\sync_and_scan_xt.ps1
<#
.SYNOPSIS
  Version XT du scanner Git ARES : rapport Markdown + stats, robuste.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location "D:\V13\workspace_v13"

$reportTxt = "dist\git_scan_report.txt"
$reportMd  = "dist\git_scan_report.md"
New-Item -ItemType Directory -Force -Path "dist" | Out-Null

Write-Host "=== [ARES] Git sync & scan XT started ===`n"

# --- Git ---
$branch    = (git rev-parse --abbrev-ref HEAD).Trim()
$remote    = git remote -v
$status    = git status
$log       = git log --oneline -10
$diff      = git diff --name-status
$untracked = git ls-files --others --exclude-standard

# --- Stats projet ---
$files = Get-ChildItem -Recurse -File
$totalSizeMB = [math]::Round((($files | Measure-Object -Property Length -Sum).Sum) / 1MB, 2)
$topExt = $files | Group-Object Extension | Sort-Object Count -Descending | Select-Object -First 10

# --- Rapport texte brut ---
@"
=== GIT STATUS ===
$status

=== GIT LOG (10 last commits) ===
$log

=== GIT REMOTE ===
$remote

=== LOCAL CHANGES ===
$diff

=== UNTRACKED FILES ===
$untracked

=== PROJECT STATS ===
Total size: ${totalSizeMB} MB
Top 10 extensions:
$(
  $topExt | ForEach-Object {
    $n = if ([string]::IsNullOrEmpty($_.Name)) { "(no ext)" } else { $_.Name.TrimStart('.') }
    "  $n - $($_.Count)"
  }
)
"@ | Out-File -FilePath $reportTxt -Encoding utf8

# --- Rapport Markdown (construction sûre) ---
$ticks = '```'   # code fence en texte pur (pas interprété)
$nl    = "`r`n"

$md = New-Object System.Collections.Generic.List[string]
$md.Add('# ARES Git Sync & Scan XT Report')
$md.Add((Get-Date -Format 'yyyy-MM-dd HH:mm'))
$md.Add(("**Branch:** {0}  " -f $branch))
$md.Add(("**Remote:**  {0}  " -f (($remote -split "`n")[0]).Trim()))
$md.Add(("**Project Size:** {0} MB  " -f $totalSizeMB))
$md.Add('') 

$md.Add('## Top 10 Extensions')
foreach ($e in $topExt) {
  $name = if ([string]::IsNullOrEmpty($e.Name)) { '(no ext)' } else { $e.Name.TrimStart('.') }
  $md.Add(("- {0}: {1} files" -f $name, $e.Count))
}
$md.Add('')

$md.Add('## Git Status')
$md.Add($ticks)
$md.Add($status)
$md.Add($ticks)
$md.Add('')

$md.Add('## Last 10 Commits')
$md.Add($ticks)
$md.Add($log)
$md.Add($ticks)
$md.Add('')

$md.Add('## Local Changes')
$md.Add($ticks)
$md.Add($diff)
$md.Add($ticks)
$md.Add('')

$md.Add('## Untracked Files')
$md.Add($ticks)
$md.Add($untracked)
$md.Add($ticks)

$md -join $nl | Out-File -FilePath $reportMd -Encoding utf8

Write-Host "✅ Rapports générés :"
Write-Host " - $reportTxt"
Write-Host " - $reportMd"

Start-Process notepad.exe $reportMd
Write-Host "=== [ARES] Git sync & scan XT completed ==="
