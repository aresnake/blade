param([string]$Version = $null)

$Repo = (Resolve-Path .).Path
$Ares = Join-Path $Repo "ares"
$Dist = Join-Path $Repo "dist"
New-Item -ItemType Directory -Path $Dist -Force | Out-Null

# Version depuis ares/__init__.py si non donnée
if (-not $Version) {
  $init = Get-Content -Raw (Join-Path $Ares "__init__.py")
  if ($init -match "__version__\s*=\s*['""]([^'""]+)['""]") { $Version = $Matches[1] } else { $Version = "0.0.0" }
}
$ZipPath = Join-Path $Dist ("ares-" + $Version + ".zip")
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

# ---- Préparer un staging propre (sans __pycache__/pyc) ----
$stagingRoot = Join-Path $Repo ".pack_staging"
$stagingAres = Join-Path $stagingRoot "ares"
Remove-Item $stagingRoot -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path $stagingAres -Force | Out-Null

# Copier récursivement tout en filtrant
Get-ChildItem -Path $Ares -Recurse -File | Where-Object {
  $_.FullName -notmatch "\\__pycache__\\|\.pyc$"
} | ForEach-Object {
  $rel = $_.FullName.Substring($Ares.Length).TrimStart('\','/')
  $dst = Join-Path $stagingAres $rel
  New-Item -ItemType Directory -Path (Split-Path $dst -Parent) -Force | Out-Null
  Copy-Item $_.FullName -Destination $dst -Force
}

# ---- Méthode 1 : Compress-Archive si dispo ----
if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
  # Important : passer le dossier "ares" pour qu'il soit racine dans le zip
  Compress-Archive -Path $stagingAres -DestinationPath $ZipPath -CompressionLevel Optimal -Force
}
else {
  # ---- Méthode 2 : .NET, en chargeant les 2 assemblies ----
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  Add-Type -AssemblyName System.IO.Compression
  $fs = [System.IO.File]::Open($ZipPath, [System.IO.FileMode]::Create)
  $zipArchive = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create, $false)
  Get-ChildItem -Path $stagingAres -Recurse -File | ForEach-Object {
    $entryName = $_.FullName.Substring($stagingRoot.Length + 1)  # garde "ares/..." dans le zip
    $entry = $zipArchive.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
    $in = [System.IO.File]::OpenRead($_.FullName)
    $out = $entry.Open()
    $in.CopyTo($out)
    $out.Dispose(); $in.Dispose()
  }
  $zipArchive.Dispose(); $fs.Dispose()
}

# Nettoyage
Remove-Item $stagingRoot -Recurse -Force -ErrorAction SilentlyContinue | Out-Null

Write-Host "✅ Package ready:" $ZipPath
