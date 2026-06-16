"""
Claude Mouse MCP server.

Cung cấp cho Claude khả năng:
  - Nhìn màn hình  (screenshot, get_screen_size, get_cursor_position)
  - Điều khiển chuột (move_mouse, click, drag, scroll)
  - Điều khiển bàn phím (type_text, press_key)

Chạy qua stdio transport => dùng được cho cả Claude Desktop lẫn Claude Code.
"""

from __future__ import annotations

import io
import sys
import time

# --- Bật DPI awareness TRƯỚC khi import pyautogui ---------------------------
# Trên Windows nếu scale màn hình != 100% (vd 125%, 150%) thì toạ độ logic và
# pixel thật bị lệch -> Claude click sai chỗ. Bật DPI-aware để pyautogui.size()
# và ảnh chụp dùng CÙNG hệ toạ độ pixel vật lý.
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

# An toàn: di chuột vào 1 trong 4 góc màn hình sẽ raise FailSafeException,
# dừng ngay mọi hành động đang chạy. Đây là "phanh tay" thủ công.
pyautogui.FAILSAFE = True
# Delay nhỏ sau mỗi lệnh để UI kịp phản hồi.
pyautogui.PAUSE = 0.05

mcp = FastMCP("claude-mouse")

# Giới hạn bề rộng ảnh gửi cho Claude để tiết kiệm token (ảnh full-HD rất nặng).
MAX_SCREENSHOT_WIDTH = 1280

# Thời gian (giây) chuột lướt tới vị trí đích -> đủ chậm để nhìn thấy chuyển động.
MOVE_DURATION = 0.6
# Hàm easing: tăng/giảm tốc tự nhiên giống tay người, dễ nhìn hơn tuyến tính.
TWEEN = pyautogui.easeInOutQuad


def _grab_png(region: tuple[int, int, int, int] | None = None,
              max_width: int = MAX_SCREENSHOT_WIDTH) -> tuple[bytes, int, int, float]:
    """Chụp màn hình -> (PNG bytes, rộng_ảnh, cao_ảnh, scale).

    scale = pixel_màn_hình / pixel_ảnh. Nhân toạ độ-trên-ảnh với scale để ra
    toạ độ màn hình thật dùng cho click.
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
#  NHÌN MÀN HÌNH
# --------------------------------------------------------------------------
@mcp.tool()
def get_screen_size() -> str:
    """Trả về kích thước màn hình (chiều rộng x chiều cao, đơn vị pixel).

    Gọi tool này trước khi tính toạ độ click để biết phạm vi hợp lệ.
    """
    w, h = pyautogui.size()
    return f"Kích thước màn hình: {w} x {h} pixel"


@mcp.tool()
def get_cursor_position() -> str:
    """Trả về toạ độ (x, y) hiện tại của con trỏ chuột."""
    x, y = pyautogui.position()
    return f"Vị trí chuột hiện tại: x={x}, y={y}"


@mcp.tool()
def screenshot(
    full_screen: bool = True,
    left: int = 0,
    top: int = 0,
    width: int = 0,
    height: int = 0,
) -> list:
    """Chụp ảnh màn hình để Claude nhìn được nội dung đang hiển thị.

    - full_screen=True: chụp toàn màn hình (mặc định).
    - full_screen=False: chụp 1 vùng chữ nhật xác định bởi left/top/width/height.

    QUAN TRỌNG về toạ độ: ảnh trả về có thể đã bị THU NHỎ để tiết kiệm token.
    Kèm theo ảnh là dòng chú thích cho biết kích thước ảnh, kích thước màn hình
    thật và hệ số 'scale'. Toạ độ click PHẢI tính theo PIXEL MÀN HÌNH THẬT:
        x_thật = x_trên_ảnh * scale   (cộng thêm 'left'/'top' nếu chụp 1 vùng)
    Dùng tool này sau mỗi hành động để xác nhận kết quả trước khi làm bước tiếp.
    """
    region = None
    ox, oy = 0, 0
    if not full_screen:
        if width <= 0 or height <= 0:
            raise ValueError("Khi full_screen=False phải cung cấp width và height > 0")
        region = (left, top, width, height)
        ox, oy = left, top
    png, img_w, img_h, scale = _grab_png(region)
    screen_w, screen_h = pyautogui.size()
    note = (
        f"[Thông tin toạ độ] Ảnh: {img_w}x{img_h}px | "
        f"Màn hình thật: {screen_w}x{screen_h}px | scale={scale:.3f}. "
        f"Đổi toạ độ: x_thật = x_ảnh*{scale:.3f} + {ox}, "
        f"y_thật = y_ảnh*{scale:.3f} + {oy}. Click theo toạ độ THẬT."
    )
    return [note, Image(data=png, format="png")]


# --------------------------------------------------------------------------
#  ĐIỀU KHIỂN CHUỘT
# --------------------------------------------------------------------------
@mcp.tool()
def move_mouse(x: int, y: int, duration: float = MOVE_DURATION) -> str:
    """Di chuyển con trỏ chuột tới toạ độ (x, y) — chuột LƯỚT mượt để nhìn thấy.

    duration = số giây để di chuyển. Đặt 0 nếu muốn nhảy tức thì (không khuyến khích).
    """
    pyautogui.moveTo(x, y, duration=duration, tween=TWEEN)
    return f"Đã di chuột tới ({x}, {y})"


@mcp.tool()
def click(
    x: int = -1,
    y: int = -1,
    button: str = "left",
    clicks: int = 1,
    duration: float = MOVE_DURATION,
) -> str:
    """Click chuột tại (x, y). Nếu không truyền toạ độ thì click tại vị trí hiện tại.

    Chuột sẽ LƯỚT mượt tới (x, y) (nhìn thấy được) rồi mới click — không nhảy "bụp".
    - button: "left" | "right" | "middle"
    - clicks: 1 = single click, 2 = double click
    - duration: số giây chuột lướt tới đích.
    """
    if button not in ("left", "right", "middle"):
        raise ValueError("button phải là 'left', 'right' hoặc 'middle'")
    if x >= 0 and y >= 0:
        # Lướt tới đích trước cho người dùng nhìn thấy, rồi click tại chỗ.
        pyautogui.moveTo(x, y, duration=duration, tween=TWEEN)
        where = f"tại ({x}, {y})"
    else:
        where = "tại vị trí hiện tại"
    pyautogui.click(clicks=clicks, button=button, interval=0.1)
    return f"Đã {clicks}-click chuột {button} {where}"


@mcp.tool()
def drag(
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
    button: str = "left",
    duration: float = 0.8,
) -> str:
    """Kéo–thả: nhấn giữ chuột tại (from_x, from_y) rồi kéo tới (to_x, to_y) và thả."""
    pyautogui.moveTo(from_x, from_y, duration=MOVE_DURATION, tween=TWEEN)
    pyautogui.dragTo(to_x, to_y, duration=duration, button=button, tween=TWEEN)
    return f"Đã kéo từ ({from_x}, {from_y}) tới ({to_x}, {to_y})"


@mcp.tool()
def scroll(amount: int, x: int = -1, y: int = -1) -> str:
    """Cuộn chuột. amount > 0 = cuộn lên, amount < 0 = cuộn xuống.

    Có thể truyền (x, y) để di chuột tới đó trước khi cuộn.
    """
    if x >= 0 and y >= 0:
        pyautogui.moveTo(x, y, duration=MOVE_DURATION, tween=TWEEN)
    pyautogui.scroll(amount)
    return f"Đã cuộn {amount} đơn vị ({'lên' if amount > 0 else 'xuống'})"


# --------------------------------------------------------------------------
#  ĐIỀU KHIỂN BÀN PHÍM
# --------------------------------------------------------------------------
@mcp.tool()
def type_text(text: str, interval: float = 0.02) -> str:
    """Gõ một đoạn văn bản như gõ bàn phím. interval = giây giữa mỗi ký tự."""
    pyautogui.write(text, interval=interval)
    return f"Đã gõ {len(text)} ký tự"


@mcp.tool()
def press_key(keys: str) -> str:
    """Nhấn phím hoặc tổ hợp phím tắt.

    - Một phím: "enter", "esc", "tab", "f5", "delete"...
    - Tổ hợp: dùng dấu "+", ví dụ "ctrl+c", "ctrl+shift+esc", "alt+f4".
    Danh sách tên phím theo quy ước pyautogui (vd: ctrl, alt, shift, win, enter).
    """
    parts = [k.strip().lower() for k in keys.split("+") if k.strip()]
    if not parts:
        raise ValueError("Chuỗi phím rỗng")
    if len(parts) == 1:
        pyautogui.press(parts[0])
    else:
        pyautogui.hotkey(*parts)
    return f"Đã nhấn: {keys}"


# --------------------------------------------------------------------------
def main() -> None:
    """Entry point: chạy server qua stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
