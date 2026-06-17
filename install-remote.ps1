<#
.SYNOPSIS
  Install claude-mouse-mcp REMOTELY — no git clone needed.

.DESCRIPTION
  Uses `uvx` to run the package directly from GitHub (auto-downloads it and
  creates an isolated environment in the cache, no manual venv). The script:
    1. Installs `uv` if the machine doesn't have it.
    2. Registers the MCP server with Claude Code via `claude mcp add ... uvx --from git+...`.
    3. Grants auto-approve permissions for the tools.

  Quick run (one line, uses defaults):
    irm https://raw.githubusercontent.com/Namdevv/claude-mouse-mcp/main/install-remote.ps1 | iex

  To customize parameters, download it first then run:
    irm https://raw.githubusercontent.com/Namdevv/claude-mouse-mcp/main/install-remote.ps1 -OutFile install-remote.ps1
    .\install-remote.ps1 -Scope local -Name my-mouse

.PARAMETER Scope
  Registration scope: user (default) | local | project.

.PARAMETER Name
  MCP server name. Default: claude-mouse.

.PARAMETER Ref
  Repo branch / tag / commit to pin a version. Default: main.

.PARAMETER NoPermission
  Skip the auto-approve permission step.
#>
param(
    [ValidateSet('user', 'local', 'project')]
    [string]$Scope = 'user',
    [string]$Name = 'claude-mouse',
    [string]$Ref = 'main',
    [switch]$NoPermission
)

$ErrorActionPreference = 'Stop'

$Repo = 'https://github.com/Namdevv/claude-mouse-mcp.git'
$Source = "git+$Repo@$Ref"

# 1. Make sure uv/uvx is available
if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Yellow
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    # Load uv into PATH for the current session
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
        Write-Error "uv was installed but is not on PATH yet. Reopen your terminal and run the script again."
    }
}

# 2. Check for the claude CLI
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Error "Could not find the 'claude' CLI on PATH. Install Claude Code first."
}

# 3. Remove the old registration (if any) then re-register -> idempotent
try { claude mcp remove $Name --scope $Scope 2>&1 | Out-Null } catch {}

Write-Host "Registering MCP server '$Name' (scope=$Scope) via uvx from GitHub..." -ForegroundColor Yellow
claude mcp add $Name --scope $Scope -- uvx --from $Source claude-mouse-mcp

# 4. Grant auto-approve permissions
if (-not $NoPermission) {
    Write-Host "Granting auto-approve permissions for '$Name'..." -ForegroundColor Yellow

    # User scope -> ~/.claude/settings.json ; otherwise -> .claude/settings.local.json in the current directory
    if ($Scope -eq 'user') {
        $SettingsDir  = Join-Path $env:USERPROFILE '.claude'
        $SettingsFile = Join-Path $SettingsDir 'settings.json'
    } else {
        $SettingsDir  = Join-Path (Get-Location) '.claude'
        $SettingsFile = Join-Path $SettingsDir 'settings.local.json'
    }
    if (-not (Test-Path $SettingsDir)) { New-Item -ItemType Directory -Path $SettingsDir | Out-Null }

    if (Test-Path $SettingsFile) {
        $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json
    } else {
        $settings = [PSCustomObject]@{}
    }
    if (-not $settings.PSObject.Properties['permissions']) {
        $settings | Add-Member permissions ([PSCustomObject]@{}) -Force
    }
    if (-not $settings.permissions.PSObject.Properties['allow']) {
        $settings.permissions | Add-Member allow @() -Force
    }

    $tools = @('get_screen_size','get_cursor_position','screenshot','move_mouse',
               'click','drag','scroll','type_text','press_key')
    $rules = @("mcp__$Name") + ($tools | ForEach-Object { "mcp__${Name}__$_" })

    $allow = [System.Collections.Generic.List[string]]::new()
    foreach ($r in $settings.permissions.allow) { $allow.Add($r) }
    foreach ($r in $rules) { if (-not $allow.Contains($r)) { $allow.Add($r) } }
    $settings.permissions.allow = $allow

    $json = $settings | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($SettingsFile, $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Wrote permissions to $SettingsFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done. Verify with: claude mcp list" -ForegroundColor Green
Write-Host "NOTE: Fully quit Claude Code and reopen it to load the server + permissions." -ForegroundColor Magenta
Write-Host "On the first server start, uvx downloads the package from GitHub (a bit slow)." -ForegroundColor DarkGray
