"""
Claude Mouse MCP server.

Gives Claude the ability to:
  - See the screen      (screenshot, get_screen_size, get_cursor_position)
  - Control the mouse   (move_mouse, click, drag, scroll)
  - Control the keyboard (type_text, press_key)

Runs over the stdio transport => works with both Claude Desktop and Claude Code.
"""

from __future__ import annotations

import io
import sys
import time

# --- Enable DPI awareness BEFORE importing pyautogui -----------------------
# On Windows, if the display scale != 100% (e.g. 125%, 150%) the logical and
# physical pixel coordinates diverge -> Claude clicks the wrong spot. Enabling
# DPI awareness makes pyautogui.size() and the screenshot use the SAME physical
# pixel coordinate system.
if sys.platform == "win32":
    try:
        import ctypes

        # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import pyautogui
from mcp.server.fastmcp import FastMCP, Image

# Safety: moving the mouse into one of the 4 screen corners raises a
# FailSafeException, immediately stopping any running action. This is the manual
# "emergency brake".
pyautogui.FAILSAFE = True
# Small delay after each command so the UI has time to respond.
pyautogui.PAUSE = 0.05

mcp = FastMCP("claude-mouse")

# Cap the width of images sent to Claude to save tokens (full-HD images are heavy).
MAX_SCREENSHOT_WIDTH = 1280

# Time (seconds) for the cursor to glide to the target -> slow enough to see the motion.
MOVE_DURATION = 0.6
# Easing function: natural ease-in/ease-out like a human hand, easier to follow than linear.
TWEEN = pyautogui.easeInOutQuad


def _grab_png(region: tuple[int, int, int, int] | None = None,
              max_width: int = MAX_SCREENSHOT_WIDTH) -> tuple[bytes, int, int, float]:
    """Capture the screen -> (PNG bytes, image_width, image_height, scale).

    scale = screen_pixels / image_pixels. Multiply an in-image coordinate by
    scale to get the real screen coordinate used for clicking.
    """
    img = pyautogui.screenshot(region=region)
    orig_w = img.width
    scale = 1.0
    if max_width and img.width > max_width:
        scale = img.width / max_width
        img = img.resize((max_width, round(img.height / scale)))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), img.width, img.height, scale


# --------------------------------------------------------------------------
#  SEE THE SCREEN
# --------------------------------------------------------------------------
@mcp.tool()
def get_screen_size() -> str:
    """Return the screen size (width x height, in pixels).

    Call this before computing click coordinates to know the valid range.
    """
    w, h = pyautogui.size()
    return f"Screen size: {w} x {h} pixels"


@mcp.tool()
def get_cursor_position() -> str:
    """Return the current (x, y) coordinates of the mouse cursor."""
    x, y = pyautogui.position()
    return f"Current cursor position: x={x}, y={y}"


@mcp.tool()
def screenshot(
    full_screen: bool = True,
    left: int = 0,
    top: int = 0,
    width: int = 0,
    height: int = 0,
) -> list:
    """Capture a screenshot so Claude can see what is currently displayed.

    - full_screen=True: capture the entire screen (default).
    - full_screen=False: capture a rectangular region defined by left/top/width/height.

    IMPORTANT about coordinates: the returned image may have been SCALED DOWN to
    save tokens. The image comes with a note describing the image size, the real
    screen size and the 'scale' factor. Click coordinates MUST be computed in
    REAL SCREEN PIXELS:
        real_x = image_x * scale   (plus 'left'/'top' when capturing a region)
    Use this tool after each action to confirm the result before the next step.
    """
    region = None
    ox, oy = 0, 0
    if not full_screen:
        if width <= 0 or height <= 0:
            raise ValueError("When full_screen=False you must provide width and height > 0")
        region = (left, top, width, height)
        ox, oy = left, top
    png, img_w, img_h, scale = _grab_png(region)
    screen_w, screen_h = pyautogui.size()
    note = (
        f"[Coordinate info] Image: {img_w}x{img_h}px | "
        f"Real screen: {screen_w}x{screen_h}px | scale={scale:.3f}. "
        f"Convert coordinates: real_x = image_x*{scale:.3f} + {ox}, "
        f"real_y = image_y*{scale:.3f} + {oy}. Click using REAL coordinates."
    )
    return [note, Image(data=png, format="png")]


# --------------------------------------------------------------------------
#  MOUSE CONTROL
# --------------------------------------------------------------------------
@mcp.tool()
def move_mouse(x: int, y: int, duration: float = MOVE_DURATION) -> str:
    """Move the cursor to (x, y) — the mouse GLIDES smoothly so the motion is visible.

    duration = number of seconds for the movement. Set to 0 for an instant jump (not recommended).
    """
    pyautogui.moveTo(x, y, duration=duration, tween=TWEEN)
    return f"Moved cursor to ({x}, {y})"


@mcp.tool()
def click(
    x: int = -1,
    y: int = -1,
    button: str = "left",
    clicks: int = 1,
    duration: float = MOVE_DURATION,
) -> str:
    """Click the mouse at (x, y). If no coordinates are given, click at the current position.

    The mouse GLIDES smoothly to (x, y) (visibly) before clicking — no instant jump.
    - button: "left" | "right" | "middle"
    - clicks: 1 = single click, 2 = double click
    - duration: number of seconds for the glide to the target.
    """
    if button not in ("left", "right", "middle"):
        raise ValueError("button must be 'left', 'right' or 'middle'")
    if x >= 0 and y >= 0:
        # Glide to the target first so the user can see it, then click in place.
        pyautogui.moveTo(x, y, duration=duration, tween=TWEEN)
        where = f"at ({x}, {y})"
    else:
        where = "at the current position"
    pyautogui.click(clicks=clicks, button=button, interval=0.1)
    return f"Performed {clicks}-click with {button} button {where}"


@mcp.tool()
def drag(
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
    button: str = "left",
    duration: float = 0.8,
) -> str:
    """Drag and drop: press and hold the mouse at (from_x, from_y), drag to (to_x, to_y) and release."""
    pyautogui.moveTo(from_x, from_y, duration=MOVE_DURATION, tween=TWEEN)
    pyautogui.dragTo(to_x, to_y, duration=duration, button=button, tween=TWEEN)
    return f"Dragged from ({from_x}, {from_y}) to ({to_x}, {to_y})"


@mcp.tool()
def scroll(amount: int, x: int = -1, y: int = -1) -> str:
    """Scroll the mouse wheel. amount > 0 = scroll up, amount < 0 = scroll down.

    You may pass (x, y) to move the mouse there before scrolling.
    """
    if x >= 0 and y >= 0:
        pyautogui.moveTo(x, y, duration=MOVE_DURATION, tween=TWEEN)
    pyautogui.scroll(amount)
    return f"Scrolled {amount} units ({'up' if amount > 0 else 'down'})"


# --------------------------------------------------------------------------
#  KEYBOARD CONTROL
# --------------------------------------------------------------------------
@mcp.tool()
def type_text(text: str, interval: float = 0.02) -> str:
    """Type a piece of text as if typing on the keyboard. interval = seconds between each character."""
    pyautogui.write(text, interval=interval)
    return f"Typed {len(text)} characters"


@mcp.tool()
def press_key(keys: str) -> str:
    """Press a key or a keyboard shortcut combination.

    - Single key: "enter", "esc", "tab", "f5", "delete"...
    - Combination: use "+", e.g. "ctrl+c", "ctrl+shift+esc", "alt+f4".
    Key names follow the pyautogui convention (e.g. ctrl, alt, shift, win, enter).
    """
    parts = [k.strip().lower() for k in keys.split("+") if k.strip()]
    if not parts:
        raise ValueError("Empty key string")
    if len(parts) == 1:
        pyautogui.press(parts[0])
    else:
        pyautogui.hotkey(*parts)
    return f"Pressed: {keys}"


# --------------------------------------------------------------------------
def main() -> None:
    """Entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
