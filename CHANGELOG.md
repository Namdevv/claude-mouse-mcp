# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project metadata in `pyproject.toml` (authors, URLs, keywords, classifiers).
- Smoke test suite under `tests/` and a GitHub Actions CI workflow.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and issue/PR templates.

### Changed
- `claude_desktop_config.example.json` now uses a placeholder path instead of a
  personal one.

## [0.1.0] - 2026-06-17

### Added
- Initial release.
- MCP server over stdio exposing nine tools: `get_screen_size`,
  `get_cursor_position`, `screenshot`, `move_mouse`, `click`, `drag`, `scroll`,
  `type_text`, `press_key`.
- DPI awareness so clicks match real pixels on scaled displays.
- Screenshots auto-scaled to a max width of 1280px to save tokens.
- `pyautogui.FAILSAFE` emergency brake (mouse to a screen corner).
- `install.ps1` (local/editable) and `install-remote.ps1` (uvx from GitHub)
  installers.

[Unreleased]: https://github.com/Namdevv/claude-mouse-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Namdevv/claude-mouse-mcp/releases/tag/v0.1.0
