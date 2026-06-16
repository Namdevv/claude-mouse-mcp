# claude-mouse-mcp

> MCP server cho phép **Claude nhìn màn hình và điều khiển chuột/bàn phím** trên máy Windows của bạn.

<p align="left">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="MCP" src="https://img.shields.io/badge/MCP-stdio-6E40C9">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

Claude làm việc theo vòng lặp **nhìn → quyết định → hành động → kiểm tra**:

```
screenshot ──▶ (Claude phân tích) ──▶ move_mouse / click / type_text ──▶ screenshot
   ▲                                                                          │
   └──────────────────────────────  lặp lại  ───────────────────────────────┘
```

Hoạt động qua **stdio transport**, dùng được cho cả **Claude Code (CLI)** lẫn **Claude Desktop**.

---

## ✨ Tính năng

- 👁️ **Nhìn màn hình** — chụp toàn màn hình hoặc một vùng, gửi ảnh trực tiếp cho Claude.
- 🖱️ **Điều khiển chuột** — di chuyển, click (trái/phải/giữa, single/double), kéo–thả, cuộn.
- ⌨️ **Điều khiển bàn phím** — gõ văn bản, nhấn phím và tổ hợp phím (`ctrl+c`, `alt+f4`, ...).
- 🎯 **DPI-aware** — toạ độ click khớp pixel thật kể cả khi màn hình scale 125% / 150%.
- 🪙 **Tiết kiệm token** — ảnh tự thu nhỏ về tối đa 1280px chiều rộng.
- 🛑 **Phanh tay khẩn cấp** — hất chuột vào góc màn hình để dừng mọi hành động ngay lập tức.

## 📋 Yêu cầu

| Thành phần | Phiên bản |
|------------|-----------|
| Hệ điều hành | Windows 10 / 11 |
| Python | 3.10 trở lên |
| Claude | [Claude Code (CLI)](https://docs.claude.com/en/docs/claude-code) hoặc Claude Desktop |

## 🚀 Cài đặt nhanh (1 lệnh)

Clone repo rồi chạy script cài đặt từ thư mục dự án:

```powershell
git clone https://github.com/Namdevv/claude-mouse-mcp.git
cd claude-mouse-mcp
powershell -ExecutionPolicy Bypass -File install.ps1
```

Script `install.ps1` tự động:

1. Tạo virtual environment `.venv` (nếu chưa có)
2. Cài package ở chế độ editable (`pip install -e .`)
3. Đăng ký MCP server vào Claude Code (`claude mcp add`) — đường dẫn được sinh tự động, **không hardcode path cá nhân**
4. Cấp quyền auto-approve cho các tool vào `.claude/settings.local.json`
5. Nhắc khởi động lại Claude Code

> Script **idempotent** — chạy lại bao nhiêu lần cũng được, không nhân đôi cấu hình.

Sau khi chạy xong, **thoát hẳn Claude Code rồi mở lại** để nạp server + quyền. Kiểm tra:

```powershell
claude mcp list
```

### Tùy chọn script

```powershell
.\install.ps1 -NoPermission     # Cài nhưng KHÔNG auto-approve (Claude vẫn hỏi mỗi lần)
.\install.ps1 -Scope project    # Ghi cấu hình vào .mcp.json trong repo (chia sẻ cho team)
.\install.ps1 -Scope local      # Chỉ áp dụng cho máy này, repo này
.\install.ps1 -Name my-mouse    # Đổi tên MCP server
```

## 🔧 Cài đặt thủ công

<details>
<summary>Bấm để xem các bước thủ công</summary>

```powershell
# 1. Tạo venv + cài package
py -m venv .venv
.venv\Scripts\python.exe -m pip install -e .

# 2. Đăng ký với Claude Code (thay <PROJECT_DIR> bằng đường dẫn thật)
claude mcp add claude-mouse -- "<PROJECT_DIR>\.venv\Scripts\python.exe" -m claude_mouse_mcp.server
```

</details>

### Kết nối Claude Desktop

Mở file cấu hình `%APPDATA%\Claude\claude_desktop_config.json` và thêm khối sau (sửa đường dẫn cho khớp máy bạn):

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

Khởi động lại Claude Desktop.

## 🛠️ Danh sách Tools

| Tool | Chức năng | Tham số chính |
|------|-----------|---------------|
| `get_screen_size` | Lấy độ phân giải màn hình (pixel) | — |
| `get_cursor_position` | Lấy vị trí chuột hiện tại | — |
| `screenshot` | Chụp toàn màn hình hoặc một vùng | `region` (tuỳ chọn) |
| `move_mouse` | Di chuột tới `(x, y)` | `x`, `y`, `duration` |
| `click` | Click trái/phải/giữa, single/double | `x`, `y`, `button`, `clicks` |
| `drag` | Kéo–thả từ A tới B | toạ độ đầu/cuối |
| `scroll` | Cuộn lên/xuống tại vị trí | `amount`, `x`, `y` |
| `type_text` | Gõ văn bản | `text`, `interval` |
| `press_key` | Nhấn phím / tổ hợp (vd `ctrl+c`, `alt+f4`) | `keys` |

## ⚠️ An toàn

> [!WARNING]
> Server điều khiển chuột/bàn phím **thật** trên máy bạn. Claude có thể click, gõ, đóng cửa sổ. Chỉ chạy khi bạn đang ngồi quan sát.

- 🛑 **Phanh tay khẩn cấp**: hất nhanh chuột vào **một trong bốn góc màn hình** → mọi hành động đang chạy dừng ngay (`pyautogui.FAILSAFE`).
- 🔒 Nên **đóng các ứng dụng nhạy cảm** (ngân hàng, trình quản lý mật khẩu) trước khi dùng.
- 🧪 Khi cấp quyền auto-approve, Claude thao tác **không hỏi lại** — cân nhắc dùng `-NoPermission` nếu muốn xác nhận từng bước.
- ↩️ Thu hồi quyền: xóa các dòng `mcp__claude-mouse*` trong `.claude/settings.local.json`.

## 🧩 Ghi chú kỹ thuật

- **DPI awareness** được bật trước khi import `pyautogui`, nên `pyautogui.size()` và ảnh chụp dùng cùng hệ toạ độ pixel vật lý — click không bị lệch khi scale màn hình.
- Ảnh chụp tự thu nhỏ về tối đa **1280px** chiều rộng để tiết kiệm token. Claude nên gọi `get_screen_size` để biết toạ độ thật.
- Chuột di chuyển với easing `easeInOutQuad` (~0.6s) để chuyển động tự nhiên, dễ theo dõi.

## ❓ Khắc phục sự cố

| Triệu chứng | Cách xử lý |
|-------------|-----------|
| `claude mcp list` không thấy server | Chạy lại `install.ps1`, kiểm tra `claude` có trong PATH |
| Claude vẫn hỏi quyền mỗi lần | **Thoát hẳn** Claude Code rồi mở lại — settings chỉ nạp lúc khởi động |
| Click sai vị trí | Đảm bảo dùng toạ độ thật (nhân scale từ ảnh) hoặc gọi `get_screen_size` |
| `No module named claude_mouse_mcp` | Chạy lại bước `pip install -e .` trong đúng `.venv` |

## 🤝 Đóng góp

Pull request và issue đều được hoan nghênh. Mở issue tại
[github.com/Namdevv/claude-mouse-mcp/issues](https://github.com/Namdevv/claude-mouse-mcp/issues).

## 📄 License

[MIT](LICENSE) © Nam TRAN
