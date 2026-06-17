<#
.SYNOPSIS
  Install + register claude-mouse-mcp with Claude Code in a single command.

.DESCRIPTION
  Auto-detects the project directory, creates a venv (if missing), installs the
  package, then registers the MCP server with Claude Code using an
  auto-generated absolute path (no hardcoded personal path).

.PARAMETER Scope
  Registration scope: user (default) | local | project.

.PARAMETER Name
  MCP server name. Default: claude-mouse.

.PARAMETER NoPermission
  Skip the auto-approve permission step. By default the script DOES grant permissions.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install.ps1
#>
param(
    [ValidateSet('user', 'local', 'project')]
    [string]$Scope = 'user',
    [string]$Name = 'claude-mouse',
    [switch]$NoPermission
)

$ErrorActionPreference = 'Stop'

# Project directory = the folder containing this script
$ProjectDir = $PSScriptRoot
$Python = Join-Path $ProjectDir '.venv\Scripts\python.exe'

Write-Host "Project: $ProjectDir" -ForegroundColor Cyan

# 1. Create venv if missing
if (-not (Test-Path $Python)) {
    Write-Host "Creating venv..." -ForegroundColor Yellow
    py -m venv (Join-Path $ProjectDir '.venv')
}

# 2. Install the package (editable)
Write-Host "Installing package..." -ForegroundColor Yellow
& $Python -m pip install -e $ProjectDir --quiet

# 3. Check for the claude CLI
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Error "Could not find the 'claude' CLI on PATH. Install Claude Code first."
}

# 4. Remove the old registration (if any) then re-register -> idempotent
try { claude mcp remove $Name --scope $Scope 2>&1 | Out-Null } catch {}

Write-Host "Registering MCP server '$Name' (scope=$Scope)..." -ForegroundColor Yellow
claude mcp add $Name --scope $Scope -- $Python -m claude_mouse_mcp.server

# 5. Grant auto-approve permissions in .claude/settings.local.json (this machine only)
if (-not $NoPermission) {
    Write-Host "Granting auto-approve permissions for '$Name'..." -ForegroundColor Yellow

    $SettingsDir = Join-Path $ProjectDir '.claude'
    $SettingsFile = Join-Path $SettingsDir 'settings.local.json'
    if (-not (Test-Path $SettingsDir)) { New-Item -ItemType Directory -Path $SettingsDir | Out-Null }

    # Read existing settings (if any), otherwise create new
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

    # Rules: whole server + each tool (compatible across versions)
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
