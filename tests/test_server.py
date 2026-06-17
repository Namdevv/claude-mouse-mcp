"""Smoke tests for the claude-mouse MCP server.

These tests verify the server module imports cleanly and registers every
expected tool. They avoid moving the real mouse/keyboard so they are safe to
run in CI (including on headless Linux runners, where pyautogui still imports).
"""

from __future__ import annotations

import asyncio

import pytest


EXPECTED_TOOLS = {
    "get_screen_size",
    "get_cursor_position",
    "screenshot",
    "move_mouse",
    "click",
    "drag",
    "scroll",
    "type_text",
    "press_key",
}


@pytest.fixture(scope="module")
def server():
    # pyautogui may fail to import without a display (e.g. headless CI). If so,
    # skip rather than fail — the import-time behavior is environment-specific.
    try:
        from claude_mouse_mcp import server as srv
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"pyautogui unavailable in this environment: {exc}")
    return srv


def test_version_exported():
    import claude_mouse_mcp

    assert isinstance(claude_mouse_mcp.__version__, str)
    assert claude_mouse_mcp.__version__


def test_all_tools_registered(server):
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name for t in tools}
    assert EXPECTED_TOOLS <= names, f"Missing tools: {EXPECTED_TOOLS - names}"


def test_press_key_rejects_empty(server):
    with pytest.raises(ValueError):
        server.press_key("")


def test_click_rejects_bad_button(server):
    with pytest.raises(ValueError):
        server.click(button="diagonal")


def test_screenshot_region_requires_size(server):
    with pytest.raises(ValueError):
        server.screenshot(full_screen=False, left=0, top=0, width=0, height=0)
