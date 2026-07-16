param(
    [string]$ShortcutName = "Dragon's Lair RPG"
)

$ErrorActionPreference = "Stop"

$RepoDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$Launcher = Join-Path $RepoDir "Run Dragons Lair RPG.cmd"
$IconPath = Join-Path $RepoDir "assets\processed\ui\dragon_app_icon.ico"

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

if (-not (Test-Path -LiteralPath $Launcher)) {
    throw "Launcher not found: $Launcher"
}

# BEGINNER CODE LABEL: Windows desktop shortcut builder.
# This creates a click-friendly launcher for the current checkout. The shortcut
# still runs the normal .cmd launcher, so it keeps the existing update check.
$desktop = Get-DesktopPath
$shortcutPath = Join-Path $desktop "$ShortcutName.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $Launcher
$shortcut.WorkingDirectory = $RepoDir
$shortcut.Description = "Run Dragon's Lair RPG from this checkout"

if (Test-Path -LiteralPath $IconPath) {
    $shortcut.IconLocation = $IconPath
}

$shortcut.Save()

Write-Host "Dragon's Lair RPG desktop shortcut is ready." -ForegroundColor Green
Write-Host $shortcutPath
