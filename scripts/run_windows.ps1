$ErrorActionPreference = "Stop"

$RepoDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$Branch = "main"
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

function Get-DirtyActivePaths {
    # BEGINNER CODE LABEL: Local edit safety check.
    # The launcher can copy fresh files from GitHub, but only after this
    # function confirms the active game files are clean. That protects local
    # edits made by the user or Codex from being overwritten.
    Push-Location $RepoDir
    try {
        $statusArgs = @("status", "--porcelain", "--") + $ActivePaths
        $statusLines = & git @statusArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Could not check for local file edits."
        }

        $dirtyPaths = @()
        foreach ($line in $statusLines) {
            if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 4) {
                continue
            }

            $path = $line.Substring(3).Trim()
            if ($path.Contains(" -> ")) {
                $path = ($path -split " -> ")[-1]
            }
            $dirtyPaths += $path.Trim('"')
        }

        return $dirtyPaths | Sort-Object -Unique
    }
    finally {
        Pop-Location
    }
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

function Update-GameFiles {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "Git not found; skipping auto-update." -ForegroundColor Yellow
        return
    }

    if (-not (Test-Path -LiteralPath (Join-Path $RepoDir ".git"))) {
        Write-Host "No .git folder found; skipping auto-update." -ForegroundColor Yellow
        return
    }

    $dirtyPaths = @(Get-DirtyActivePaths)
    if ($dirtyPaths.Count -gt 0) {
        # BEGINNER CODE LABEL: Stop before GitHub restore.
        # Returning here means the launcher still starts the local game, but it
        # skips the auto-update step so changed files stay untouched.
        Write-Host "Local game edits detected; skipping auto-update so they are not overwritten." -ForegroundColor Yellow
        foreach ($path in $dirtyPaths) {
            Write-Host "  $path" -ForegroundColor DarkYellow
        }
        return
    }

    Write-Host "Checking GitHub for updates..." -ForegroundColor Cyan
    Push-Location $RepoDir
    try {
        Invoke-Checked "git" @("fetch", "origin", $Branch) "Could not fetch the latest game files."
        Invoke-Checked "git" @("config", "core.sparseCheckout", "true") "Could not enable sparse checkout."
        Invoke-Checked "git" @("config", "core.sparseCheckoutCone", "false") "Could not configure sparse checkout."

        $sparseFile = Join-Path $RepoDir ".git\info\sparse-checkout"
        $sparseDir = Split-Path $sparseFile -Parent
        if (-not (Test-Path -LiteralPath $sparseDir)) {
            New-Item -ItemType Directory -Path $sparseDir | Out-Null
        }
        Set-Content -LiteralPath $sparseFile -Value $ActivePaths -Encoding ASCII

        Invoke-Checked "git" (@("restore", "--source=origin/$Branch", "--worktree", "--") + $ActivePaths) "Could not restore the latest game files."
        Write-Host "Game files are up to date." -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

function Get-GamePython {
    $venvPython = Join-Path $RepoDir ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
    }

    $basePython = Get-BasePython
    Write-Host "Creating local Python environment..." -ForegroundColor Cyan
    Invoke-Checked $basePython.FilePath ($basePython.Arguments + @("-m", "venv", (Join-Path $RepoDir ".venv"))) "Could not create the Python environment."

    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "The Python environment was not created correctly."
    }

    return $venvPython
}

function Ensure-Requirements {
    param([string]$PythonExe)

    & $PythonExe -c "import pygame" *> $null
    if ($LASTEXITCODE -eq 0) {
        return
    }

    Write-Host "Installing game packages..." -ForegroundColor Cyan
    Invoke-Checked $PythonExe @("-m", "pip", "install", "--upgrade", "pip") "Could not upgrade pip."
    Invoke-Checked $PythonExe @("-m", "pip", "install", "-r", (Join-Path $RepoDir "requirements.txt")) "Could not install game packages."
}

try {
    Update-GameFiles
    $python = Get-GamePython
    Ensure-Requirements $python

    Push-Location $RepoDir
    try {
        & $python "main.py"
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    exit $exitCode
}
catch {
    Write-Host ""
    Write-Host "Dragon's Lair RPG could not start:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}
