# 🛡️ GIAO THỨC KIỂM ĐỊNH QA, CHỐNG ẢO GIÁC AI & MINH CHỨNG HÌNH ẢNH (STRICT QA PROTOCOL)

> **Mục đích:** File này được thiết kế để Agent tự phản biện, kiểm tra chéo và rà soát lại toàn bộ kết quả sau mỗi lần giải quyết Issue/Task trong dự án **SOC Lab (Wazuh + Suricata)**.  
> **Cơ chế áp dụng:** Agent chỉ cập nhật file này sau mỗi lần hoàn thành task issue. Phải đọc lại trước và sau khi làm task để tránh lặp lại sai lầm, tuyệt đối không được vượt tầm kiểm soát của người dùng.

---

## 🔍 PHẦN 1: BẢN TỰ PHẢN BIỆN CỦA CHUYÊN GIA QA KHẮT KHE (AUDIT TRAIL)

Sau khi đối chiếu nghiêm ngặt với thực tế máy ảo Wazuh 4.8 OVA và các tương tác dòng lệnh vừa qua, chuyên gia QA chỉ ra **4 điểm sai lệch, thiếu logic và mơ hồ nghiêm trọng** mà AI đã mắc phải:

### ❌ Điểm sai 1: Ảo giác về công cụ cài sẵn (Khuyên dùng `nano` khi chưa có mạng)
* **Lỗi của AI:** Trong câu trả lời trước, AI đề xuất "Cách 1: Khuyên dùng `nano` trực quan để không lo kẹt lệnh".
* **Lỗ hổng chết người:** Amazon Linux 2023 (nền tảng của Wazuh 4.8 OVA) là bản minimal, **mặc định KHÔNG HỀ cài sẵn `nano`**, mà chỉ có **`vi`**! 
* **Hậu quả thực tế:** Người dùng đang ở bước cấu hình IP ban đầu (chưa có IP tĩnh, chưa có Internet) nên **hoàn toàn không thể chạy `sudo dnf install -y nano`** để tải về. Nếu làm theo AI gõ `sudo nano`, máy ảo sẽ báo lỗi `bash: nano: command not found`, làm người dùng rơi vào bế tắc khác.
* **Bản sửa đổi chuẩn xác:** Công cụ duy nhất chắc chắn có sẵn 100% trên máy ảo lúc chưa có mạng là **`vi`** (hoặc lệnh `cat << 'EOF'`). Tài liệu phải hướng dẫn chi tiết từng phím bấm của `vi` (nhấn `i` để nhập, nhấn `Esc` rồi gõ `:wq` để lưu).

---

### ❌ Điểm sai 2: Không cảnh báo rác cấu hình sau khi kẹt Heredoc
* **Lỗi của AI:** Khi thấy người dùng bị kẹt ở dấu `>` do gõ nhầm `.bash...` và `wq`, AI chỉ bảo bấm `Ctrl + C` rồi chạy lệnh tiếp mà không yêu cầu kiểm tra/xóa file rác.
* **Lỗ hổng kỹ thuật:** Nếu lệnh `tee` đã bắt đầu ghi file dở dang trước khi bị `Ctrl + C`, file `/etc/systemd/network/10-static-eth0.network` có thể chứa các dòng rác cú pháp (`.bash_history`, `wq`).
* **Hậu quả thực tế:** Khi khởi động lại `systemd-networkd`, dịch vụ sẽ đọc phải cú pháp rác, báo lỗi phân tích cấu hình (parse error) và từ chối cấp IP tĩnh, khiến mạng tiếp tục không thông.
* **Bản sửa đổi chuẩn xác:** Bắt buộc phải có bước dọn sạch: `sudo rm -f /etc/systemd/network/10-static-eth0.network` hoặc `cat` kiểm tra nội dung file trước khi khởi động lại dịch vụ.

---

### ❌ Điểm sai 3: Vi phạm nguyên tắc phân nhánh Git (Làm việc trực tiếp trên `main`)
* **Lỗi của AI:** Tự ý stage các file sửa đổi trên nhánh `main` và suýt commit thẳng lên `main` thay vì tạo nhánh công việc riêng.
* **Lỗ hổng quản trị:** Nhánh `main` là nhánh sản phẩm đã được bật Branch Protection. Mọi sửa đổi phải thực hiện trên **nhánh công việc độc lập** (ví dụ: `feature/wazuh-siem-network-setup`), sau đó tạo Pull Request để CI kiểm duyệt. Tuyệt đối không làm trên nhánh cũ đã xong hoặc commit đè lên `main`.
* **Bản sửa đổi chuẩn xác:** Chuyển toàn bộ công việc sang nhánh công việc riêng biệt, chỉ merge vào `main` khi có xác nhận từ người dùng qua Pull Request.

---

### ❌ Điểm sai 4: Thiếu quy chuẩn về Minh chứng hình ảnh (Screenshots Protocol)
* **Lỗi của AI:** Khi người dùng chụp màn hình thực tế, AI trả lời đơn lẻ từng trường hợp mà không hệ thống hóa thành quy chuẩn lưu trữ minh chứng đồ án.
* **Hậu quả thực tế:** Khi viết báo cáo đồ án, nhóm không có quy chuẩn đường dẫn và quy cách đặt tên ảnh, dẫn đến việc thiếu bằng chứng thực nghiệm khi bảo vệ trước hội đồng.
* **Bản sửa đổi chuẩn xác:** Thiết lập mục hướng dẫn chụp ảnh minh chứng kèm đường dẫn chuẩn xác (xem Phần 3).

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

*Ví dụ:*
* Minh chứng cấu hình mạng IP tĩnh Wazuh thành công:  
  `docs/screenshots/tv1_wazuh_ip_static_ok.png`
* Minh chứng 3 dịch vụ Wazuh đang chạy (`systemctl status`):  
  `docs/screenshots/tv1_wazuh_services_active.png`
* Minh chứng Suricata chạy 2 card mạng:  
  `docs/screenshots/tv2_suricata_2interfaces_ok.png`
* Minh chứng Active Response chặn IP Kali:  
  `docs/screenshots/tv3_target_iptables_drop.png`

### 3. Cú pháp nhúng ảnh vào Markdown (`README.md` hoặc `Ke_Hoach_Trien_Khai.md`):
```markdown
![Minh chứng cấu hình IP tĩnh Wazuh 4.8 thành công](docs/screenshots/tv1_wazuh_ip_static_ok.png)
```

---

## 🛠️ PHẦN 3: BẢN HƯỚNG DẪN CHUẨN XÁC CẤU HÌNH MẠNG WAZUH 4.8 OVA (GROUND TRUTH)

Dành cho Thành viên 1 khi thiết lập máy ảo Wazuh 4.8 OVA trên VMware:

### Bước 1: Dọn sạch file rác (nếu lỡ gõ dở dang)
```bash
sudo rm -f /etc/systemd/network/10-static-eth0.network
```

### Bước 2: Tạo file cấu hình mạng bằng `vi` (Công cụ mặc định 100% có sẵn)
```bash
sudo vi /etc/systemd/network/10-static-eth0.network
```
* **Thao tác trong `vi`:**
  1. Nhấn phím **`i`** (màn hình góc dưới hiện `-- INSERT --`).
  2. Gõ hoặc dán nội dung chuẩn:
     ```ini
     [Match]
     Name=eth0

     [Network]
     Address=192.168.100.10/24
     Gateway=192.168.100.2
     DNS=8.8.8.8
     DNS=1.1.1.1
     ```
  3. Nhấn phím **`Esc`** trên bàn phím.
  4. Gõ **`:wq`** rồi nhấn **`Enter`** (để lưu và thoát).

*(Mẹo: Bấm **`Ctrl + Alt`** để nhả chuột từ VMware ra Windows).*

### Bước 3: Áp dụng cấu hình và kiểm tra kết quả
```bash
sudo systemctl restart systemd-networkd
ip a show eth0
ping -c 3 8.8.8.8
```
*(Nếu có yêu cầu minh chứng: Chụp màn hình kết quả lệnh `ip a show eth0` lưu vào `docs/screenshots/tv1_wazuh_ip_static_ok.png`).*

---

## 📋 PHẦN 4: CHECKLIST BẮT BUỘC CHẠY LẠI SAU MỖI TASK/ISSUE

Mỗi khi Agent hoàn thành bất kỳ Issue nào, **BẮT BUỘC** phải rà soát qua 6 cánh cổng kiểm định sau:

```text
[CỔNG 1: KIỂM ĐỊNH MÔI TRƯỜNG & RUNTIME THỰC TẾ]
[ ] Không đoán mò: Công cụ đề xuất (vi, nano, nmcli, ufw) có THỰC SỰ cài sẵn trên HĐH mục tiêu không?
[ ] Có tính đến tình huống chưa có Internet thì không thể tải thêm package (như dnf install nano) chưa?
[ ] Đã dọn dẹp các tệp tin cấu hình rác/dở dang trước khi áp dụng cấu hình mới chưa?

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
[ ] Mọi thay đổi kỹ thuật mới đã được cập nhật đồng bộ song song vào README.md và docs/Ke_Hoach_Trien_Khai.md chưa?
```

---

## 🚨 PHẦN 5: GIAO THỨC DỪNG KHẨN CẤP & KIỂM SOÁT THẨM QUYỀN (HUMAN APPROVAL GATE)

### ⛔ QUY TẮC BẤT DI BẤT DỊCH:
1. **NGHIÊM CẤM** tự ý chạy `git commit` hoặc `git push` lên GitHub khi chưa có sự xác nhận rõ ràng của người dùng trong lượt hội thoại hiện tại.
2. **NGHIÊM CẤM** vượt ra ngoài phạm vi yêu cầu của task.
3. Khi gặp lỗi lặp lại 3 lần không giải quyết được $\rightarrow$ **KÍCH HOẠT CIRCUIT BREAKER**, dừng lại và lập báo cáo Escalation Template xin ý kiến người dùng.
