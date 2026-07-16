param(
    [string[]]$SearchRoots = @()
)

$ErrorActionPreference = "Stop"

function Add-ExistingRoot {
    param(
        [System.Collections.Generic.List[string]]$Roots,
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return
    }

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $Path).ProviderPath
    if (-not $Roots.Contains($resolved)) {
        $Roots.Add($resolved)
    }
}

function Invoke-GitText {
    param(
        [string]$RepoPath,
        [string[]]$Arguments
    )

    $output = & git -c "safe.directory=$RepoPath" -C $RepoPath @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        return "<git failed: $($output -join ' ')>"
    }

    return ($output -join "`n").Trim()
}

function Get-CopyInfo {
    param(
        [string]$FolderPath
    )

    $hasGit = Test-Path -LiteralPath (Join-Path $FolderPath ".git")
    $hasGameFile = Test-Path -LiteralPath (Join-Path $FolderPath "main.py")
    $hasReadme = Test-Path -LiteralPath (Join-Path $FolderPath "README.md")

    if (-not ($hasGit -or ($hasGameFile -and $hasReadme))) {
        return $null
    }

    if (-not $hasGit) {
        return [PSCustomObject]@{
            Path = $FolderPath
            Git = "no"
            Branch = ""
            Head = ""
            Origin = ""
            DirtyCount = ""
            Note = "Looks like a source folder, but no .git folder was found."
        }
    }

    $branchLine = Invoke-GitText $FolderPath @("status", "--short", "--branch")
    $statusLines = @()
    if ($branchLine) {
        $statusLines = $branchLine -split "`n"
    }

    $head = Invoke-GitText $FolderPath @("log", "-1", "--pretty=%h %s")
    $origin = Invoke-GitText $FolderPath @("remote", "get-url", "origin")
    $dirtyCount = 0
    foreach ($line in $statusLines) {
        if ($line -and -not $line.StartsWith("##")) {
            $dirtyCount += 1
        }
    }

    # BEGINNER CODE LABEL: Read-only local-copy report.
    # This script prints useful facts and never runs pull, reset, clean, delete,
    # or checkout. Older folders can contain unique work, so inspection comes
    # before any update command.
    return [PSCustomObject]@{
        Path = $FolderPath
        Git = "yes"
        Branch = ($statusLines | Select-Object -First 1)
        Head = $head
        Origin = $origin
        DirtyCount = $dirtyCount
        Note = if ($dirtyCount -gt 0) { "Review before updating." } else { "Clean at scan time." }
    }
}

$roots = [System.Collections.Generic.List[string]]::new()
if ($SearchRoots.Count -gt 0) {
    foreach ($root in $SearchRoots) {
        Add-ExistingRoot $roots $root
    }
}
else {
    Add-ExistingRoot $roots (Join-Path $env:USERPROFILE "Documents")
    Add-ExistingRoot $roots ([Environment]::GetFolderPath("MyDocuments"))
    if ($env:OneDrive) {
        Add-ExistingRoot $roots (Join-Path $env:OneDrive "Documents")
    }
}

$candidatePaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($root in $roots) {
    Get-ChildItem -LiteralPath $root -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "Tboy450|Dragon.?Lair|RPG" } |
        ForEach-Object { [void]$candidatePaths.Add($_.FullName) }
}

$reports = foreach ($path in ($candidatePaths | Sort-Object)) {
    Get-CopyInfo $path
}

$reports |
    Where-Object { $null -ne $_ } |
    Sort-Object Path |
    Format-List

Write-Host ""
Write-Host "Inventory only. Preserve unique commits before pulling, cleaning, or deleting old folders." -ForegroundColor Yellow
