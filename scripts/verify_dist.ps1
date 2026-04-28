param(
    [string]$DistDir = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path "dist\ConvertTools"),
    [string]$BuildDir = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path "build\ConvertTools"),
    [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"

function Fail($Message) {
    throw "Distribution verification failed: $Message"
}

$DistDir = (Resolve-Path $DistDir).Path
$ExePath = Join-Path $DistDir "ConvertTools.exe"
$InternalDir = Join-Path $DistDir "_internal"
$QtPlatformsDir = Join-Path $InternalDir "PySide6\plugins\platforms"
$QWindows = Join-Path $QtPlatformsDir "qwindows.dll"

if (-not (Test-Path $ExePath)) {
    Fail "ConvertTools.exe was not found in $DistDir"
}

if (-not (Test-Path $QWindows)) {
    Fail "Qt platform plugin qwindows.dll was not found at $QWindows"
}

$blockedDllGlobs = @(
    "icu*.dll",
    "libgcc_s*.dll",
    "libstdc++*.dll",
    "libwinpthread*.dll"
)

foreach ($glob in $blockedDllGlobs) {
    $matches = Get-ChildItem -Path $DistDir -Recurse -Filter $glob -File -ErrorAction SilentlyContinue
    if ($matches) {
        $paths = ($matches | ForEach-Object { $_.FullName }) -join [Environment]::NewLine
        Fail "Blocked DLL pattern '$glob' was found. This often means Anaconda, MSYS2, or Git\usr\bin polluted the build PATH.$([Environment]::NewLine)$paths"
    }
}

if (Test-Path $BuildDir) {
    $tocMatches = Select-String -Path (Join-Path $BuildDir "*.toc") -Pattern "Anaconda", "MSYS2", "Git\\usr\\bin" -SimpleMatch -ErrorAction SilentlyContinue
    if ($tocMatches) {
        $details = ($tocMatches | ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }) -join [Environment]::NewLine
        Fail "Build metadata references a known DLL pollution source.$([Environment]::NewLine)$details"
    }
}

if (-not $SkipSmoke) {
    $startupLog = Join-Path $env:LOCALAPPDATA "ConvertTools\startup-error.log"
    Remove-Item $startupLog -ErrorAction SilentlyContinue

    $process = Start-Process -FilePath $ExePath -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3

    if (Test-Path $startupLog) {
        $logText = Get-Content $startupLog -Raw
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        Fail "startup-error.log was created.$([Environment]::NewLine)$logText"
    }

    if ($process.HasExited) {
        Fail "ConvertTools.exe exited during smoke test with code $($process.ExitCode)"
    }

    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "Distribution verification passed: $DistDir"
