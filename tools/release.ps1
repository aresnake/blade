param(
  [string]$Tag = '',
  [string]$ZipPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 1) Build du ZIP si non fourni
if (-not $ZipPath) {
  & .\make_zip.ps1 | Write-Host
  $dist = Join-Path (Join-Path $PSScriptRoot '..') 'dist'
  $zip  = Get-ChildItem $dist\*.zip | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $zip) { throw 'Aucun ZIP trouvé après build.' }
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

# 3) Création tag + push (idempotent)
git tag $Tag 2>$null
git push origin $Tag

# 4) Create or upload release
$exists = (& gh release view $Tag *> $null; $?)
if ($exists) {
  gh release upload $Tag "$ZipPath" --clobber
} else {
  gh release create $Tag "$ZipPath" -t "Blade $Tag" -n "Release auto (git archive)."
}

Write-Host "`n✅ Release '$Tag' publiée avec '$ZipPath'"