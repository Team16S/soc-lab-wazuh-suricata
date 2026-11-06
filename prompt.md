# 🛡️ GIAO THỨC KIỂM ĐỊNH QA & CHỐNG ẢO GIÁC AI (STRICT QA PROTOCOL)

> **Mục đích:** File này được thiết kế để Agent tự phản biện, kiểm tra chéo và rà soát lại toàn bộ kết quả sau mỗi lần giải quyết Issue/Task trong dự án **SOC Lab (Wazuh + Suricata)**.  
> **Cơ chế áp dụng:** Agent chỉ cập nhật file này sau mỗi lần hoàn thành task issue. Phải đọc lại trước và sau khi làm task để tránh lặp lại sai lầm, tuyệt đối không được vượt tầm kiểm soát của người dùng.

---

## 🔍 PHẦN 1: BẢN TỰ PHẢN BIỆN CỦA CHUYÊN GIA QA KHẮT KHE (AUDIT TRAIL)

Sau khi đối chiếu nghiêm ngặt với thực tế máy ảo VMware của 3 thành viên, chuyên gia QA chỉ ra **các điểm sai lệch, thiếu logic và mơ hồ nghiêm trọng** cần được khắc phục triệt để:

### ❌ Điểm sai 1: Ảo giác về công cụ cài sẵn (Khuyên dùng `nano` khi chưa có mạng - TV1)
* **Lỗi của AI:** Đề xuất "Dùng `sudo nano ...` để trực quan, không lo kẹt lệnh".
* **Lỗ hổng chết người:** Amazon Linux 2023 (nền tảng của Wazuh 4.8 OVA) là bản minimal, **mặc định KHÔNG HỀ cài sẵn `nano`**, mà chỉ có **`vi`**! 
* **Hậu quả thực tế:** Người dùng đang cấu hình IP ban đầu (chưa có mạng) nên **hoàn toàn không thể chạy `sudo dnf install -y nano`**. Máy ảo sẽ báo lỗi `bash: nano: command not found`.
* **Bản sửa đổi chuẩn xác:** Công cụ duy nhất có sẵn 100% là **`vi`**. Hướng dẫn chi tiết từng phím: nhấn `i` để nhập, nhấn `Esc` rồi gõ `:wq` để lưu.

---

### ❌ Điểm sai 2: Không cảnh báo rác cấu hình sau khi kẹt Heredoc (TV1)
* **Lỗi của AI:** Khi thấy người dùng bị kẹt ở dấu `>` do gõ nhầm `.bash...` và `wq`, AI chỉ bảo bấm `Ctrl + C` mà không yêu cầu kiểm tra/xóa file rác.
* **Hậu quả thực tế:** File `/etc/systemd/network/10-static-eth0.network` bị dính cú pháp rác, khiến `systemd-networkd` báo lỗi cú pháp và từ chối cấp IP tĩnh.
* **Bản sửa đổi chuẩn xác:** Bắt buộc dọn sạch: `sudo rm -f /etc/systemd/network/10-static-eth0.network` trước khi tạo file mới.

---

### ❌ Điểm sai 3: Lệnh `netfilter-persistent save` báo lỗi `command not found` (TV2 - Sensor)
* **Lỗi của AI:** Viết lệnh `sudo netfilter-persistent save` mà không hướng dẫn cài đặt gói.
* **Sự thật kỹ thuật:** Ubuntu Server 22.04 LTS **mặc định KHÔNG cài sẵn `iptables-persistent` hay `netfilter-persistent`**!
* **Hậu quả thực tế:** Lệnh báo lỗi `command not found`. Khi máy ảo Sensor reboot, toàn bộ rule `iptables NAT MASQUERADE` biến mất $\rightarrow$ Target (`10.0.0.10`) mất toàn bộ Internet, không thể `apt update`, không cài được Nginx!
* **Bản sửa đổi chuẩn xác:** Phải cài đặt trước: `sudo apt install -y iptables-persistent netfilter-persistent`.

---

### ❌ Điểm sai 4: Wazuh Agent bị `Permission Denied` khi đọc `eve.json` (TV2 - Sensor)
* **Lỗi của AI:** Chỉ hướng dẫn `sudo chmod 644 /var/log/suricata/eve.json`.
* **Sự thật kỹ thuật:** Thư mục cha `/var/log/suricata/` có quyền mặc định `750` (`drwxr-x---`) thuộc sở hữu của `suricata:suricata`. User `wazuh` không thể đi qua thư mục này để đọc log khi xoay vòng file (logrotate).
* **Hậu quả thực tế:** Wazuh Agent báo lỗi: `ossec-logcollector: ERROR: Could not open file '/var/log/suricata/eve.json' permission denied`!
* **Bản sửa đổi chuẩn xác:** Thêm user `wazuh` vào group `suricata` (`sudo usermod -aG suricata wazuh`) và cấp quyền thư mục `sudo chmod 755 /var/log/suricata`.

---

### ❌ Điểm sai 5: Suricata KHÔNG hề nạp file `local.rules` (TV2 - Sensor)
* **Lỗi của AI:** Hướng dẫn viết rules vào `/var/lib/suricata/rules/local.rules` nhưng không khai báo trong `/etc/suricata/suricata.yaml`.
* **Sự thật kỹ thuật:** Mặc định Suricata chỉ đọc `suricata.rules`. Nếu không thêm `- local.rules` vào mục `rule-files:`, Suricata sẽ bỏ qua 100% custom rules!
* **Hậu quả thực tế:** Kali quét Ping, Nmap, SSH thì Suricata hoàn toàn im lặng, không sinh alert trong `eve.json`!
* **Bản sửa đổi chuẩn xác:** Khai báo rõ ràng `- local.rules` trong mục `rule-files:` của `/etc/suricata/suricata.yaml`.

---

### ❌ Điểm sai 6: File từ điển `rockyou.txt` trên Kali Linux CHƯA được giải nén (TV3 - Kali)
* **Lỗi của AI:** Viết lệnh `hydra -l root -P /usr/share/wordlists/rockyou.txt ...`
* **Sự thật kỹ thuật:** Mặc định trên Kali Linux, từ điển này nằm ở dạng nén: `/usr/share/wordlists/rockyou.txt.gz`!
* **Hậu quả thực tế:** Hydra báo ngay: `[ERROR] File for passwords not found: /usr/share/wordlists/rockyou.txt`.
* **Bản sửa đổi chuẩn xác:** Thêm lệnh giải nén: `sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz` (hoặc tạo file từ điển nhỏ chuyên biệt cho lab).

---

### ❌ Điểm sai 7: Brute-force `root` bị chặn bởi chính sách SSH Ubuntu 22.04 (TV3 - Target)
* **Lỗi của AI:** Dùng Hydra dò pass tài khoản `root` qua SSH trên Target.
* **Sự thật kỹ thuật:** Ubuntu 22.04 LTS mặc định đặt `PermitRootLogin prohibit-password`. SSH từ chối ngay ở tầng xác thực, không sinh log `Failed password for root` chuẩn trong `/var/log/auth.log` $\rightarrow$ Wazuh Rule 5712 không kích hoạt được!
* **Bản sửa đổi chuẩn xác:** Nhắm mục tiêu vào tài khoản người dùng: `hydra -l ubuntu -P ...` (hoặc cấu hình bật password auth cho root nếu muốn).

---

### ❌ Điểm sai 8: Kali mất Static Route khi Reboot (TV3 - Kali)
* **Lỗi của AI:** Lệnh `sudo ip route add 10.0.0.0/24 via 192.168.100.20` chỉ lưu trong RAM.
* **Hậu quả thực tế:** Kali reboot là mất route đến Target (`Destination Host Unreachable`).
* **Bản sửa đổi chuẩn xác:** Tự động kiểm tra và thêm route trong script tự động hóa `scripts/attack_simulation.sh`.

---

### ❌ Điểm sai 9: Chưa phân định rạch ròi giữa README và Kế hoạch triển khai
* **Bản sửa đổi chuẩn xác:**
  * **`README.md`:** Là **Executive Showcase & Quick Runbook** (Bức tranh toàn cảnh, kiến trúc, quy hoạch IP, hướng dẫn pull/sync nhanh ở đầu trang, bảng RACI tóm tắt, ma trận MITRE, lệnh cứu hộ ngắn).
  * **`docs/Ke_Hoach_Trien_Khai.md`:** Là **Detailed Technical Blueprint & Defense Runbook** (Cẩm nang thi công chi tiết từng bước 9.1, 9.2, 9.3, mẹo sửa lỗi, 20 câu hỏi vấn đáp Viva Voce).
  * **Minh chứng hình ảnh:** Dự án **KHÔNG YÊU CẦU** lưu ảnh trong Git để giữ repo gọn nhẹ, 100% tập trung vào Live Demo và mã nguồn cấu hình thực tế.

---

### ❌ Điểm sai 10: Ảo giác về "Install VMware Tools" và thiếu cẩm nang Copy-Paste cho cả 4 máy ảo
* **Lỗi & Thiếu sót của AI:** Không cảnh báo trước việc bấm nút "Install VMware Tools" trên menu VMware Workstation sẽ bị lỗi chết cứng `Could not find component on update server` (do Broadcom đã đổi cụm server cập nhật); thiếu cẩm nang SSH từ máy thật khiến thành viên phải gõ tay hàng chục dòng lệnh phức tạp trên màn hình console đen sì của VMware.
* **Hậu quả thực tế:** Người dùng mất thời gian sửa lỗi VMware Tools không cần thiết, thao tác console dễ bị lỗi font, gõ sai ký tự, kẹt con trỏ chuột.
* **Bản sửa đổi chuẩn xác:**
  * Cảnh báo rõ ràng: **Tuyệt đối KHÔNG bấm "Install VMware Tools" trên VMware**; toàn bộ hệ thống dùng `open-vm-tools` của Linux.
  * Thêm cẩm nang SSH trực tiếp từ PowerShell máy thật cho cả 4 máy ảo (`192.168.100.10`, `192.168.100.20`, `10.0.0.10`, `192.168.100.50`) để thoải mái Copy - Paste bằng `Ctrl + V` hoặc Chuột phải.
  * Thêm lệnh định tuyến trên máy thật Windows: `route add 10.0.0.0 mask 255.255.255.0 192.168.100.20` giúp máy thật SSH trực tiếp vào Target ở dải nội bộ LAN.
  * Cung cấp gói `open-vm-tools-desktop` cho Kali Linux để bật clipboard và kéo thả file hai chiều trên giao diện Desktop.

---

### ❌ Điểm sai 11: Không nhấn mạnh ngữ cảnh phân quyền (sudo vs user), gây lỗi E212 và kẹt Swap E325
* **Lỗi & Thiếu sót của AI:** Viết lệnh cấu hình nhưng không giải thích ngữ cảnh quyền hạn root, khiến thành viên mở file hệ thống bằng tài khoản thường (`wazuh-user`, `ubuntu`) mà quên `sudo`.
* **Hậu quả thực tế:** Người dùng gặp lỗi `E212: Can't open file for writing`, không lưu được file mạng. Khi lỡ tắt cửa sổ ngang, tiến trình bị treo ngầm sinh file swap rác `/var/tmp/*.swp` gây tiếp lỗi `E325: ATTENTION Swap file already exists`.
* **Bản sửa đổi chuẩn xác:**
  * Nhấn mạnh 100% lệnh sửa `/etc/`, dịch vụ `systemctl`, mạng và cài gói bắt buộc phải có `sudo` hoặc chạy dưới quyền root.
  * Hướng dẫn mẹo nhàn nhất: Gõ `sudo -i` ngay khi đăng nhập để lên quyền root `#`, tránh quên `sudo`.
  * Bổ sung quy trình cứu hộ: Thoát `vi` khi bị E212 (`Enter` -> `Esc` -> `:q!` -> `Enter`), và lệnh dọn sạch tiến trình ngầm + file swap: `sudo killall vi 2>/dev/null; sudo rm -f /var/tmp/*.swp 2>/dev/null`.

---

### ❌ Điểm sai 12: Thư mục `/etc/systemd/network` KHÔNG tồn tại mặc định trên Amazon Linux 2023
* **Lỗi & Thiếu sót của AI:** Hướng dẫn chạy `sudo vi /etc/systemd/network/10-static-eth0.network` mà bỏ qua bước kiểm tra/tạo thư mục cha.
* **Sự thật kỹ thuật:** Trên Amazon Linux 2023 (Wazuh 4.8 OVA), các file cấu hình mạng mặc định được tự động sinh tại `/run/systemd/network/`. Thư mục `/etc/systemd/network/` **hoàn toàn chưa tồn tại**! Trình soạn thảo `vi` trong Linux không thể tự động tạo thư mục cha chưa có.
* **Hậu quả thực tế:** Người dùng dù đã dùng `sudo` hoặc đang ở quyền `root` 100%, khi gõ `:wq` vẫn bị `vi` chặn lại với lỗi `E212: Can't open file for writing`. Người dùng bối rối tưởng mình thiếu quyền, thoát ra vào lại gây kẹt swap `E325`.
* **Bản sửa đổi chuẩn xác:**
  * BẮT BUỘC thêm lệnh `sudo mkdir -p /etc/systemd/network` trước khi mở `vi`.
  * Hướng dẫn cứu nguy trực tiếp trong `vi` khi đã lỡ nhập xong: Nhấn `Esc` $\rightarrow$ gõ `:!mkdir -p /etc/systemd/network` $\rightarrow$ `Enter` $\rightarrow$ gõ `:wq` để lưu thoát.

---

## 📋 PHẦN 2: CHECKLIST BẮT BUỘC CHẠY LẠI SAU MỖI TASK/ISSUE

Mỗi khi Agent hoàn thành bất kỳ Issue nào, **BẮT BUỘC** phải rà soát qua 6 cánh cổng kiểm định sau:

```text
[CỔNG 1: KIỂM ĐỊNH MÔI TRƯỜNG & RUNTIME THỰC TẾ]
[ ] Không đoán mò: Công cụ đề xuất (vi, nano, nmcli, ufw) có THỰC SỰ cài sẵn trên HĐH mục tiêu không?
[ ] Có tính đến tình huống chưa có Internet thì không thể tải thêm package (như dnf install nano) chưa?
[ ] Đã dọn dẹp các tệp tin cấu hình rác/dở dang trước khi áp dụng cấu hình mới chưa?
[ ] Đã tạo thư mục cha (mkdir -p /etc/systemd/network) trước khi mở vi tránh lỗi E212 chưa?
[ ] Đã cài iptables-persistent trước khi chạy netfilter-persistent save trên Ubuntu chưa?
[ ] Đã phân quyền usermod -aG suricata wazuh cho Agent đọc eve.json chưa?
[ ] Đã giải nén rockyou.txt.gz trên Kali trước khi chạy Hydra chưa?

[CỔNG 2: KIỂM ĐỊNH ĐỊA CHỈ MẠNG & TOPOLOGY]
[ ] IP đúng chuẩn: Wazuh (192.168.100.10), Sensor (ens33: 192.168.100.20, ens34: 10.0.0.1), Target (10.0.0.10), Kali (192.168.100.50)?
[ ] Đã cấu hình white-list tránh Active Response tự chặn nhầm Gateway 10.0.0.1 chưa?

[CỔNG 3: AN TOÀN BẢO MẬT DỮ LIỆU (ZERO LEAK)]
[ ] Tuyệt đối không chứa Telegram Bot Token thật?
[ ] Tuyệt đối không commit file mật khẩu, file log eve.json hay ổ đĩa máy ảo .vmdk?

[CỔNG 4: QUY CHUẨN NHÁNH GIT (BRANCH GOVERNANCE)]
[ ] TUYỆT ĐỐI KHÔNG làm việc trên nhánh main!
[ ] TUYỆT ĐỐI KHÔNG làm việc trên các nhánh đã hoàn thành trong quá khứ!
[ ] Đang làm việc trên đúng NHÁNH CÔNG VIỆI HIỆN TẠI (VD: feature/..., fix/...)?

[CỔNG 5: TÀI LIỆU HÓA ĐỒNG BỘ (SINGLE SOURCE OF TRUTH)]
[ ] Phân định rõ ràng: README.md (Executive Showcase & Quick Runbook) vs Ke_Hoach_Trien_Khai.md (Detailed Technical Blueprint)?
[ ] Mọi thay đổi kỹ thuật mới đã được cập nhật đồng bộ song song vào README.md và docs/Ke_Hoach_Trien_Khai.md chưa?

[CỔNG 6: TẬP TRUNG LIVE DEMO & KHÔNG RÁC ẢNH]
[ ] Không yêu cầu tạo thư mục screenshots hay nhồi nhét ảnh vào Git repo, bảo toàn repo sạch đẹp chuẩn code kỹ thuật!
```

---

## 🚨 PHẦN 3: GIAO THỨC DỪNG KHẨN CẤP & KIỂM SOÁT THẨM QUYỀN (HUMAN APPROVAL GATE)

### ⛔ QUY TẮC BẤT DI BẤT DỊCH:
1. **NGHIÊM CẤM** tự ý chạy `git commit` hoặc `git push` lên GitHub khi chưa có sự xác nhận rõ ràng của người dùng trong lượt hội thoại hiện tại.
2. **NGHIÊM CẤM** vượt ra ngoài phạm vi yêu cầu của task.
3. Khi gặp lỗi lặp lại 3 lần không giải quyết được $\rightarrow$ **KÍCH HOẠT CIRCUIT BREAKER**, dừng lại và lập báo cáo Escalation Template xin ý kiến người dùng.
