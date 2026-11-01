# 🛡️ GIAO THỨC KIỂM ĐỊNH QA & CHỐNG ẢO GIÁC AI (STRICT QA PROTOCOL)

> **Mục đích:** File này được thiết kế để Agent tự chạy phản biện, kiểm tra chéo và rà soát lại toàn bộ kết quả sau mỗi lần giải quyết Issue/Task trong dự án **SOC Lab (Wazuh + Suricata)**.  
> **Nguyên tắc cốt lõi:** Luôn nghi ngờ giả định ban đầu, không tự tin thái quá, đối chiếu từng dòng lệnh với kiến trúc mạng thực tế trước khi bàn giao.

---

## 🔍 PHẦN 1: BẢN TỰ PHẢN BIỆN CỦA CHUYÊN GIA QA (AUDIT TRAIL)

Sau khi đối chiếu chi tiết với [**docs/Ke_Hoach_Trien_Khai.md**](docs/Ke_Hoach_Trien_Khai.md), chuyên gia QA chỉ ra **4 điểm sai lệch, thiếu logic và mơ hồ nghiêm trọng** trong các câu trả lời trước đó:

### ❌ Điểm sai 1: Sai lệch cấu hình kích hoạt CI (Flawed Trigger Logic)
* **Lỗi trước đó:** Khi người dùng yêu cầu chỉ check Pull Request, AI đã xóa hoàn toàn sự kiện `push` khỏi workflow.
* **Hậu quả thực tế:** 
  1. Khi Admin dùng quyền đặc cách push trực tiếp lên `main`, hoặc khi một PR được merge vào `main`, **CI sẽ không chạy trên nhánh `main`**.
  2. Dẫn đến huy hiệu trạng thái (Badge `CI Passing`) trên file `README.md` sẽ bị mất tín hiệu hoặc hiển thị trạng thái cũ, không phản ánh đúng sức khỏe của nhánh chính.
* **Khắc phục chuẩn xác:** Phải giữ cấu hình:
  ```yaml
  on:
    push:
      branches: [ "main" ]        # Cập nhật huy hiệu khi merge hoặc admin push vào main
    pull_request:
      branches: [ "main" ] # Chỉ chạy kiểm tra khi có PR nộp vào main, không spam nhánh con
  ```

### ❌ Điểm sai 2: Mơ hồ về cơ chế phát hiện giữa Network IDS và Host SIEM
* **Lỗi trước đó:** Trong bảng kịch bản TC-02 (Brute-force SSH), tài liệu mô tả Suricata bắt SSH Scan và Wazuh kích hoạt Rule 5712.
* **Hậu quả thực tế:** Gây nhầm lẫn chết người cho sinh viên khi vấn đáp. Rule 5712 của Wazuh là **Host Log Analysis** (bóc tách từ `/var/log/auth.log` trên máy chủ mục tiêu), chứ **KHÔNG PHẢI** tương quan từ luồng mạng của Suricata. Suricata chỉ nhìn thấy các gói tin TCP bắt tay cổng 22, không thể đọc được nội dung xác thực mã hóa SSH để đếm số lần sai mật khẩu.
* **Khắc phục chuẩn xác:** Phải tách bạch rạch ròi:
  * **Suricata (Network):** Bắt `ET SCAN Potential SSH Scan` (quét nhiều cổng/kết nối bất thường).
  * **Wazuh Agent trên Target (Host):** Đọc `/var/log/auth.log` bắt 5 lần `authentication failure` $\rightarrow$ sinh Rule 5712 (Level 10) $\rightarrow$ kích hoạt `firewall-drop` chặn IP trên Target.

### ❌ Điểm sai 3: Cắt xén các cảnh báo sống còn trong README
* **Lỗi trước đó:** File `README.md` ban đầu bị rút gọn quá mức, bỏ qua 6 sai lầm chí mạng trong file kế hoạch.
* **Hậu quả thực tế:** Thành viên clone repo về không hề biết:
  1. Kali bắt buộc phải gõ `sudo ip route add 10.0.0.0/24 via 192.168.100.20` mới tới được Target.
  2. Sensor phải bật `net.ipv4.ip_forward=1` thì Target mới ra được Internet để cài Nginx.
  3. Wazuh Indexer nếu không giới hạn `-Xms1g -Xmx1g` sẽ làm treo đứng máy tính thật của sinh viên.
* **Khắc phục chuẩn xác:** Đồng bộ toàn bộ 6 sai lầm chí mạng và bảng cấu hình Virtual Network Editor (tắt DHCP trên VMnet2) vào `README.md`.

### ❌ Điểm sai 4: Để Placeholder URL ảo trên README
* **Lỗi trước đó:** Badge CI trên README để URL mẫu `USERNAME_OR_ORG/soc-lab-wazuh-suricata` dù repo thực tế đã được liên kết với `Team16S/soc-lab-wazuh-suricata`.
* **Khắc phục chuẩn xác:** Cập nhật chính xác đường dẫn của tổ chức `Team16S`.

---

## 📋 PHẦN 2: CHECKLIST BẮT BUỘC CHẠY LẠI SAU MỖI ISSUE (AGENT SELF-CHECK)

Mỗi khi Agent hoàn thành bất kỳ Issue hoặc chỉnh sửa code nào, **BẮT BUỘC** phải rà soát qua 6 cánh cổng kiểm định sau:

```text
[CỔNG 1: KIỂM ĐỊNH ĐỊA CHỈ MẠNG & ROUTING]
[ ] IP có đúng quy hoạch: Wazuh (192.168.100.10), Sensor (ens33: 192.168.100.20, ens34: 10.0.0.1), Target (10.0.0.10), Kali (192.168.100.50)?
[ ] Có tính đến lệnh static route trên Kali chưa?
[ ] Đã cấu hình white-list tránh Active Response tự chặn nhầm Gateway 10.0.0.1 chưa?

[CỔNG 2: PHÂN ĐỊNH TẦNG BẢO VỆ (DEFENSE-IN-DEPTH)]
[ ] Sự kiện này thuộc tầng Mạng (Suricata NIDS/IPS) hay tầng Máy chủ (Wazuh HIDS/FIM)?
[ ] Có gán nhầm tính năng của Wazuh sang Suricata hoặc ngược lại không?

[CỔNG 3: CÚ PHÁP CẤU HÌNH & RUNTIME COMPATIBILITY]
[ ] File YAML: Đã thụt lề chuẩn bằng khoảng trắng (space), tuyệt đối không dùng tab?
[ ] File XML: Các thẻ <group>, <rule>, <regex> đã được đóng đầy đủ chưa?
[ ] Script Python: Đã phân quyền chmod 750 và chown root:wazuh chưa?

[CỔNG 4: AN TOÀN BẢO MẬT DỮ LIỆU (ZERO LEAK)]
[ ] Tuyệt đối không chứa Telegram Bot Token thật (ví dụ chuỗi dạng 123456789:ABC...)?
[ ] Tuyệt đối không commit file mật khẩu, file log eve.json hay ổ đĩa máy ảo .vmdk?

[CỔNG 5: QUY CHUẨN GIT & BRANCH]
[ ] Đang làm việc trên đúng nhánh phân công (feature/wazuh-..., feature/suricata-..., feature/target-...)?
[ ] Commit message có tuân thủ format: [loại]: [mô tả tiếng Việt không dấu]?

[CỔNG 6: TÀI LIỆU HÓA (DOCUMENTATION INTEGRITY)]
[ ] Mọi thay đổi kỹ thuật mới đã được cập nhật đồng bộ vào README.md và docs/Ke_Hoach_Trien_Khai.md chưa?
```

---

## 🚨 PHẦN 3: GIAO THỨC DỪNG KHẨN CẤP KHI VƯỢT QUÁ TẦM KIỂM SOÁT (FAIL-SAFE & ESCALATION)

### ⛔ QUY TẮC BẤT DI BẤT DỊCH: KIỂM SOÁT THẨM QUYỀN GIT (HUMAN APPROVAL GATE)
* ❌ **TUYỆT ĐỐI CẤM:** Tự ý chạy `git commit` và `git push` lên GitHub khi chưa có sự cho phép rõ ràng từ người dùng.
* ✅ **QUY TRÌNH BẮT BUỘC:** 
  1. Mọi chỉnh sửa chỉ thực hiện ở cấp độ tệp tin cục bộ (Local files).
  2. Xuất trình tóm tắt thay đổi và diff rõ ràng.
  3. Cung cấp sẵn câu lệnh Git hoặc xin phép người dùng xác nhận trước khi thực hiện bất kỳ lệnh commit/push nào.

---

Khi gặp các tình huống **thiếu sót, sai lệch nghiêm trọng hoặc vượt quá tầm kiểm soát của Agent đối với người dùng**, Agent **TUYỆT ĐỐI KHÔNG ĐƯỢC:**
* ❌ Tự ý bịa đặt (hallucinate) ra câu trả lời hoặc lệnh không có cơ sở kiểm chứng.
* ❌ Tự tiện thực thi các lệnh mang tính phá hủy (Destructive actions) như xóa dữ liệu, flush mạng, đổi IP ngoài luồng kế hoạch.
* ❌ Cố gắng sửa lỗi mù quáng trong một vòng lặp vô tận (Looping failures).

### 1. Các trường hợp kích hoạt cơ chế Dừng Khẩn Cấp (Circuit Breaker):
1. **Quy tắc 3 lần thất bại (3-Strike Rule):** Nếu Agent thử sửa một lỗi kỹ thuật (dịch vụ không start, agent mất kết nối, lỗi mạng) đến **lần thứ 3** mà vẫn không thành công $\rightarrow$ **DỪNG LẠI NGAY LẬP TỨC**.
2. **Lỗi phụ thuộc phần cứng máy thật:** Thiếu RAM vật lý, CPU chưa bật cờ ảo hóa trong BIOS (Intel VT-x / AMD-V), xung đột card mạng ảo VMware với Windows Host $\rightarrow$ Agent không thể can thiệp từ terminal, bắt buộc phải báo người dùng.
3. **Mâu thuẫn yêu cầu (Requirement Conflict):** Yêu cầu mới của người dùng mâu thuẫn trực tiếp với kế hoạch chốt trong `docs/Ke_Hoach_Trien_Khai.md` hoặc làm hỏng phần việc của thành viên khác trong nhóm.
4. **Nguy cơ mất an toàn dữ liệu:** Thao tác có khả năng làm mất cấu hình, mất quyền root máy ảo hoặc khóa nhầm đường truyền SSH chính mình.

### 2. Định dạng báo cáo bắt buộc gửi Người Dùng khi Leo Thang (Escalation Template):

Khi dừng khẩn cấp, Agent phải xuất trình báo cáo minh bạch theo mẫu sau:

```text
================================================================================
🚨 CẢNH BÁO: PHÁT HIỆN SỰ CỐ VƯỢT QUÁ TẦM KIỂM SOÁT CỦA AGENT
================================================================================
1. VẤN ĐỀ GẶP PHẢI:
   [Mô tả chính xác lỗi kỹ thuật / điểm mâu thuẫn / nguyên nhân bế tắc]

2. NGUYÊN NHÂN GỐC RỄ ĐÃ XÁC MINH:
   [Lý do kỹ thuật thực tế sau khi đã tra soát logs, không phỏng đoán]

3. RỦI RO NẾU TIẾP TỤC TỰ ĐỘNG THỰC THI:
   [Hậu quả có thể xảy ra: Treo máy ảo, mất kết nối mạng, sai lệch đồ án]

4. CÁC PHƯƠNG ÁN ĐỀ XUẤT CHO NGƯỜI DÙNG QUYẾT ĐỊNH:
   👉 Phương án A: [Giải pháp 1 - Ưu điểm & Nhược điểm]
   👉 Phương án B: [Giải pháp 2 - Ưu điểm & Nhược điểm]
   👉 Phương án C (Khôi phục): Revert về Snapshot VMware hoặc commit Git gần nhất.
================================================================================
```

---
*Mỗi lần Agent xử lý xong Issue, hãy chạy lệnh đối chiếu lại toàn bộ checklist trong `@prompt.md` để đảm bảo hệ thống luôn vận hành ổn định, chính xác 100% và không bao giờ tự ý vượt quá thẩm quyền của người dùng.*
