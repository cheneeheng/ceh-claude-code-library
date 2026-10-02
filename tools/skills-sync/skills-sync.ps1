<#
.SYNOPSIS
    skills-sync — copy Claude Code skills from a GitHub repo or local folder
    into a project's .claude/skills/ directory.

.DESCRIPTION
    Behaviorally equivalent to skills-sync.py and produces byte-compatible
    .claude/skills/.manifest.json manifests (same keys, same key order, same
    JSON formatting: 2-space indent, trailing newline, LF line endings).

    Requires PowerShell 7+ (pwsh). This script targets pwsh for cross-platform
    consistency (Linux/macOS/Windows) and to avoid Windows PowerShell 5.1
    quirks around UTF-8 (no BOM) output and JSON formatting. No PS7-only
    operators (??, ?., ternary ?:) are used, but pwsh is the supported and
    tested runtime.

.USAGE
    ./skills-sync.ps1 install (-Repo owner/name [-Ref REF] | -Path DIR) `
        [-Skills a,b|all] [-Target DIR] [-Token TOKEN]
    ./skills-sync.ps1 update [-Skills a,b|all] [-Target DIR] [-Token TOKEN]
    ./skills-sync.ps1 add -Skills a,b [-Target DIR] [-Token TOKEN]
    ./skills-sync.ps1 remove -Skills a,b [-Target DIR]
    ./skills-sync.ps1 list [-Target DIR]

    Flag names match the spec (Repo, Path, Ref, Skills, Target, Token).
    PowerShell's automatic case-insensitive prefix matching also allows
    `--repo`, `--path`, etc. as long as the leading dashes are stripped by
    the caller's shell — use the `-Name value` form shown above.
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("install", "update", "add", "remove", "list")]
    [string]$Command,

    [string]$Repo,
    [string]$Path,
    [string]$Ref,
    [string]$Skills,
    [string]$Target = ".",
    [string]$Token
)

$ErrorActionPreference = "Stop"

$MANIFEST_NAME = ".manifest.json"
$OLD_GITIGNORE_LINE = "skills/"  # legacy blanket-ignore line; migrated away from

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Write-ErrorAndExit {
    param([string]$Message, [int]$Code = 1)
    [Console]::Error.WriteLine("error: $Message")
    exit $Code
}

function Get-NowIso {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss+00:00")
}

function Get-SkillsDir {
    param([string]$TargetDir)
    return Join-Path (Join-Path $TargetDir ".claude") "skills"
}

function Get-ManifestPath {
    param([string]$TargetDir)
    return Join-Path (Get-SkillsDir $TargetDir) $MANIFEST_NAME
}

# Load the manifest preserving key order. Returns $null if not found.
# The result is an [ordered] hashtable so callers can mutate/rewrite while
# preserving original key order and unknown keys.
function Get-Manifest {
    param([string]$TargetDir)

    $path = Get-ManifestPath $TargetDir
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $path -Raw -Encoding utf8
    $obj = $raw | ConvertFrom-Json

    $ordered = [ordered]@{}
    foreach ($prop in $obj.PSObject.Properties) {
        if ($prop.Name -eq "skills") {
            # Normalize to a plain string array regardless of how the JSON
            # parser represented it (single value, array, or null/missing).
            $vals = @()
            if ($null -ne $prop.Value) {
                foreach ($v in @($prop.Value)) { $vals += [string]$v }
            }
            $ordered["skills"] = $vals
        }
        else {
            $ordered[$prop.Name] = $prop.Value
        }
    }
    return $ordered
}

# Write the manifest as JSON: 2-space indent, LF line endings, trailing
# newline, UTF-8 without BOM. $Manifest must be an [ordered] hashtable (or
# anything ConvertTo-Json renders with stable key order).
function Save-Manifest {
    param([string]$TargetDir, $Manifest)

    $path = Get-ManifestPath $TargetDir
    $dir = Split-Path -Parent $path
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $json = $Manifest | ConvertTo-Json -Depth 10
    # Normalize line endings to LF and ensure a single trailing newline.
    $json = $json -replace "`r`n", "`n"
    $json = $json.TrimEnd("`n") + "`n"

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($path, $json, $utf8NoBom)
}

# Lines that should be present in .claude/.gitignore: one for the manifest
# itself, plus one per currently-installed skill folder.
function Get-GitignoreLines {
    param([string[]]$SkillNames)

    $lines = [System.Collections.Generic.List[string]]::new()
    $lines.Add("skills/$MANIFEST_NAME")
    foreach ($name in (@($SkillNames) | Sort-Object -Unique)) {
        $lines.Add("skills/$name/")
    }
    return @($lines)
}

# Read .claude/.gitignore as a list of lines (no trailing empty element from
# a final newline), or an empty array if the file is absent/empty.
function Read-GitignoreLines {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return @()
    }
    $content = Get-Content -LiteralPath $Path -Raw -Encoding utf8
    if ($null -eq $content -or $content.Length -eq 0) {
        return @()
    }
    $lines = @($content -split "`r?`n")
    if ($lines.Count -gt 0 -and $lines[-1] -eq "") {
        $lines = $lines[0..($lines.Count - 2)]
    }
    return @($lines)
}

# Ensure .claude/.gitignore ignores the manifest and each given skill's
# folder individually (not the whole skills/ directory), so a project can
# track its own custom skills alongside synced ones.
#
# Migrates away from the old blanket "skills/" line if present. Appends any
# missing lines without reordering existing content; never duplicates a line.
function Confirm-Gitignore {
    param([string]$TargetDir, [string[]]$SkillNames)

    $claudeDir = Join-Path $TargetDir ".claude"
    if (-not (Test-Path -LiteralPath $claudeDir)) {
        New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
    }
    $path = Join-Path $claudeDir ".gitignore"

    $lines = Read-GitignoreLines -Path $path
    $before = $lines -join "`n"

    $lines = @($lines | Where-Object { $_ -ne $OLD_GITIGNORE_LINE })

    foreach ($line in (Get-GitignoreLines -SkillNames $SkillNames)) {
        if ($lines -notcontains $line) {
            $lines += $line
        }
    }

    $after = $lines -join "`n"
    if ($after -eq $before) {
        return
    }

    [System.IO.File]::WriteAllText($path, $after + "`n", (New-Object System.Text.UTF8Encoding($false)))
}

# Remove the gitignore line for each given skill name ("skills/<name>/"),
# preserving all other lines and their order. No-op if the file is absent.
function Remove-GitignoreLines {
    param([string]$TargetDir, [string[]]$SkillNames)

    $path = Join-Path (Join-Path $TargetDir ".claude") ".gitignore"
    $lines = Read-GitignoreLines -Path $path
    if ($lines.Count -eq 0) {
        return
    }

    $toRemove = @($SkillNames | ForEach-Object { "skills/$_/" })
    $newLines = @($lines | Where-Object { $toRemove -notcontains $_ })

    if ($newLines.Count -eq $lines.Count) {
        return
    }

    $content = if ($newLines.Count -gt 0) { ($newLines -join "`n") + "`n" } else { "" }
    [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false)))
}

# Recursively find every directory that directly contains a SKILL.md.
# Returns an (ordered) hashtable mapping skill name -> absolute directory path.
# A SKILL.md at $Root itself is skipped. If two directories share a basename,
# the later one found wins and a warning is printed to stderr.
function Find-Skills {
    param([string]$RootPath)

    $root = (Resolve-Path -LiteralPath $RootPath).ProviderPath
    $available = @{}

    $skillFiles = Get-ChildItem -LiteralPath $root -Recurse -Filter "SKILL.md" -File |
        Sort-Object -Property FullName

    foreach ($skillMd in $skillFiles) {
        $skillDir = Split-Path -Parent $skillMd.FullName
        $normalizedSkillDir = $skillDir.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
        $normalizedRoot = $root.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)

        if ($normalizedSkillDir -eq $normalizedRoot) {
            continue
        }

        $name = Split-Path -Leaf $skillDir

        if ($available.ContainsKey($name) -and $available[$name] -ne $skillDir) {
            [Console]::Error.WriteLine("warning: duplicate skill name '$name' found at '$skillDir' and '$($available[$name])' - using the latter")
        }
        $available[$name] = $skillDir
    }

    return $available
}

# Resolve a -Skills value ('all', a comma list, or empty/$null) against the
# skills available in the source. Errors out (and exits) on unknown names.
function Resolve-Selection {
    param([string]$Requested, [hashtable]$Available)

    if ($null -eq $Requested -or $Requested.Trim().ToLowerInvariant() -eq "all") {
        return @($Available.Keys | Sort-Object)
    }

    $names = @($Requested -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    $names = @($names | Sort-Object -Unique)

    $unknown = @($names | Where-Object { -not $Available.ContainsKey($_) })
    if ($unknown.Count -gt 0) {
        $availableList = @($Available.Keys | Sort-Object)
        $availableStr = if ($availableList.Count -gt 0) { $availableList -join ", " } else { "(none)" }
        Write-ErrorAndExit "unknown skill(s): $($unknown -join ', '). Available: $availableStr"
    }

    return $names
}

# Wipe-and-replace copy of a single skill directory into <skillsRoot>/<name>/
function Copy-Skill {
    param([string]$SourceDir, [string]$SkillsRoot, [string]$Name)

    $dest = Join-Path $SkillsRoot $Name
    if (Test-Path -LiteralPath $dest) {
        Remove-Item -LiteralPath $dest -Recurse -Force
    }
    New-Item -ItemType Directory -Path $dest -Force | Out-Null

    # Copy contents of SourceDir into dest (not the SourceDir itself).
    $items = Get-ChildItem -LiteralPath $SourceDir -Force
    foreach ($item in $items) {
        Copy-Item -LiteralPath $item.FullName -Destination $dest -Recurse -Force
    }
}

# Download and extract a GitHub repo tarball to a temp dir.
# Returns a hashtable with Root (path to the extracted repo contents, past
# the owner-repo-<sha>/ wrapper) and TmpDir (caller must remove it).
function Get-GitHubSource {
    param([string]$RepoName, [string]$RefName, [string]$AuthToken)

    if ($AuthToken) {
        $url = "https://api.github.com/repos/$RepoName/tarball/$RefName"
    }
    else {
        $url = "https://codeload.github.com/$RepoName/tar.gz/$RefName"
    }

    $tmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ("skills-sync-" + [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

    try {
        $tarballPath = Join-Path $tmpDir "repo.tar.gz"

        $headers = @{ "User-Agent" = "skills-sync" }
        if ($AuthToken) {
            $headers["Authorization"] = "Bearer $AuthToken"
        }

        try {
            Invoke-WebRequest -Uri $url -Headers $headers -OutFile $tarballPath -UseBasicParsing
        }
        catch {
            $statusCode = $null
            if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            if ($statusCode -eq 404) {
                Write-ErrorAndExit "HTTP 404 fetching $url (check repo/ref/token - private repos 404 without a token)"
            }
            elseif ($null -ne $statusCode) {
                Write-ErrorAndExit "HTTP $statusCode fetching $url"
            }
            else {
                Write-ErrorAndExit "network error fetching $url`: $($_.Exception.Message)"
            }
        }

        $extractDir = Join-Path $tmpDir "extracted"
        New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

        $tarExe = Get-Command tar -ErrorAction SilentlyContinue
        if (-not $tarExe) {
            Write-ErrorAndExit "'tar' was not found on PATH; it is required to extract the downloaded archive"
        }

        & tar -xzf $tarballPath -C $extractDir
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorAndExit "failed to extract archive downloaded from $url (tar exit code $LASTEXITCODE)"
        }

        $entries = @(Get-ChildItem -LiteralPath $extractDir -Force)
        if ($entries.Count -eq 1 -and $entries[0].PSIsContainer) {
            $root = $entries[0].FullName
        }
        else {
            $root = $extractDir
        }

        return @{ Root = $root; TmpDir = $tmpDir }
    }
    catch {
        Remove-Item -LiteralPath $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
        throw
    }
}

# Resolve and validate a -Path local source. Returns a hashtable with
# Root (absolute path) and Available (hashtable of skill name -> dir).
function Get-LocalSource {
    param([string]$SourcePath, [string]$TargetDir)

    if (-not (Test-Path -LiteralPath $SourcePath -PathType Container)) {
        Write-ErrorAndExit "local source path does not exist or is not a directory: $SourcePath"
    }

    $src = (Resolve-Path -LiteralPath $SourcePath).ProviderPath

    # Self-copy guard: the resolved source directory must not be the same as,
    # or nested inside, the target's .claude/skills/. Use GetFullPath (not
    # Resolve-Path) since .claude/skills/ may not exist yet.
    $targetSkillsDir = Get-SkillsDir $TargetDir
    $targetSkillsResolved = [System.IO.Path]::GetFullPath($targetSkillsDir)
    $srcWithSep = $src.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    $targetWithSep = $targetSkillsResolved.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

    if ($src -eq $targetSkillsResolved -or $srcWithSep.StartsWith($targetWithSep)) {
        Write-ErrorAndExit "source path '$src' is inside the target's .claude/skills/ - refusing to self-copy"
    }

    $available = Find-Skills $src
    if ($available.Count -eq 0) {
        Write-ErrorAndExit "no skills (SKILL.md) found under '$src'"
    }

    return @{ Root = $src; Available = $available }
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

function Invoke-Install {
    if ($Repo -and $Path) {
        Write-ErrorAndExit "exactly one of -Repo or -Path is required (got both)"
    }
    if (-not $Repo -and -not $Path) {
        Write-ErrorAndExit "exactly one of -Repo or -Path is required (got neither)"
    }
    if ($Path -and $PSBoundParameters.ContainsKey("Ref")) {
        Write-ErrorAndExit "-Ref is only valid with -Repo"
    }

    $cleanupDir = $null
    try {
        if ($Repo) {
            $effectiveRef = $Ref
            if ([string]::IsNullOrEmpty($effectiveRef)) { $effectiveRef = "main" }

            $ghSource = Get-GitHubSource -RepoName $Repo -RefName $effectiveRef -AuthToken $Token
            $cleanupDir = $ghSource.TmpDir
            $srcRoot = $ghSource.Root

            $available = Find-Skills $srcRoot
            if ($available.Count -eq 0) {
                Write-ErrorAndExit "no skills (SKILL.md) found in $Repo@$effectiveRef"
            }
        }
        else {
            $localSource = Get-LocalSource -SourcePath $Path -TargetDir $Target
            $srcRoot = $localSource.Root
            $available = $localSource.Available
        }

        $selection = Resolve-Selection -Requested $Skills -Available $available
        if ($selection.Count -eq 0) {
            Write-ErrorAndExit "no skills selected"
        }

        $skillsRoot = Get-SkillsDir $Target
        if (-not (Test-Path -LiteralPath $skillsRoot)) {
            New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
        }

        foreach ($name in $selection) {
            Copy-Skill -SourceDir $available[$name] -SkillsRoot $skillsRoot -Name $name
        }

        $manifest = [ordered]@{}
        if ($Repo) {
            $manifest["source"] = "github"
            $manifest["repo"] = $Repo
            $manifest["ref"] = $effectiveRef
        }
        else {
            $manifest["source"] = "local"
            $manifest["path"] = $srcRoot
        }
        $manifest["updated"] = Get-NowIso
        $manifest["skills"] = @($selection)

        Save-Manifest -TargetDir $Target -Manifest $manifest
        Confirm-Gitignore -TargetDir $Target -SkillNames $selection

        Write-Output "Installed $($selection.Count) skill(s): $($selection -join ', ')"
    }
    finally {
        if ($cleanupDir) {
            Remove-Item -LiteralPath $cleanupDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-Update {
    param([bool]$RequireSkills = $false)

    $manifest = Get-Manifest -TargetDir $Target
    if ($null -eq $manifest) {
        Write-ErrorAndExit "no manifest found - run install first"
    }

    if ($RequireSkills -and [string]::IsNullOrEmpty($Skills)) {
        Write-ErrorAndExit "-Skills is required for 'add'"
    }

    $source = $null
    if ($manifest.Contains("source")) { $source = $manifest["source"] }
    if ($null -eq $source -or $source -eq "") {
        if ($manifest.Contains("repo")) { $source = "github" } else { $source = "local" }
    }

    $cleanupDir = $null
    try {
        if ($source -eq "github") {
            $repoName = $manifest["repo"]
            $refName = "main"
            if ($manifest.Contains("ref") -and $manifest["ref"]) { $refName = $manifest["ref"] }

            $ghSource = Get-GitHubSource -RepoName $repoName -RefName $refName -AuthToken $Token
            $cleanupDir = $ghSource.TmpDir
            $srcRoot = $ghSource.Root
        }
        elseif ($source -eq "local") {
            $srcRoot = $manifest["path"]
            if (-not (Test-Path -LiteralPath $srcRoot -PathType Container)) {
                Write-ErrorAndExit "local source path no longer exists: $srcRoot. If the folder moved, re-run 'install -Path' instead."
            }
        }
        else {
            Write-ErrorAndExit "unknown manifest source: '$source'"
        }

        $available = Find-Skills $srcRoot

        if (-not [string]::IsNullOrEmpty($Skills)) {
            $selection = Resolve-Selection -Requested $Skills -Available $available
        }
        else {
            $oldSkills = @()
            if ($manifest.Contains("skills") -and $manifest["skills"]) { $oldSkills = @($manifest["skills"]) }
            $availableNames = @($available.Keys)
            $selection = @($oldSkills | Where-Object { $availableNames -contains $_ } | Sort-Object -Unique)
        }

        $skillsRoot = Get-SkillsDir $Target
        if (-not (Test-Path -LiteralPath $skillsRoot)) {
            New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
        }

        foreach ($name in $selection) {
            Copy-Skill -SourceDir $available[$name] -SkillsRoot $skillsRoot -Name $name
        }

        $oldSkills = @()
        if ($manifest.Contains("skills") -and $manifest["skills"]) { $oldSkills = @($manifest["skills"]) }
        $unionSkills = @($oldSkills + $selection | Sort-Object -Unique)

        $manifest["skills"] = $unionSkills
        $manifest["updated"] = Get-NowIso

        Save-Manifest -TargetDir $Target -Manifest $manifest
        Confirm-Gitignore -TargetDir $Target -SkillNames $unionSkills

        $selectionStr = if ($selection.Count -gt 0) { $selection -join ", " } else { "(none)" }
        Write-Output "Updated $($selection.Count) skill(s): $selectionStr"
    }
    finally {
        if ($cleanupDir) {
            Remove-Item -LiteralPath $cleanupDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-Add {
    Invoke-Update -RequireSkills $true
}

function Invoke-Remove {
    if ([string]::IsNullOrWhiteSpace($Skills)) {
        Write-ErrorAndExit "-Skills is required for 'remove'"
    }

    $manifest = Get-Manifest -TargetDir $Target
    if ($null -eq $manifest) {
        Write-ErrorAndExit "no manifest found - run install first"
    }

    $names = @($Skills -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    $names = @($names | Sort-Object -Unique)
    if ($names.Count -eq 0) {
        Write-ErrorAndExit "-Skills is required for 'remove'"
    }

    $skillsRoot = Get-SkillsDir $Target

    $existingSkills = @()
    if ($manifest.Contains("skills") -and $manifest["skills"]) { $existingSkills = @($manifest["skills"]) }

    $removed = @()
    $remaining = [System.Collections.Generic.List[string]]::new()
    foreach ($s in $existingSkills) { $remaining.Add($s) }

    foreach ($name in $names) {
        $skillPath = Join-Path $skillsRoot $name
        if (Test-Path -LiteralPath $skillPath) {
            Remove-Item -LiteralPath $skillPath -Recurse -Force
        }
        if ($remaining.Contains($name)) {
            $remaining.Remove($name) | Out-Null
            $removed += $name
        }
    }

    $manifest["skills"] = @($remaining | Sort-Object -Unique)
    $manifest["updated"] = Get-NowIso

    Save-Manifest -TargetDir $Target -Manifest $manifest
    Remove-GitignoreLines -TargetDir $Target -SkillNames $names

    $removedStr = if ($removed.Count -gt 0) { $removed -join ", " } else { "(none found)" }
    Write-Output "Removed $($removed.Count) skill(s): $removedStr"
}

function Invoke-List {
    $manifest = Get-Manifest -TargetDir $Target
    if ($null -eq $manifest) {
        Write-ErrorAndExit "no manifest found - run install first"
    }

    $source = $null
    if ($manifest.Contains("source")) { $source = $manifest["source"] }
    if ($null -eq $source -or $source -eq "") {
        if ($manifest.Contains("repo")) { $source = "github" } else { $source = "local" }
    }

    if ($source -eq "github") {
        $refName = "main"
        if ($manifest.Contains("ref") -and $manifest["ref"]) { $refName = $manifest["ref"] }
        $label = "$($manifest['repo'])@$refName"
    }
    else {
        $label = "(unknown path)"
        if ($manifest.Contains("path") -and $manifest["path"]) { $label = $manifest["path"] }
    }

    $updated = "unknown"
    if ($manifest.Contains("updated") -and $manifest["updated"]) { $updated = $manifest["updated"] }

    Write-Output "$label (updated $updated)"

    $skillsList = @()
    if ($manifest.Contains("skills") -and $manifest["skills"]) { $skillsList = @($manifest["skills"]) }
    foreach ($name in $skillsList) {
        Write-Output "  $name"
    }
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

switch ($Command) {
    "install" { Invoke-Install }
    "update"  { Invoke-Update -RequireSkills $false }
    "add"     { Invoke-Add }
    "remove"  { Invoke-Remove }
    "list"    { Invoke-List }
}
