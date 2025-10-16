param(
  [string]$Tag = '',
  [string]$ZipPath = '',
  [switch]$SkipBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 1) ZIP: utilise celui fourni, sinon (sauf SkipBuild) rebuild puis prend le plus récent
if (-not $ZipPath) {
  if (-not $SkipBuild) {
    & .\make_zip.ps1 | Write-Host
  }
  $dist = Join-Path (Join-Path $PSScriptRoot '..') 'dist'
  $zip  = Get-ChildItem $dist\*.zip | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $zip) { throw 'Aucun ZIP trouvé. Fournis -ZipPath ou enlève -SkipBuild.' }
  $ZipPath = $zip.FullName
}

# 2) Tag par défaut (depuis bl_info version, sinon datestamp)
if (-not $Tag -or $Tag -eq '') {
  $init = Resolve-Path (Join-Path $PSScriptRoot '..\ares\__init__.py')
  $txt = Get-Content -LiteralPath $init -Raw
  if ($txt -match 'version\D*\((?<maj>\d+),\s*(?<min>\d+),\s*(?<patch>\d+)') {
    $Tag = "v$([int]$Matches.maj).$([int]$Matches.min).$([int]$Matches.patch)-test"
  } else {
    $Tag = "v13-$(Get-Date -Format 'yyyyMMdd-HHmm')-test"
  }
}

# 3) Tag idempotent (ne crée/pousse que s'il n'existe pas)
$null = & git rev-parse -q --verify "refs/tags/$Tag" 2>$null
$hasTag = ($LASTEXITCODE -eq 0)
if ($hasTag) {
  Write-Host "ℹ️  Tag '$Tag' existe déjà — on ne le recrée pas."
} else {
  git tag $Tag
  git push origin $Tag
}

# 4) Create or upload release — détection silencieuse via Start-Process (temp files)
$tfOut = [System.IO.Path]::GetTempFileName()
$tfErr = [System.IO.Path]::GetTempFileName()
$proc  = Start-Process -FilePath gh -ArgumentList @("release","view",$Tag) -NoNewWindow -Wait -PassThru `
         -RedirectStandardOutput $tfOut -RedirectStandardError $tfErr
$exists = ($proc.ExitCode -eq 0)
Remove-Item -ErrorAction SilentlyContinue $tfOut, $tfErr

if ($exists) {
  gh release upload $Tag "$ZipPath" --clobber
} else {
  gh release create $Tag "$ZipPath" -t "Blade $Tag" -n "Release auto (git archive)."
}

Write-Host "`n✅ Release '$Tag' publiée avec '$ZipPath'"