# 🛡️ GIAO THỨC KIỂM ĐỊNH QA, CHỐNG ẢO GIÁC AI & MINH CHỨNG HÌNH ẢNH (STRICT QA PROTOCOL)

> **Mục đích:** File này được thiết kế để Agent tự phản biện, kiểm tra chéo và rà soát lại toàn bộ kết quả sau mỗi lần giải quyết Issue/Task trong dự án **SOC Lab (Wazuh + Suricata)**.  
> **Cơ chế áp dụng:** Agent chỉ cập nhật file này sau mỗi lần hoàn thành task issue. Phải đọc lại trước và sau khi làm task để tránh lặp lại sai lầm, tuyệt đối không được vượt tầm kiểm soát của người dùng.

---

## 🔍 PHẦN 1: BẢN TỰ PHẢN BIỆN CỦA CHUYÊN GIA QA KHẮT KHE (AUDIT TRAIL)

Sau khi đối chiếu nghiêm ngặt với thực tế máy ảo VMware của 3 thành viên, chuyên gia QA chỉ ra **9 điểm sai lệch, thiếu logic và mơ hồ nghiêm trọng** cần được khắc phục triệt để:

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
* **Lỗi của AI:** Nhồi nhét lệnh chi tiết vào README làm mất tính tổng quan, hoặc cắt xén kế hoạch triển khai.
* **Bản sửa đổi chuẩn xác:**
  * **`README.md`:** Là **Executive Showcase & Quick Runbook** (Bức tranh toàn cảnh, kiến trúc, quy hoạch IP, sơ đồ dữ liệu, bảng RACI tóm tắt, ma trận MITRE, lệnh cứu hộ ngắn).
  * **`docs/Ke_Hoach_Trien_Khai.md`:** Là **Detailed Technical Blueprint & Defense Runbook** (Cẩm nang thi công chi tiết từng bước 9.1, 9.2, 9.3, mẹo sửa lỗi, 20 câu hỏi vấn đáp Viva Voce).

---

## 📷 PHẦN 2: HƯỚNG DẪN CHỤP ẢNH MINH CHỨNG & ĐƯỜNG DẪN LƯU TRỮ (EVIDENCE PROTOCOL)

Khi thực hiện các bước cấu hình có yêu cầu lưu lại minh chứng thực nghiệm (hoặc khi gặp lỗi cần báo cáo):

### 1. Thư mục lưu trữ chuẩn trong Repository:
Tất cả ảnh minh chứng của dự án bắt buộc lưu vào thư mục:
```text
docs/screenshots/
```
*(Nếu thư mục chưa có, tạo bằng lệnh: `mkdir -p docs/screenshots`)*

### 2. Quy tắc đặt tên file ảnh minh chứng:
Đặt tên viết thường, không dấu, dùng dấu gạch dưới `_` theo cấu trúc:
`[thanh_vien]_[ten_may_ao]_[noi_dung_minh_chung].png`

*Ví dụ chuẩn xác:*
* **Thành viên 1:**  
  `docs/screenshots/tv1_wazuh_ip_static_ok.png` (Minh chứng gán IP tĩnh thành công)  
  `docs/screenshots/tv1_wazuh_services_active.png` (Minh chứng 3 dịch vụ SIEM đang chạy)  
  `docs/screenshots/tv1_wazuh_dashboard_login.png` (Minh chứng giao diện Web Dashboard)
* **Thành viên 2:**  
  `docs/screenshots/tv2_sensor_2interfaces_ok.png` (Minh chứng 2 card mạng ens33 & ens34)  
  `docs/screenshots/tv2_sensor_iptables_nat.png` (Minh chứng lệnh iptables NAT MASQUERADE)  
  `docs/screenshots/tv2_suricata_eve_alert.png` (Minh chứng Suricata ghi alert vào eve.json)
* **Thành viên 3:**  
  `docs/screenshots/tv3_target_ping_internet.png` (Minh chứng Target thông mạng qua Sensor)  
  `docs/screenshots/tv3_target_fim_alert.png` (Minh chứng Wazuh phát hiện sửa đổi file Web)  
  `docs/screenshots/tv3_target_active_response_drop.png` (Minh chứng iptables tự động chặn IP Kali)

### 3. Cú pháp nhúng ảnh vào Markdown:
```markdown
![Mô tả ảnh](docs/screenshots/tv1_wazuh_ip_static_ok.png)
```

---

## 📋 PHẦN 3: CHECKLIST BẮT BUỘC CHẠY LẠI SAU MỖI TASK/ISSUE

Mỗi khi Agent hoàn thành bất kỳ Issue nào, **BẮT BUỘC** phải rà soát qua 6 cánh cổng kiểm định sau:

```text
[CỔNG 1: KIỂM ĐỊNH MÔI TRƯỜNG & RUNTIME THỰC TẾ]
[ ] Không đoán mò: Công cụ đề xuất (vi, nano, nmcli, ufw) có THỰC SỰ cài sẵn trên HĐH mục tiêu không?
[ ] Có tính đến tình huống chưa có Internet thì không thể tải thêm package (như dnf install nano) chưa?
[ ] Đã dọn dẹp các tệp tin cấu hình rác/dở dang trước khi áp dụng cấu hình mới chưa?
[ ] Đã cài iptables-persistent trước khi chạy netfilter-persistent save trên Ubuntu chưa?
[ ] Đã phân quyền usermod -aG suricata wazuh cho Agent đọc eve.json chưa?
[ ] Đã giải nén rockyou.txt.gz trên Kali trước khi chạy Hydra chưa?

[CỔNG 2: KIỂM ĐỊNH ĐỊA CHỈ MẠNG & TOPOLOGY]
[ ] IP đúng chuẩn: Wazuh (192.168.100.10), Sensor (ens33: 192.168.100.20, ens34: 10.0.0.1), Target (10.0.0.10), Kali (192.168.100.50)?
[ ] Đã cấu hình white-list tránh Active Response tự chặn nhầm Gateway 10.0.0.1 chưa?

[CỔNG 3: MINH CHỨNG HÌNH ẢNH (NẾU CÓ YÊU CẦU)]
[ ] Ảnh chụp màn hình có được lưu đúng thư mục docs/screenshots/ không?
[ ] Tên file ảnh có đúng định dạng: tvX_mayao_noidung.png không?
[ ] Đã tạo liên kết markdown hiển thị ảnh trong tài liệu chưa?

[CỔNG 4: AN TOÀN BẢO MẬT DỮ LIỆU (ZERO LEAK)]
[ ] Tuyệt đối không chứa Telegram Bot Token thật?
[ ] Tuyệt đối không commit file mật khẩu, file log eve.json hay ổ đĩa máy ảo .vmdk?

[CỔNG 5: QUY CHUẨN NHÁNH GIT (BRANCH GOVERNANCE)]
[ ] TUYỆT ĐỐI KHÔNG làm việc trên nhánh main!
[ ] TUYỆT ĐỐI KHÔNG làm việc trên các nhánh đã hoàn thành trong quá khứ!
[ ] Đang làm việc trên đúng NHÁNH CÔNG VIỆC HIỆN TẠI (VD: feature/..., fix/...)?

[CỔNG 6: TÀI LIỆU HÓA ĐỒNG BỘ (SINGLE SOURCE OF TRUTH)]
[ ] Phân định rõ ràng: README.md (Executive Showcase & Quick Runbook) vs Ke_Hoach_Trien_Khai.md (Detailed Technical Blueprint)?
[ ] Mọi thay đổi kỹ thuật mới đã được cập nhật đồng bộ song song vào README.md và docs/Ke_Hoach_Trien_Khai.md chưa?
```

---

## 🚨 PHẦN 4: GIAO THỨC DỪNG KHẨN CẤP & KIỂM SOÁT THẨM QUYỀN (HUMAN APPROVAL GATE)

### ⛔ QUY TẮC BẤT DI BẤT DỊCH:
1. **NGHIÊM CẤM** tự ý chạy `git commit` hoặc `git push` lên GitHub khi chưa có sự xác nhận rõ ràng của người dùng trong lượt hội thoại hiện tại.
2. **NGHIÊM CẤM** vượt ra ngoài phạm vi yêu cầu của task.
3. Khi gặp lỗi lặp lại 3 lần không giải quyết được $\rightarrow$ **KÍCH HOẠT CIRCUIT BREAKER**, dừng lại và lập báo cáo Escalation Template xin ý kiến người dùng.
