# claude-mouse-mcp

<sub>📖 **Tiếng Việt** · [English](README_en.md)</sub>

> MCP server cho phép **Claude nhìn màn hình và điều khiển chuột/bàn phím** trên máy Windows của bạn.

<p align="left">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="MCP" src="https://img.shields.io/badge/MCP-stdio-6E40C9">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="CI" src="https://github.com/Namdevv/claude-mouse-mcp/actions/workflows/ci.yml/badge.svg">
</p>

Claude hoạt động theo vòng lặp **nhìn → quyết định → hành động → kiểm tra lại**:

```
chụp màn hình ──▶ (Claude phân tích) ──▶ move_mouse / click / type_text ──▶ chụp lại
   ▲                                                                          │
   └──────────────────────────────  lặp lại  ─────────────────────────────────┘
```

Chạy qua **stdio transport**, nên dùng được với **Claude Code (CLI)**, **Claude Desktop** và **Codex CLI**.

---

## 🎬 Demo

<video src="https://github.com/Namdevv/claude-mouse-mcp/raw/main/docs/demo.mp4" controls muted width="100%"></video>

> ▶️ Nếu trình phát phía trên không hiện, **[bấm vào đây để xem video demo](https://github.com/Namdevv/claude-mouse-mcp/raw/main/docs/demo.mp4)**.

---

## ✨ Tính năng

- 👁️ **Nhìn màn hình** — chụp toàn màn hình hoặc một vùng và gửi thẳng ảnh cho Claude.
- 🖱️ **Điều khiển chuột** — di chuyển, click (trái/phải/giữa, đơn/đôi), kéo-thả, cuộn.
- ⌨️ **Điều khiển bàn phím** — gõ chữ, bấm phím và phím tắt (`ctrl+c`, `alt+f4`, ...).
- 🎯 **Chuẩn DPI** — toạ độ click khớp pixel thật kể cả khi màn hình scale 125% / 150%.
- 🪙 **Tiết kiệm token** — ảnh tự động thu nhỏ về chiều rộng tối đa 1280px.
- 🛑 **Phanh khẩn cấp** — hất chuột vào góc màn hình để dừng mọi thao tác ngay lập tức.

## 💬 Một số câu lệnh mẫu

Sau khi kết nối server, bạn chỉ cần nói chuyện với Claude bằng ngôn ngữ tự nhiên —
nó sẽ tự chụp màn hình, tính toạ độ rồi thao tác. Thử vài câu như:

- _"Chụp màn hình và cho tôi biết trên màn hình đang có gì."_
- _"Mở menu Start, tìm **Notepad** rồi mở nó lên."_
- _"Trong cửa sổ đang mở, gõ 'Hello from Claude' rồi lưu thành notes.txt trên Desktop."_
- _"Tìm icon Chrome ở thanh taskbar, click vào rồi vào github.com."_
- _"Cuộn trang xuống cho tới khi thấy mục **Pricing**."_
- _"Bôi đen toàn bộ text trong ô này (ctrl+a), copy rồi cho tôi biết nội dung."_
- _"Đóng cửa sổ đang mở bằng alt+f4."_
- _"Kéo file bên trái thả vào thư mục bên phải."_

> 💡 Mẹo: bảo Claude **chụp màn hình kiểm tra lại sau mỗi bước** để kết quả ổn định
> nhất — đó chính là vòng lặp nhìn → hành động → kiểm tra mà tool được xây dựng quanh nó.

## 📋 Yêu cầu

| Thành phần | Phiên bản |
|-----------|---------|
| Hệ điều hành | Windows 10 / 11 |
| Python | 3.10 trở lên |
| Client | [Claude Code (CLI)](https://docs.claude.com/en/docs/claude-code), Claude Desktop, hoặc Codex CLI |

## 🚀 Cài nhanh (KHÔNG cần clone)

Chỉ một dòng lệnh trong PowerShell — script sẽ tự cài [`uv`](https://docs.astral.sh/uv/) (nếu thiếu), đăng ký MCP server qua `uvx` và cấp quyền auto-approve:

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Namdevv/claude-mouse-mcp/main/install-remote.ps1 | iex"
```

`uvx` **tải package từ GitHub** về một môi trường cache độc lập — không cần `git clone`, không cần tạo `.venv` thủ công. Lần đầu Claude khởi động server sẽ hơi chậm trong lúc uvx tải package về.

Kiểm tra claude bằng lệnh

```powershell
/mcp list
```
-> Nếu connect thì done, Nếu chưa chọn tool bấm reconnect -> Done

Muốn tuỳ chỉnh (đổi tên, scope, hoặc ghim phiên bản), tải script về rồi chạy:

```powershell
irm https://raw.githubusercontent.com/Namdevv/claude-mouse-mcp/main/install-remote.ps1 -OutFile install-remote.ps1
.\install-remote.ps1 -Scope local -Name my-mouse -Ref v0.1.0
```

Hoặc đăng ký trực tiếp bằng một lệnh (không qua script, tự cấp quyền sau):

```powershell
claude mcp add claude-mouse -- uvx --from git+https://github.com/Namdevv/claude-mouse-mcp.git claude-mouse-mcp
```

> Yêu cầu: có `claude` CLI trên PATH. `uv` được script tự cài nếu thiếu.

<details>
<summary>🛠️ Cách cũ — clone repo rồi chạy <code>install.ps1</code> (chế độ dev / editable)</summary>

Clone repo rồi chạy script cài đặt từ thư mục dự án:

```powershell
git clone https://github.com/Namdevv/claude-mouse-mcp.git
cd claude-mouse-mcp
powershell -ExecutionPolicy Bypass -File install.ps1
```

`install.ps1` tự động:

1. Tạo môi trường ảo `.venv` (nếu chưa có)
2. Cài package ở chế độ editable (`pip install -e .`)
3. Đăng ký MCP server với Claude Code (`claude mcp add`) — đường dẫn được sinh tự động, **không hardcode path cá nhân**
4. Cấp quyền auto-approve cho các tool trong `.claude/settings.local.json`
5. Nhắc bạn khởi động lại Claude Code

> Script **idempotent** — chạy bao nhiêu lần cũng được, không nhân đôi config.

Sau khi chạy xong, **thoát hẳn Claude Code rồi mở lại** để nạp server + quyền. Kiểm tra bằng:

```powershell
claude mcp list
```

### Tuỳ chọn của script

```powershell
.\install.ps1 -NoPermission     # Cài KHÔNG kèm auto-approve (Claude vẫn hỏi mỗi lần)
.\install.ps1 -Scope project    # Ghi config vào .mcp.json trong repo (chia sẻ cho cả team)
.\install.ps1 -Scope local      # Chỉ áp dụng cho máy này, repo này
.\install.ps1 -Name my-mouse    # Đổi tên MCP server
```

</details>

## 🔧 Cài thủ công

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

Mở file config `%APPDATA%\Claude\claude_desktop_config.json` và thêm khối bên dưới (sửa đường dẫn cho khớp máy bạn):

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

### Kết nối Codex CLI

Codex CLI cũng nói được MCP. Hoặc đăng ký bằng một lệnh (Codex ≥ 0.20):

```powershell
codex mcp add claude-mouse -- uvx --from git+https://github.com/Namdevv/claude-mouse-mcp.git claude-mouse-mcp
```

Hoặc thêm server thủ công vào `~/.codex/config.toml` (`%USERPROFILE%\.codex\config.toml` trên Windows):

```toml
[mcp_servers.claude-mouse]
command = "uvx"
args = ["--from", "git+https://github.com/Namdevv/claude-mouse-mcp.git", "claude-mouse-mcp"]
# uvx tải package từ GitHub ở lần chạy đầu tiên — tăng startup timeout để Codex
# không bỏ cuộc trong lúc nó dựng môi trường.
startup_timeout_sec = 120
```

Khởi động lại Codex. Kiểm tra bằng `codex mcp list`.

> Muốn cài kiểu editable/local? Trỏ `command` vào Python trong venv:
> `command = "C:\\path\\to\\claude-mouse-mcp\\.venv\\Scripts\\python.exe"` với
> `args = ["-m", "claude_mouse_mcp.server"]`.

## 🛠️ Danh sách tool

| Tool | Chức năng | Tham số chính |
|------|----------|-----------------|
| `get_screen_size` | Lấy độ phân giải màn hình (pixel) | — |
| `get_cursor_position` | Lấy vị trí con trỏ hiện tại | — |
| `screenshot` | Chụp toàn màn hình hoặc một vùng | `region` (tuỳ chọn) |
| `move_mouse` | Di con trỏ tới `(x, y)` | `x`, `y`, `duration` |
| `click` | Click trái/phải/giữa, đơn/đôi | `x`, `y`, `button`, `clicks` |
| `drag` | Kéo-thả từ A tới B | toạ độ đầu/cuối |
| `scroll` | Cuộn lên/xuống tại một vị trí | `amount`, `x`, `y` |
| `type_text` | Gõ chữ | `text`, `interval` |
| `press_key` | Bấm phím / phím tắt (vd `ctrl+c`, `alt+f4`) | `keys` |

## ⚠️ An toàn

> [!WARNING]
> Server điều khiển chuột/bàn phím **thật** trên máy bạn. Claude có thể click, gõ và đóng cửa sổ. Chỉ chạy khi bạn đang ngồi xem.

- 🛑 **Phanh khẩn cấp**: hất nhanh chuột vào **bất kỳ góc nào trong 4 góc màn hình** → mọi thao tác đang chạy dừng ngay (`pyautogui.FAILSAFE`).
- 🔒 Nên **đóng các app nhạy cảm** (ngân hàng, password manager) trước khi dùng.
- 🧪 Khi đã cấp auto-approve, Claude hành động **không hỏi lại** — cân nhắc dùng `-NoPermission` nếu muốn xác nhận từng bước.
- ↩️ Thu hồi quyền: xoá các dòng `mcp__claude-mouse*` trong `.claude/settings.local.json`.

## 🧩 Ghi chú kỹ thuật

- **DPI awareness** được bật trước khi import `pyautogui`, nên `pyautogui.size()` và ảnh chụp dùng cùng một hệ toạ độ pixel vật lý — click không bị lệch khi màn hình scale.
- Ảnh chụp tự động thu nhỏ về chiều rộng tối đa **1280px** để tiết kiệm token. Claude nên gọi `get_screen_size` để biết toạ độ thật.
- Chuột di chuyển với hiệu ứng `easeInOutQuad` (~0.6s) cho chuyển động tự nhiên, dễ theo dõi.

## ❓ Khắc phục sự cố

| Triệu chứng | Cách xử lý |
|---------|-----------|
| `claude mcp list` không thấy server | Chạy lại `install.ps1`, đảm bảo `claude` có trên PATH |
| Claude vẫn hỏi quyền mỗi lần | **Thoát hẳn** Claude Code rồi mở lại — settings chỉ nạp lúc khởi động |
| Click sai chỗ | Đảm bảo dùng toạ độ thật (nhân với scale lấy từ ảnh) hoặc gọi `get_screen_size` |
| `No module named claude_mouse_mcp` | Chạy lại `pip install -e .` trong đúng `.venv` |

## 🤝 Đóng góp

Pull request và issue đều được hoan nghênh! Xem [CONTRIBUTING.md](CONTRIBUTING.md) để biết
cách dựng môi trường dev và quy ước, và vui lòng tuân theo
[Code of Conduct](CODE_OF_CONDUCT.md). Mở issue tại
[github.com/Namdevv/claude-mouse-mcp/issues](https://github.com/Namdevv/claude-mouse-mcp/issues).

Các thay đổi đáng chú ý được ghi trong [CHANGELOG](CHANGELOG.md).

## 📄 Giấy phép

[MIT](LICENSE) © Nam TRAN
