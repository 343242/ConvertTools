param(
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$UvCommand = Get-Command uv -ErrorAction SilentlyContinue
$PyInstallerExe = Join-Path $Root ".venv\Scripts\pyinstaller.exe"
$VenvScripts = Join-Path $Root ".venv\Scripts"

if (-not $UvCommand -and -not (Test-Path $PyInstallerExe)) {
    throw "Neither uv nor .venv\Scripts\pyinstaller.exe was found. Run 'uv sync' first."
}

$oldPath = $env:PATH
$oldPythonNoUserSite = $env:PYTHONNOUSERSITE

try {
    $env:PYTHONNOUSERSITE = "1"
    $cleanPath = @(
        $VenvScripts,
        "C:\Windows\System32",
        "C:\Windows"
    )
    $env:PATH = ($cleanPath -join [IO.Path]::PathSeparator)

    Push-Location $Root
    try {
        if ($UvCommand) {
            & $UvCommand.Source run pyinstaller ConvertTools.spec --noconfirm
        }
        else {
            & $PyInstallerExe ConvertTools.spec --noconfirm
        }

        if (-not $SkipVerify) {
            & (Join-Path $PSScriptRoot "verify_dist.ps1")
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    $env:PATH = $oldPath
    if ($null -eq $oldPythonNoUserSite) {
        Remove-Item Env:PYTHONNOUSERSITE -ErrorAction SilentlyContinue
    }
    else {
        $env:PYTHONNOUSERSITE = $oldPythonNoUserSite
    }
}
