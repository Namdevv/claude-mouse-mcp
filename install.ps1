<#
.SYNOPSIS
  Cài đặt + đăng ký claude-mouse-mcp vào Claude Code bằng 1 lệnh.

.DESCRIPTION
  Tự dò thư mục dự án, tạo venv (nếu chưa có), cài package,
  rồi đăng ký MCP server với Claude Code dùng đường dẫn tuyệt đối
  được sinh tự động (không hardcode path cá nhân).

.PARAMETER Scope
  Phạm vi đăng ký: user (mặc định) | local | project.

.PARAMETER Name
  Tên MCP server. Mặc định: claude-mouse.

.PARAMETER NoPermission
  Bỏ qua bước cấp quyền auto-approve. Mặc định script SẼ cấp quyền.

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

# Thư mục dự án = nơi chứa script này
$ProjectDir = $PSScriptRoot
$Python = Join-Path $ProjectDir '.venv\Scripts\python.exe'

Write-Host "Project: $ProjectDir" -ForegroundColor Cyan

# 1. Tạo venv nếu chưa có
if (-not (Test-Path $Python)) {
    Write-Host "Tao venv..." -ForegroundColor Yellow
    py -m venv (Join-Path $ProjectDir '.venv')
}

# 2. Cài package (editable)
Write-Host "Cai package..." -ForegroundColor Yellow
& $Python -m pip install -e $ProjectDir --quiet

# 3. Kiem tra claude CLI
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Error "Khong tim thay 'claude' CLI trong PATH. Cai Claude Code truoc."
}

# 4. Go dang ky cu (neu co) roi dang ky lai -> idempotent
try { claude mcp remove $Name --scope $Scope 2>&1 | Out-Null } catch {}

Write-Host "Dang ky MCP server '$Name' (scope=$Scope)..." -ForegroundColor Yellow
claude mcp add $Name --scope $Scope -- $Python -m claude_mouse_mcp.server

# 5. Cap quyen auto-approve vao .claude/settings.local.json (chi may nay)
if (-not $NoPermission) {
    Write-Host "Cap quyen auto-approve cho '$Name'..." -ForegroundColor Yellow

    $SettingsDir = Join-Path $ProjectDir '.claude'
    $SettingsFile = Join-Path $SettingsDir 'settings.local.json'
    if (-not (Test-Path $SettingsDir)) { New-Item -ItemType Directory -Path $SettingsDir | Out-Null }

    # Doc settings cu (neu co), neu khong tao moi
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

    # Rule: server tong + tung tool (tuong thich moi version)
    $tools = @('get_screen_size','get_cursor_position','screenshot','move_mouse',
               'click','drag','scroll','type_text','press_key')
    $rules = @("mcp__$Name") + ($tools | ForEach-Object { "mcp__${Name}__$_" })

    $allow = [System.Collections.Generic.List[string]]::new()
    foreach ($r in $settings.permissions.allow) { $allow.Add($r) }
    foreach ($r in $rules) { if (-not $allow.Contains($r)) { $allow.Add($r) } }
    $settings.permissions.allow = $allow

    $json = $settings | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($SettingsFile, $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Da ghi quyen vao $SettingsFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "Xong. Kiem tra bang: claude mcp list" -ForegroundColor Green
Write-Host "LUU Y: Thoat han Claude Code roi mo lai de nap server + quyen." -ForegroundColor Magenta
