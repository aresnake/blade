param([string]$Version = $null)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = Split-Path -Parent $Root
$Ares = Join-Path $Repo "ares"
$Dist = Join-Path $Repo "dist"
New-Item -ItemType Directory -Path $Dist -Force | Out-Null

# Lire version (__version__ dans ares/__init__.py sinon 0.0.0)
$ver = $Version
if (-not $ver) {
  $init = Get-Content -Raw (Join-Path $Ares "__init__.py")
  if ($init -match "__version__\s*=\s*['""]([^'""]+)['""]") { $ver = $Matches[1] } else { $ver = "0.0.0" }
}
$zip = Join-Path $Dist ("ares-" + $ver + ".zip")
if (Test-Path $zip) { Remove-Item $zip -Force }

# Zipper ares/ (sans __pycache__ ni *.pyc)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipArchive = [System.IO.Compression.ZipFile]::Open($zip, [System.IO.Compression.ZipArchiveMode]::Create)
Get-ChildItem -Path $Ares -Recurse -File | Where-Object {
  $_.FullName -notmatch "\\__pycache__\\|\.pyc$"
} | ForEach-Object {
  $entryName = $_.FullName.Substring($Repo.Length + 1)
  [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, $_.FullName, $entryName) | Out-Null
}
$zipArchive.Dispose()
Write-Host "✅ Package ready:" $zip
