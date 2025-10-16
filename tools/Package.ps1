param([string]$Version = $null)

# Preflight
. "$PSScriptRoot\ShellInfo.ps1"
$si = Get-BladeShellInfo

$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Ares = Join-Path $Repo "ares"
$Dist = Join-Path $Repo "dist"
New-Item -ItemType Directory -Path $Dist -Force | Out-Null

# Version (__version__)
if (-not $Version) {
  $init = Get-Content -Raw (Join-Path $Ares "__init__.py")
  if ($init -match "__version__\s*=\s*['""]([^'""]+)['""]") { $Version = $Matches[1] } else { $Version = "0.0.0" }
}
$ZipPath = Join-Path $Dist ("ares-" + $Version + ".zip")
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

# Staging propre
$stagingRoot = Join-Path $Repo ".pack_staging"
$stagingAres = Join-Path $stagingRoot "ares"
Remove-Item $stagingRoot -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path $stagingAres -Force | Out-Null

Get-ChildItem -Path $Ares -Recurse -File | Where-Object {
  $_.FullName -notmatch "\\__pycache__\\|\.pyc$"
} | ForEach-Object {
  $rel = $_.FullName.Substring($Ares.Length).TrimStart('\','/')
  $dst = Join-Path $stagingAres $rel
  New-Item -ItemType Directory -Path (Split-Path $dst -Parent) -Force | Out-Null
  Copy-Item $_.FullName -Destination $dst -Force
}

Write-Host ("Pack with: {0}" -f $si.ZipStrategy) -ForegroundColor Cyan

switch ($si.ZipStrategy) {
  "Compress-Archive" {
    Compress-Archive -Path $stagingAres -DestinationPath $ZipPath -CompressionLevel Optimal -Force
  }
  ".NET ZipArchive" {
    # les Add-Type déjà tentés dans ShellInfo, mais on (re)assure
    Add-Type -AssemblyName System.IO.Compression -ErrorAction SilentlyContinue
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
    $fs = [System.IO.File]::Open($ZipPath, [System.IO.FileMode]::Create)
    try {
      $zipArchive = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create, $false)
      Get-ChildItem -Path $stagingAres -Recurse -File | ForEach-Object {
        $entryName = $_.FullName.Substring($stagingRoot.Length + 1)  # garde "ares/..."
        $entry = $zipArchive.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
        $in = [System.IO.File]::OpenRead($_.FullName)
        $out = $entry.Open()
        $in.CopyTo($out)
        $out.Dispose(); $in.Dispose()
      }
      $zipArchive.Dispose()
    } finally {
      $fs.Dispose()
    }
  }
  default {
    throw "Aucune stratégie zip disponible sur ce shell (`$($si.Edition) $($si.Version)`). Installe PowerShell 7 (pwsh) ou active Compress-Archive."
  }
}

Remove-Item $stagingRoot -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
Write-Host "✅ Package ready:" $ZipPath
