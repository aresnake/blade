# Blade v13 — ShellInfo (préflight PowerShell)

function Get-BladeShellInfo {
    $si = [ordered]@{}
    $si.Edition   = $PSVersionTable.PSEdition
    $si.Version   = $PSVersionTable.PSVersion.ToString()
    $si.IsCore    = ($PSVersionTable.PSEdition -eq "Core")  # pwsh (PowerShell 7+)
    $si.IsWindows = ($PSVersionTable.PSEdition -eq "Desktop") # Windows PowerShell 5.1

    # Outils dispos
    $si.HasCompressArchive = [bool](Get-Command Compress-Archive -ErrorAction SilentlyContinue)
    $si.HasPwsh            = [bool](Get-Command pwsh -ErrorAction SilentlyContinue)

    # .NET Zip utilisable ?
    try {
        Add-Type -AssemblyName System.IO.Compression -ErrorAction Stop
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
        # ping d'un type clé
        [void][System.IO.Compression.ZipArchiveMode]::Create
        $si.HasDotNetZip = $true
    } catch {
        $si.HasDotNetZip = $false
    }

    # Résumé
    $si.ZipStrategy = if ($si.HasCompressArchive) { "Compress-Archive" }
        elseif ($si.HasDotNetZip) { ".NET ZipArchive" }
        else { "None" }

    # Env helper
    $env:__BLADE_SHELL    = "{0} {1}" -f $si.Edition, $si.Version
    $env:__BLADE_ZIPSTRAT = $si.ZipStrategy

    [pscustomobject]$si
}
