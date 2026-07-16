param(
    [string]$InstallDir = "",
    [string]$Branch = "main",
    [string]$RepoUrl = "https://github.com/Tboy450/Tboy450-new-rpg-update.git"
)

$ErrorActionPreference = "Stop"

$ActivePaths = @(
    "README.md",
    "main.py",
    "requirements.txt",
    "game_data",
    "systems",
    "assets",
    "scripts"
)

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$FailureMessage
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

function Get-DesktopPath {
    $desktop = [Environment]::GetFolderPath("Desktop")
    if ($desktop -and (Test-Path -LiteralPath $desktop)) {
        return $desktop
    }

    if ($env:OneDrive) {
        $oneDriveDesktop = Join-Path $env:OneDrive "Desktop"
        if (Test-Path -LiteralPath $oneDriveDesktop) {
            return $oneDriveDesktop
        }
    }

    $profileDesktop = Join-Path $env:USERPROFILE "Desktop"
    if (-not (Test-Path -LiteralPath $profileDesktop)) {
        New-Item -ItemType Directory -Path $profileDesktop | Out-Null
    }
    return $profileDesktop
}

function Get-DocumentsPath {
    $documents = [Environment]::GetFolderPath("MyDocuments")
    if ($documents -and (Test-Path -LiteralPath $documents)) {
        return $documents
    }

    if ($env:OneDrive) {
        $oneDriveDocuments = Join-Path $env:OneDrive "Documents"
        if (Test-Path -LiteralPath $oneDriveDocuments) {
            return $oneDriveDocuments
        }
    }

    $profileDocuments = Join-Path $env:USERPROFILE "Documents"
    if (-not (Test-Path -LiteralPath $profileDocuments)) {
        New-Item -ItemType Directory -Path $profileDocuments | Out-Null
    }
    return $profileDocuments
}

function Get-BasePython {
    if ($env:DRAGONS_LAIR_PYTHON -and (Test-Path -LiteralPath $env:DRAGONS_LAIR_PYTHON)) {
        return [PSCustomObject]@{ FilePath = $env:DRAGONS_LAIR_PYTHON; Arguments = @() }
    }

    $codexPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $codexPython) {
        return [PSCustomObject]@{ FilePath = $codexPython; Arguments = @() }
    }

    foreach ($candidate in @("py", "python", "python3")) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if (-not $command) {
            continue
        }

        if ($candidate -eq "py") {
            return [PSCustomObject]@{ FilePath = $command.Source; Arguments = @("-3") }
        }

        return [PSCustomObject]@{ FilePath = $command.Source; Arguments = @() }
    }

    throw "Python was not found. Install Python 3 from https://www.python.org/downloads/ or set DRAGONS_LAIR_PYTHON to python.exe."
}

function Sync-GameFiles {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git was not found. Install Git for Windows from https://git-scm.com/download/win and run this installer again."
    }

    if (-not (Test-Path -LiteralPath $InstallDir)) {
        New-Item -ItemType Directory -Path (Split-Path $InstallDir -Parent) -Force | Out-Null
        Invoke-Checked "git" @("clone", "--no-checkout", $RepoUrl, $InstallDir) "Could not clone the game repository."
    }
    elseif (-not (Test-Path -LiteralPath (Join-Path $InstallDir ".git"))) {
        throw "Install folder exists but is not a Git repository: $InstallDir"
    }

    Push-Location $InstallDir
    try {
        Invoke-Checked "git" @("fetch", "origin", $Branch) "Could not fetch the latest game files."
        Invoke-Checked "git" @("config", "core.sparseCheckout", "true") "Could not enable sparse checkout."
        Invoke-Checked "git" @("config", "core.sparseCheckoutCone", "false") "Could not configure sparse checkout."

        $sparseFile = Join-Path $InstallDir ".git\info\sparse-checkout"
        $sparseDir = Split-Path $sparseFile -Parent
        if (-not (Test-Path -LiteralPath $sparseDir)) {
            New-Item -ItemType Directory -Path $sparseDir | Out-Null
        }
        Set-Content -LiteralPath $sparseFile -Value $ActivePaths -Encoding ASCII

        Invoke-Checked "git" (@("restore", "--source=origin/$Branch", "--worktree", "--") + $ActivePaths) "Could not restore the latest game files."
    }
    finally {
        Pop-Location
    }
}

function Ensure-GamePython {
    $venvPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        $basePython = Get-BasePython
        Write-Host "Creating local Python environment..." -ForegroundColor Cyan
        Invoke-Checked $basePython.FilePath ($basePython.Arguments + @("-m", "venv", (Join-Path $InstallDir ".venv"))) "Could not create the Python environment."
    }

    Write-Host "Installing game packages..." -ForegroundColor Cyan
    Invoke-Checked $venvPython @("-m", "pip", "install", "--upgrade", "pip") "Could not upgrade pip."
    Invoke-Checked $venvPython @("-m", "pip", "install", "-r", (Join-Path $InstallDir "requirements.txt")) "Could not install game packages."
    return $venvPython
}

function Write-Launcher {
    $launcher = Join-Path $InstallDir "Run Dragons Lair RPG.cmd"
    $launcherText = @"
@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_windows.ps1"
if errorlevel 1 pause
"@
    Set-Content -LiteralPath $launcher -Value $launcherText -Encoding ASCII
    return $launcher
}

function Write-DesktopShortcut {
    param(
        [string]$Launcher,
        [string]$PythonExe
    )

    $desktop = Get-DesktopPath
    $shortcutPath = Join-Path $desktop "Dragon's Lair RPG.lnk"
    $iconPath = Join-Path $InstallDir "assets\processed\ui\dragon_app_icon.ico"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $Launcher
    $shortcut.WorkingDirectory = $InstallDir
    $shortcut.Description = "Run Dragon's Lair RPG and update from GitHub before launch"
    if (Test-Path -LiteralPath $iconPath) {
        $shortcut.IconLocation = $iconPath
    }
    else {
        $shortcut.IconLocation = "$PythonExe,0"
    }
    $shortcut.Save()
    return $shortcutPath
}

if (-not $InstallDir) {
    $InstallDir = Join-Path (Get-DocumentsPath) "Tboy450-new-rpg-update-windows"
}

Write-Host "Installing Dragon's Lair RPG to $InstallDir" -ForegroundColor Cyan
Sync-GameFiles
$python = Ensure-GamePython
$launcherPath = Write-Launcher
$shortcutPath = Write-DesktopShortcut $launcherPath $python

Write-Host ""
Write-Host "Dragon's Lair RPG is ready." -ForegroundColor Green
Write-Host "Desktop shortcut: $shortcutPath"
Write-Host "Each launch checks GitHub for updates before starting the game."
