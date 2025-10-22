# tools\sync_and_scan.ps1
<#
.SYNOPSIS
  Synchronise le dépôt local avec GitHub et scanne l’état complet du projet.
#>

Set-Location "D:\V13\workspace_v13"

$reportPath = "dist\git_scan_report.txt"
New-Item -ItemType Directory -Force -Path "dist" | Out-Null

Write-Host "=== [ARES] Git sync & scan started ===`n"

# Identité
$UserName = git config user.name
$UserEmail = git config user.email
Write-Host "User: $UserName <$UserEmail>"

# Remote
Write-Host "`n=== Remote ==="
git remote -v

# Sauvegarde locale (commit vide permis)
Write-Host "`n=== Local commit ==="
git add .
git commit -m "chore: sauvegarde locale avant synchro" --allow-empty

# Fetch + synchro
Write-Host "`n=== Fetch origin ==="
git fetch origin --prune

$branch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host "`n=== Sync branch '$branch' ==="
try {
    git pull origin $branch
    git push origin $branch
} catch {
    Write-Warning "⚠️ Synchronisation partielle, vérifie les conflits."
}

# Status
Write-Host "`n=== Status ==="
git status

# Rapport
$reportContent = @"
=== GIT STATUS ===
$(git status)

=== GIT LOG (10 last commits) ===
$(git log --oneline -10)

=== GIT REMOTE ===
$(git remote -v)

=== LOCAL CHANGES ===
$(git diff --name-status)

=== UNTRACKED FILES ===
$(git ls-files --others --exclude-standard)

=== RECENT FILES (20 last) ===
$((Get-ChildItem -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 20 | Format-Table -HideTableHeaders | Out-String))
"@
$reportContent | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "`n✅ Rapport généré : $reportPath"
Write-Host "=== [ARES] Git sync & scan completed ==="
