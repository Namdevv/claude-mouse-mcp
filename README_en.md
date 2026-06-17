# claude-mouse-mcp

<sub>📖 [Tiếng Việt](README.md) · **English**</sub>

> An MCP server that lets **Claude see your screen and control the mouse/keyboard** on your Windows machine.

<p align="left">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="MCP" src="https://img.shields.io/badge/MCP-stdio-6E40C9">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="CI" src="https://github.com/Namdevv/claude-mouse-mcp/actions/workflows/ci.yml/badge.svg">
</p>

Claude works in a **see → decide → act → verify** loop:

```
screenshot ──▶ (Claude analyzes) ──▶ move_mouse / click / type_text ──▶ screenshot
   ▲                                                                        │
   └──────────────────────────────  repeat  ───────────────────────────────┘
```

Runs over the **stdio transport**, so it works with **Claude Code (CLI)**, **Claude Desktop**, and **Codex CLI**.

---

## 🎬 Demo

<video src="https://github.com/Namdevv/claude-mouse-mcp/raw/main/docs/demo.mp4" controls muted width="100%"></video>

> ▶️ If the player above doesn't load, **[click here to watch the demo](https://github.com/Namdevv/claude-mouse-mcp/raw/main/docs/demo.mp4)**.

---

## ✨ Features

- 👁️ **See the screen** — capture the full screen or a region and send the image straight to Claude.
- 🖱️ **Control the mouse** — move, click (left/right/middle, single/double), drag & drop, scroll.
- ⌨️ **Control the keyboard** — type text, press keys and shortcuts (`ctrl+c`, `alt+f4`, ...).
- 🎯 **DPI-aware** — click coordinates match real pixels even when the display is scaled to 125% / 150%.
- 🪙 **Token-friendly** — images are auto-scaled down to a max width of 1280px.
- 🛑 **Emergency brake** — fling the mouse into a screen corner to stop every action instantly.

## 💬 Example prompts

Once the server is connected, just talk to Claude in natural language — it will
take a screenshot, figure out the coordinates, and act. Try things like:

- _"Take a screenshot and tell me what's on my screen right now."_
- _"Open the Start menu, search for **Notepad**, and open it."_
- _"In the open window, type 'Hello from Claude' then save the file as notes.txt on the Desktop."_
- _"Find the Chrome icon on the taskbar and click it, then go to github.com."_
- _"Scroll down this page until you see the **Pricing** section."_
- _"Select all the text in this field (ctrl+a), copy it, and tell me what it says."_
- _"Close the active window with alt+f4."_
- _"Drag the file on the left into the folder on the right."_

> 💡 Tip: ask Claude to **screenshot and verify after each step** for the most
> reliable results — that's the see → act → verify loop it's built around.

## 📋 Requirements

| Component | Version |
|-----------|---------|
| Operating system | Windows 10 / 11 |
| Python | 3.10 or newer |
| Client | [Claude Code (CLI)](https://docs.claude.com/en/docs/claude-code), Claude Desktop, or Codex CLI |

## 🚀 Quick install (NO clone needed)

Just one command in PowerShell — the script installs [`uv`](https://docs.astral.sh/uv/) (if missing), registers the MCP server via `uvx`, and grants auto-approve permissions:

```powershell
irm https://raw.githubusercontent.com/Namdevv/claude-mouse-mcp/main/install-remote.ps1 | iex
```

`uvx` **downloads the package from GitHub** into an isolated cached environment — no `git clone`, no manual `.venv`. The first time Claude starts the server it will be a little slow while uvx fetches the package.

To customize (change the name, scope, or pin a version), download the script then run it:

```powershell
irm https://raw.githubusercontent.com/Namdevv/claude-mouse-mcp/main/install-remote.ps1 -OutFile install-remote.ps1
.\install-remote.ps1 -Scope local -Name my-mouse -Ref v0.1.0
```

Or register directly with a single command (no script, grant permissions yourself afterwards):

```powershell
claude mcp add claude-mouse -- uvx --from git+https://github.com/Namdevv/claude-mouse-mcp.git claude-mouse-mcp
```

> Requires: the `claude` CLI on your PATH. `uv` is installed automatically by the script if missing.

<details>
<summary>🛠️ Legacy — clone the repo then run <code>install.ps1</code> (dev / editable mode)</summary>

Clone the repo and run the install script from the project directory:

```powershell
git clone https://github.com/Namdevv/claude-mouse-mcp.git
cd claude-mouse-mcp
powershell -ExecutionPolicy Bypass -File install.ps1
```

`install.ps1` automatically:

1. Creates the `.venv` virtual environment (if missing)
2. Installs the package in editable mode (`pip install -e .`)
3. Registers the MCP server with Claude Code (`claude mcp add`) — the path is generated automatically, **no hardcoded personal path**
4. Grants auto-approve permissions for the tools in `.claude/settings.local.json`
5. Reminds you to restart Claude Code

> The script is **idempotent** — run it as many times as you like, it won't duplicate config.

After it finishes, **fully quit Claude Code and reopen it** to load the server + permissions. Verify with:

```powershell
claude mcp list
```

### Script options

```powershell
.\install.ps1 -NoPermission     # Install WITHOUT auto-approve (Claude still asks every time)
.\install.ps1 -Scope project    # Write config into .mcp.json in the repo (shared with the team)
.\install.ps1 -Scope local      # Apply only to this machine, this repo
.\install.ps1 -Name my-mouse    # Rename the MCP server
```

</details>

## 🔧 Manual install

<details>
<summary>Click to see the manual steps</summary>

```powershell
# 1. Create venv + install the package
py -m venv .venv
.venv\Scripts\python.exe -m pip install -e .

# 2. Register with Claude Code (replace <PROJECT_DIR> with the real path)
claude mcp add claude-mouse -- "<PROJECT_DIR>\.venv\Scripts\python.exe" -m claude_mouse_mcp.server
```

</details>

### Connect Claude Desktop

Open the config file `%APPDATA%\Claude\claude_desktop_config.json` and add the block below (adjust the path to match your machine):

```json
{
  "mcpServers": {
    "claude-mouse": {
      "command": "<PROJECT_DIR>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "claude_mouse_mcp.server"]
    }
  }
}
```

Restart Claude Desktop.

### Connect Codex CLI

Codex CLI also speaks MCP. Either register it with one command (Codex ≥ 0.20):

```powershell
codex mcp add claude-mouse -- uvx --from git+https://github.com/Namdevv/claude-mouse-mcp.git claude-mouse-mcp
```

Or add the server manually to `~/.codex/config.toml` (`%USERPROFILE%\.codex\config.toml` on Windows):

```toml
[mcp_servers.claude-mouse]
command = "uvx"
args = ["--from", "git+https://github.com/Namdevv/claude-mouse-mcp.git", "claude-mouse-mcp"]
# uvx downloads the package from GitHub on first launch — raise the startup
# timeout so Codex doesn't give up while it builds the environment.
startup_timeout_sec = 120
```

Restart Codex. Verify with `codex mcp list`.

> Want the editable/local install instead? Point `command` at your venv Python:
> `command = "C:\\path\\to\\claude-mouse-mcp\\.venv\\Scripts\\python.exe"` with
> `args = ["-m", "claude_mouse_mcp.server"]`.

## 🛠️ Tool list

| Tool | Function | Main parameters |
|------|----------|-----------------|
| `get_screen_size` | Get the screen resolution (pixels) | — |
| `get_cursor_position` | Get the current cursor position | — |
| `screenshot` | Capture the full screen or a region | `region` (optional) |
| `move_mouse` | Move the cursor to `(x, y)` | `x`, `y`, `duration` |
| `click` | Left/right/middle click, single/double | `x`, `y`, `button`, `clicks` |
| `drag` | Drag and drop from A to B | start/end coordinates |
| `scroll` | Scroll up/down at a position | `amount`, `x`, `y` |
| `type_text` | Type text | `text`, `interval` |
| `press_key` | Press a key / shortcut (e.g. `ctrl+c`, `alt+f4`) | `keys` |

## ⚠️ Safety

> [!WARNING]
> The server controls the **real** mouse/keyboard on your machine. Claude can click, type, and close windows. Only run it while you are watching.

- 🛑 **Emergency brake**: quickly fling the mouse into **any of the four screen corners** → every running action stops immediately (`pyautogui.FAILSAFE`).
- 🔒 You should **close sensitive apps** (banking, password managers) before using it.
- 🧪 With auto-approve granted, Claude acts **without asking again** — consider using `-NoPermission` if you want to confirm each step.
- ↩️ Revoke permissions: delete the `mcp__claude-mouse*` lines in `.claude/settings.local.json`.

## 🧩 Technical notes

- **DPI awareness** is enabled before `pyautogui` is imported, so `pyautogui.size()` and the screenshot use the same physical pixel coordinate system — clicks don't drift when the display is scaled.
- Screenshots are auto-scaled down to a max width of **1280px** to save tokens. Claude should call `get_screen_size` to know the real coordinates.
- The mouse moves with `easeInOutQuad` easing (~0.6s) for a natural, easy-to-follow motion.

## ❓ Troubleshooting

| Symptom | How to fix |
|---------|-----------|
| `claude mcp list` doesn't show the server | Re-run `install.ps1`, make sure `claude` is on your PATH |
| Claude still asks for permission every time | **Fully quit** Claude Code and reopen — settings only load at startup |
| Clicks land in the wrong place | Make sure you use real coordinates (multiply by the scale from the image) or call `get_screen_size` |
| `No module named claude_mouse_mcp` | Re-run `pip install -e .` inside the correct `.venv` |

## 🤝 Contributing

Pull requests and issues are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for
the dev setup and guidelines, and please follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Open an issue at
[github.com/Namdevv/claude-mouse-mcp/issues](https://github.com/Namdevv/claude-mouse-mcp/issues).

Notable changes are tracked in the [CHANGELOG](CHANGELOG.md).

## 📄 License

[MIT](LICENSE) © Nam TRAN
