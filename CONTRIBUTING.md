# Contributing to claude-mouse-mcp

Thanks for your interest in improving **claude-mouse-mcp**! Pull requests and
issues are welcome.

## Development setup

This project targets **Windows 10 / 11** and **Python 3.10+**.

```powershell
# 1. Clone
git clone https://github.com/Namdevv/claude-mouse-mcp.git
cd claude-mouse-mcp

# 2. Create a virtual environment + install in editable mode with dev deps
py -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"

# 3. Run the test suite
.venv\Scripts\python.exe -m pytest -v
```

## Project layout

```
src/claude_mouse_mcp/
  __init__.py     # package metadata (__version__)
  server.py       # the MCP server + all tools
tests/            # smoke tests (no real mouse/keyboard movement)
install.ps1       # local/editable installer
install-remote.ps1  # uvx-based remote installer
```

## Making changes

1. **Open an issue first** for anything beyond a small fix, so we can agree on
   the approach.
2. Create a branch off `main`.
3. Keep the style consistent with the existing code:
   - English comments and docstrings.
   - Every MCP tool is a function decorated with `@mcp.tool()` and has a clear
     docstring — Claude reads these descriptions to decide how to call the tool.
   - Validate user input and raise `ValueError` with a helpful message.
4. Add or update a test in `tests/` when you change behavior.
5. Run `pytest` locally before pushing.

## Safety reminder

This server controls the **real** mouse and keyboard. When testing tools that
move the cursor, type, or press keys, do it deliberately and keep the failsafe
in mind: flinging the mouse into any screen corner stops every action
(`pyautogui.FAILSAFE`).

## Commit messages

Write clear, descriptive commit messages in English (imperative mood, e.g.
"Add scroll direction validation").

## Reporting bugs

Open an issue at
[github.com/Namdevv/claude-mouse-mcp/issues](https://github.com/Namdevv/claude-mouse-mcp/issues)
and include your OS version, Python version, the client (Claude Code / Desktop /
Codex), and steps to reproduce.
