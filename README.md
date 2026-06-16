# claude-mouse-mcp

MCP server cho phép **Claude nhìn màn hình và điều khiển chuột/bàn phím** trên máy Windows của bạn.

Claude làm việc theo vòng lặp: `screenshot` (nhìn) → quyết định → `move_mouse`/`click`/`type_text` (hành động) → `screenshot` (kiểm tra kết quả).

## Tools

| Tool | Chức năng |
|------|-----------|
| `get_screen_size` | Lấy độ phân giải màn hình (pixel) |
| `get_cursor_position` | Lấy vị trí chuột hiện tại |
| `screenshot` | Chụp toàn màn hình hoặc 1 vùng, gửi ảnh cho Claude |
| `move_mouse` | Di chuột tới (x, y) |
| `click` | Click trái/phải/giữa, single/double |
| `drag` | Kéo–thả từ A tới B |
| `scroll` | Cuộn lên/xuống |
| `type_text` | Gõ văn bản |
| `press_key` | Nhấn phím / tổ hợp phím (vd `ctrl+c`, `alt+f4`) |

## Cài đặt

```powershell
cd C:\Users\Admin\Documents\Workspace\claude-mouse-mcp
py -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

## Kết nối với Claude

### Claude Code (CLI)
Đã có sẵn file `.mcp.json` ở thư mục dự án. Mở Claude Code trong thư mục này và xác nhận khi được hỏi có tin tưởng MCP server không. Kiểm tra bằng:

```powershell
claude mcp list
```

Hoặc đăng ký thủ công ở phạm vi user:

```powershell
claude mcp add claude-mouse -- "C:\Users\Admin\Documents\Workspace\claude-mouse-mcp\.venv\Scripts\python.exe" -m claude_mouse_mcp.server
```

### Claude Desktop
Chép nội dung `claude_desktop_config.example.json` vào file cấu hình:

```
%APPDATA%\Claude\claude_desktop_config.json
```

Rồi khởi động lại Claude Desktop.

## An toàn ⚠️

- Server điều khiển chuột/bàn phím **thật** trên máy bạn. Chỉ chạy khi bạn đang quan sát.
- **Phanh tay khẩn cấp**: hất nhanh chuột vào **góc trên–trái màn hình** → mọi hành động đang chạy dừng ngay (pyautogui FAILSAFE).
- Nên đóng các ứng dụng nhạy cảm (ngân hàng, mật khẩu) trước khi dùng.

## Ghi chú kỹ thuật

- Đã bật **DPI awareness** trên Windows nên toạ độ click khớp với pixel thật kể cả khi màn hình scale 125%/150%.
- Ảnh chụp tự thu nhỏ về tối đa 1280px chiều rộng để tiết kiệm token; Claude nên gọi `get_screen_size` để biết toạ độ thật.
