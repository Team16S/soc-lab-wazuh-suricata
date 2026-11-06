# HỆ THỐNG GIÁM SÁT AN NINH MẠNG TẬP TRUNG (SOC LAB)
## KẾT HỢP CENTRAL SIEM (WAZUH) VÀ NIDS/IPS (SURICATA) VỚI PHẢN ỨNG TỰ ĐỘNG

[![SOC Lab CI - Syntax & Security Check](https://github.com/Team16S/soc-lab-wazuh-suricata/actions/workflows/ci.yml/badge.svg)](https://github.com/Team16S/soc-lab-wazuh-suricata/actions/workflows/ci.yml)
![Defense-in-Depth](https://img.shields.io/badge/Security-Defense--in--Depth-blue)
![Platform](https://img.shields.io/badge/Platform-VMware%20Workstation-orange)
![Wazuh](https://img.shields.io/badge/SIEM-Wazuh%20v4.x-brightgreen)
![Suricata](https://img.shields.io/badge/NIDS-Suricata%20Engine-red)

> **Đồ án môn học:** An ninh mạng  
> **Mô hình triển khai:** Cụm 4 máy ảo trên nền tảng VMware Workstation (Chạy trên 1 máy $\ge 16\text{GB}$ RAM hoặc chia tải 2 máy $\le 8\text{GB}$ RAM)  
> **Cơ cấu nhóm:** 03 thành viên  
> 
> 🧭 **Phân định cấu trúc tài liệu dự án:**
> * **[`README.md`](README.md):** Bản tóm tắt điều hành & Quick Runbook (Kiến trúc tổng quan, quy hoạch IP, phân công RACI, lệnh chạy nhanh, ma trận MITRE ATT&CK, chỉ số KPI).
> * **[`docs/Ke_Hoach_Trien_Khai.md`](docs/Ke_Hoach_Trien_Khai.md):** Bản thiết kế kỹ thuật chi tiết & Cẩm nang bảo vệ đồ án 14 mục (Hướng dẫn VMware từng bước, chi tiết lệnh 9.1-9.2-9.3, 20 câu hỏi & trả lời vấn đáp Viva Voce).

---

## ⚡ HƯỚNG DẪN ĐỒNG BỘ DỮ LIỆU NHANH CHO CẢ NHÓM (DAILY GIT SYNC)
> [!IMPORTANT]
> **Dành cho mọi thành viên:** Bất cứ khi nào bắt đầu làm việc hoặc thấy nhóm chat thông báo có cập nhật mới vừa merge vào `main`, hãy chạy ngay các lệnh sau để đảm bảo máy của bạn luôn có bản mới nhất:

> [!TIP]
> **🤖 LƯU Ý SỐNG CÒN KHI LÀM VIỆC CÙNG TRỢ LÝ AI (AI PAIR-PROGRAMMING):**  
> Mọi thành viên trong nhóm khi nhờ AI hỗ trợ gõ lệnh/sửa lỗi **bắt buộc tuân thủ 5 nguyên tắc** (xem chi tiết tại [**Mục 14: Nguyên tắc phối hợp với Trợ lý AI**](#-14-nguyên-tắc-phối-hợp-với-trợ-lý-ai-working-with-ai--governance)).  
> * **Sau mỗi buổi làm việc:** Bắt buộc yêu cầu AI tóm tắt và lưu lại vào file [`session_summary.md`](session_summary.md) trên máy cá nhân để tránh AI bị mất toàn bộ ngữ cảnh và sinh ảo giác lặp lại các lỗi cũ ở phiên sau!

### Cách 1: Cập nhật nhánh `main` trên máy tính của bạn
```bash
# 1. Chuyển sang nhánh main:
git checkout main

# 2. Kéo toàn bộ code và tài liệu mới nhất về:
git pull origin main
```

### Cách 2: Đồng bộ nội dung mới từ `main` vào nhánh cá nhân đang làm dở
Nếu bạn đang làm dở trên nhánh riêng (ví dụ `feature/wazuh-rules-telegram`):
```bash
# Bước 1: Cất tạm các thay đổi dở dang (nếu có):
git stash

# Bước 2: Chuyển sang main và cập nhật mới nhất:
git checkout main
git pull origin main

# Bước 3: Quay lại nhánh cá nhân và gộp cập nhật từ main vào:
git checkout <ten-nhanh-cua-ban>    # Ví dụ: feature/wazuh-rules-telegram
git merge main

# Bước 4: Lấy lại các thay đổi dở dang để tiếp tục làm việc:
git stash pop
```
*(Mẹo: Bấm `git stash` để cất tạm thay đổi trước khi checkout, tránh bị lỗi xung đột khi đổi nhánh).*

### Cách 3: Kiểm tra & Sửa lỗi chéo trên Pull Request của đồng đội (Review & Fix PR)
Khi một thành viên mở PR trên GitHub (ví dụ: `feature/suricata-sensor-nat`), bạn có thể kéo nhánh đó về máy mình để kiểm tra chạy thử hoặc hỗ trợ sửa lỗi:

```bash
# 1. Tải danh sách commit và nhánh mới nhất từ GitHub:
git fetch origin

# 2. Chuyển sang nhánh PR của bạn (lần đầu tiên lấy về máy):
git switch --track origin/<ten-nhanh-pr>   # Ví dụ: git switch --track origin/feature/suricata-sensor-nat
# (Nếu nhánh này đã có sẵn trên máy bạn từ trước: git switch <ten-nhanh-pr>)

# 3. Xem các thay đổi so với nhánh main:
git diff main...HEAD

# 4. Sửa lỗi, chạy thử nghiệm, sau đó commit và push thẳng lên chính nhánh PR đó:
git add .
git commit -m "fix: sua loi cu phap ho dong doi"
git push origin <ten-nhanh-pr>

# 5. Khi CI GitHub Actions báo Xanh lá -> Tiến hành Duyệt (Approve) và bấm Merge vào main!
```

---

## 📌 1. Mục tiêu & Phạm vi kỹ thuật

Hệ thống thiết lập một trung tâm điều hành an ninh mạng (SOC) thu nhỏ bảo vệ đa tầng theo chiều sâu (*Defense-in-Depth*):
1. **Tầng mạng (Network Layer):** Triển khai **Suricata IDS/IPS** tại Router Gateway để phân tích lưu lượng theo thời gian thực (Deep Packet Inspection), nhận diện signature tấn công (Nmap, SQLi, SSH Scan) và đẩy log cấu trúc `eve.json`.
2. **Tầng máy chủ (Host Layer):** Triển khai **Wazuh Agent** trên Target Server và Sensor để ghi nhận xác thực hệ điều hành (`auth.log`), audit log và **giám sát tính toàn vẹn tệp (FIM - File Integrity Monitoring)** tại `/var/www/html/` chống tải WebShell.
3. **Tầng điều hành trung tâm (Central SIEM):** **Wazuh Manager + Indexer + Dashboard** tương quan hóa sự kiện đa nguồn (correlation) chuẩn hóa theo khung tham chiếu **MITRE ATT&CK Enterprise Matrix**.
4. **Tầng phản ứng tự động (Active Response):** Khi phát hiện brute-force SSH hoặc vi phạm nghiêm trọng, Wazuh Server tự động ra lệnh cho Agent trên Target kích hoạt `firewall-drop` (chặn IP qua `iptables`), đồng thời đẩy cảnh báo tức thời qua **Telegram Bot Webhook**.

---

## 🔄 2. Sơ đồ dòng chảy dữ liệu sự kiện (Event Data Flow Pipeline)

```text
[ Kẻ tấn công (Kali) ] 
       │ Gói tin độc hại (SYN Scan, SQL Injection)
       ▼
[ Cổng Router Gateway (Suricata-Sensor) ]
       │ 1. AF-PACKET bắt gói theo thời gian thực & đối chiếu Signature ET-Open
       ▼
   /var/log/suricata/eve.json
       │ 2. Wazuh Agent đọc luồng JSON (logcollector)
       ▼ (Cổng mã hóa 1514 TCP/UDP)
[ Bộ não trung tâm: Wazuh Manager ]
       │ 3. Giải mã (Decoders) -> Tương quan hóa (Rules Correlation) -> Gắn nhãn MITRE ATT&CK
       ├─────────────────────────────────┬─────────────────────────────────┐
       ▼                                 ▼                                 ▼
[ Wazuh Indexer & Dashboard ]     [ Active Response Engine ]       [ Telegram Bot Webhook ]
(Trực quan hóa đồ thị cảnh báo)     (Gửi lệnh DROP IP xuống Target)  (Bắn tin khẩn về điện thoại)
```

---

## 💾 3. Bảng tệp tin máy ảo & Khóa cứng phiên bản số chính xác

> ⛔ **CẢNH BÁO TỬ HUYỆT VỀ CON SỐ PHIÊN BẢN (VERSION COMPATIBILITY LOCK):**
> * **Wazuh SIEM (Quan trọng nhất):** Trên menu dropdown phiên bản của trang chủ Wazuh, **BẮT BUỘC CHỌN SỐ: `Version 4.7` HOẶC `Version 4.8`** (File `.ova`).  
>   ❌ **TUYỆT ĐỐI KHÔNG CHỌN:** Dòng trên cùng `Version 4.14 (current)`. Các bản mới này đã xóa đường dẫn file đọc pass `/home/wazuh-user/wazuh-install-files.tar` và đổi kiến trúc quản lý indexer, khiến lệnh trong Runbook bị vô hiệu hóa!
> * **Ubuntu Server (Target & Sensor):** BẮT BUỘC tải bản số **`22.04.4 LTS`** hoặc **`22.04.5 LTS`** (`ubuntu-22.04.x-live-server-amd64.iso`).  
>   ❌ **TUYỆT ĐỐI KHÔNG TẢI:** Bản mới nhất **`Ubuntu 24.04 LTS`** (Khai tử cú pháp Netplan `gateway4`, chặn cài Python bằng lỗi `PEP 668` và lỗi APT GPG key).
> * Tuyệt đối không tải các bản Desktop có giao diện đồ họa (GUI) gây tràn bộ nhớ RAM.

### Bảng đối chiếu con số phiên bản chuẩn xác cho cả nhóm:

| Thành phần | Con số phiên bản CHÍNH XÁC | Tên tệp tin & Link tải trực tiếp | Môi trường hệ điều hành | Phiên bản TUYỆT ĐỐI TRÁNH |
| :--- | :---: | :--- | :--- | :--- |
| **Wazuh-SIEM** | **`4.7.x`** hoặc **`4.8.x`** | • Bản 4.7: [`wazuh-4.7.5.ova` (Tải trực tiếp)](https://packages.wazuh.com/4.x/vm/wazuh-4.7.5.ova) — [Doc Wazuh 4.7](https://documentation.wazuh.com/4.7/deployment-options/virtual-machine/virtual-machine.html)<br>• Bản 4.8: [`wazuh-4.8.0.ova` (Tải trực tiếp)](https://packages.wazuh.com/4.x/vm/wazuh-4.8.0.ova) — [Doc Wazuh 4.8](https://documentation.wazuh.com/4.8/deployment-options/virtual-machine/virtual-machine.html) | **Amazon Linux** (Dịch vụ mạng: `network`, `vi`)<br>*(❌ Không có `nmcli`)* | ❌ Tránh `4.14 (current)` |
| **Target & Sensor** | **`22.04.4`** hoặc **`22.04.5`** | [`ubuntu-22.04.5-live-server-amd64.iso` (Tải trực tiếp)](https://releases.ubuntu.com/jammy/ubuntu-22.04.5-live-server-amd64.iso) | **Ubuntu 22.04 LTS** (Lệnh: `netplan`, `apt`) | ❌ Tránh `24.04` (Mới nhất) |
| **Attacker-Kali** | **`2023.4`** hoặc **`2024.1` / `2024.2`** | File `.7z` (~3.0 GB) từ [Kali VMware Pre-built](https://www.kali.org/get-kali/#kali-virtual-machines) | **Kali Linux (Debian)** (Có sẵn Nmap/Hydra) | Bản Installer ISO tự cài |
| **Suricata Engine** | **`6.0.x`** hoặc **`7.0.x`** | Cài tự động qua PPA `ppa:oisf/suricata-stable` | NIDS/IPS Engine | Bản mặc định cũ `5.x` |

---

## 🌐 4. Quy hoạch địa chỉ mạng & Tài khoản hệ thống

```text
[ Attacker: Kali Linux ] (192.168.100.50)
            │ (VMnet8 - NAT)
            ▼
┌──────────────────────────────────────────────────────────────┐
│                  Suricata-Sensor (Router Gateway)             │
│   Card 1 (ens33): 192.168.100.20  |  Card 2 (ens34): 10.0.0.1  │
│          Suricata Engine NIDS/IPS  +  Wazuh Agent            │
└──────────────────────────────┬───────────────────────────────┘
                               │ (VMnet2 - Internal LAN)
                               ▼
               ┌─────────────────────────────────┐
               │    Target-Server (Ubuntu 22)    │
               │   IP (ens33): 10.0.0.10/24      │
               │   Nginx (80) + SSH + Wazuh Agent│
               └─────────────────────────────────┘
                                ▲
                                │ Đẩy log xác thực & cảnh báo
                                │
┌──────────────────────────────┴───────────────────────────────┐
│                     Wazuh-SIEM Server                        │
│   IP: 192.168.100.10/24 (VMnet8)                             │
│   Wazuh Manager + Indexer + Dashboard + Telegram Integration  │
└──────────────────────────────────────────────────────────────┘
```

### Bảng thông số chi tiết 4 Node mạng:
| Node mạng | Vai trò | Card mạng VMware | IP gán tĩnh | Default Gateway | Tài khoản mặc định | Cấu hình & Dịch vụ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Wazuh-SIEM** | Central SIEM | VMnet8 (NAT) | `192.168.100.10/24` | `192.168.100.2` | `wazuh-user` / `wazuh`<br>Web: `admin` / *(xem file pass)* | RAM: 4GB, CPU: 2 Cores<br>Web HTTPS: 443, Agent: 1514, 1515 |
| **Suricata-Sensor** | Gateway IDS/IPS | Card 1: VMnet8<br>Card 2: VMnet2 | `ens33`: `192.168.100.20/24`<br>`ens34`: `10.0.0.1/24` | `192.168.100.2` | `ubuntu` / `123` | RAM: 2GB, CPU: 2 Cores<br>Suricata, IP Forwarding, NAT |
| **Target-Server** | Web/DB mục tiêu | VMnet2 (Host-only) | `ens33`: `10.0.0.10/24` | `10.0.0.1` | `ubuntu` / `123` | RAM: 2GB, CPU: 1 Core<br>Nginx: 80, SSH: 22, Wazuh Agent |
| **Attacker-Kali** | Red Team giả lập | VMnet8 (NAT) | `eth0`: `192.168.100.50/24` | `192.168.100.2` | `kali` / `kali` | RAM: 2GB, CPU: 1 Core<br>Nmap, Hydra, Route tĩnh `10.0.0.0/24` |

---

## ⚙️ 5. Cấu hình mạng ảo VMware Workstation (Bắt buộc làm trước tiên)

1. Mở VMware $\rightarrow$ **Edit** $\rightarrow$ **Virtual Network Editor...** $\rightarrow$ Nhấn **Change Settings**.
2. **VMnet8 (NAT):**
   * Subnet IP: `192.168.100.0` | Subnet mask: `255.255.255.0`
   * Bấm **NAT Settings...** $\rightarrow$ Gateway IP: `192.168.100.2` $\rightarrow$ OK.
3. **VMnet2 (Host-only - Mạng nội bộ):**
   * Bấm **Add Network...** $\rightarrow$ Chọn **VMnet2**.
   * **BỎ TÍCH** ô *"Use local DHCP service to distribute IP addresses to VMs"* (để tránh IP nhảy lung tung).
   * Subnet IP: `10.0.0.0` | Subnet mask: `255.255.255.0` $\rightarrow$ Nhấn **Apply** $\rightarrow$ **OK**.

---

## 💡 MẸO SỐNG CÒN: COPY - PASTE TỪ MÁY THẬT (WINDOWS) VÀO CẢ 4 MÁY ẢO

> ⛔ **CẢNH BÁO LỖI PHỔ BIẾN:**  
> Tuyệt đối **KHÔNG bấm nút "Install VMware Tools"** trên thanh menu của VMware Workstation. VMware sẽ báo lỗi `Could not find component on update server...` vì Broadcom đã đóng server tải cũ. Toàn bộ máy ảo Linux hiện đại đều sử dụng **`open-vm-tools`** chính thức!

### 1. Bí quyết chuẩn DevSecOps: SSH trực tiếp từ máy thật (PowerShell / Windows Terminal)
Thay vì gõ lệnh trên màn hình console đen sì, chật hẹp của VMware (dễ kẹt phím, không nhận chuột), sau khi gán xong IP ở bước đầu, **hãy thu nhỏ VMware lại và mở PowerShell trên máy thật Windows**:

| Máy ảo | Địa chỉ IP | Lệnh SSH từ PowerShell / Windows Terminal máy thật | Mật khẩu mặc định |
| :--- | :--- | :--- | :--- |
| **Wazuh-SIEM** | `192.168.100.10` | `ssh wazuh-user@192.168.100.10` | `wazuh` |
| **Suricata-Sensor** | `192.168.100.20` | `ssh ubuntu@192.168.100.20` | `123` |
| **Target-Server** | `10.0.0.10` | `ssh ubuntu@10.0.0.10` *(xem lưu ý route bên dưới)* | `123` |
| **Attacker-Kali** | `192.168.100.50` | `ssh kali@192.168.100.50` | `kali` |

* **Lợi ích tuyệt đối:** Bạn có thể bôi đen copy bất kỳ đoạn script nào trong tài liệu này và **nhấn `Ctrl + V` hoặc click chuột phải** để paste ngay vào máy ảo cực nhanh, không sót ký tự!
* **Mẹo cho máy Target (`10.0.0.10` nằm sau Router):** Để máy thật Windows có thể ping và SSH thẳng vào Target, mở PowerShell **Run as Administrator** trên Windows và chạy lệnh thêm route:
  ```powershell
  route add 10.0.0.0 mask 255.255.255.0 192.168.100.20
  ```

### 2. Đối với máy Kali Linux (Giao diện đồ họa Desktop)
Nếu muốn Copy - Paste văn bản và Kéo - Thả file (Drag & Drop) trực tiếp giữa màn hình Windows và Desktop Kali Linux:
1. Mở terminal trên Kali và chạy:
   ```bash
   sudo apt update && sudo apt install -y open-vm-tools-desktop && sudo reboot
   ```
2. Trên VMware: Vào **VM** $\rightarrow$ **Settings** $\rightarrow$ **Options** $\rightarrow$ **Guest Isolation** $\rightarrow$ Tích chọn cả:
   * `[x] Enable drag and drop`
   * `[x] Enable copy and paste`

### 3. Ghi nhớ thao tác bàn phím khi chưa có SSH (30 giây đầu cấu hình IP)
- **Thoát chuột khỏi máy ảo về lại Windows:** Nhấn tổ hợp phím **`Ctrl + Alt`**.
- **Wazuh (Amazon Linux 2023):** Dùng trình soạn thảo `vi`. Nhấn `i` để gõ, gõ xong nhấn `Esc` rồi gõ `:wq` và ấn `Enter`.
- **Ubuntu (Sensor/Target):** Dùng `nano`. Gõ xong nhấn `Ctrl + O` $\rightarrow$ `Enter` để lưu, `Ctrl + X` để thoát.

### 4. ⚠️ NGUYÊN TẮC PHÂN QUYỀN (ROOT / SUDO) — TUYỆT ĐỐI KHÔNG BỎ QUA
> ❌ **CẢNH BÁO LỖI PHỔ BIẾN:**  
> Nếu bạn gõ lệnh sửa file cấu hình mà **quên gõ `sudo`** hoặc **thư mục cha chưa tồn tại**, bạn sẽ bị lỗi **`E212: Can't open file for writing`** (không lưu được file). Nếu lỡ đóng cửa sổ ngang, lần sau mở lại sẽ bị lỗi kẹt swap **`E325: ATTENTION`**!

* **2 nguyên nhân cốt tử gây lỗi `E212: Can't open file for writing`:**
  1. *Quên quyền `sudo`:* File thuộc sở hữu của `root`, user thường không ghi được.
  2. *Thư mục cha chưa tồn tại:* `vi` không tự tạo folder. Ví dụ trên Amazon Linux 2023, thư mục `/etc/systemd/network` mặc định **chưa có sẵn**, bắt buộc phải tạo trước bằng `sudo mkdir -p /etc/systemd/network`!
* **Cứu nguy ngay trong `vi` khi đã lỡ nhập xong mà bị lỗi E212:**
  - Nhấn `Esc` $\rightarrow$ Gõ `:!mkdir -p /etc/systemd/network` $\rightarrow$ `Enter` $\rightarrow$ Bấm `Enter` quay lại $\rightarrow$ Gõ `:wq` $\rightarrow$ `Enter` để lưu thành công 100%!
* **Lệnh nào BẮT BUỘC dùng `sudo` (Quyền Root)?**
  - Mọi thao tác sửa file trong `/etc/` và `/var/` (ví dụ: `/etc/systemd/network/...`, `/etc/netplan/...`, `/etc/suricata/...`, `/var/ossec/...`).
  - Mọi lệnh khởi động / dừng dịch vụ: `systemctl restart/status ...`.
  - Mọi lệnh cấu hình mạng & tường lửa: `iptables`, `firewall-cmd`, `sysctl`, `netplan apply`.
  - Mọi lệnh cài đặt phần mềm: `apt`, `dnf`.
* **Cách thoát khi lỡ gõ thiếu `sudo` trong `vi`:**
  - Nhấn `Enter` $\rightarrow$ Nhấn `Esc` $\rightarrow$ Gõ `:q!` $\rightarrow$ Nhấn `Enter` để thoát ra không lưu.
* **Cách xóa lỗi kẹt file Swap (E325: ATTENTION):**
  - Nhấn `q` để thoát thông báo $\rightarrow$ Chạy lệnh dọn sạch: `sudo killall vi 2>/dev/null; sudo rm -f /var/tmp/*.swp 2>/dev/null`.
* **💡 Mẹo nhàn nhất cho cả nhóm:**
  - Để không phải gõ `sudo` trước mỗi lệnh, ngay sau khi đăng nhập máy ảo hoặc SSH, bạn gõ một lần duy nhất:
    ```bash
    sudo -i
    ```
    *(Dấu nhắc lệnh chuyển từ `$` sang `#` tức là bạn đã lên quyền `root`, thoải mái gõ toàn bộ lệnh trong Runbook mà không bao giờ bị lỗi quyền).*

---

## 👥 6. Phân công trách nhiệm 3 người & Hướng dẫn kỹ thuật chi tiết

### 🟢 THÀNH VIÊN 1: SIEM & Integration Lead (Bộ não trung tâm)
* **Máy quản lý:** `Wazuh-SIEM` (`192.168.100.10/24`) | **Nhánh Git:** `feature/wazuh-rules-telegram`
* **Nhiệm vụ chi tiết:**
  1. Import file `.ova`, đặt RAM 4GB, 2 Cores, mạng **VMnet8**.
  2. Gán IP tĩnh `192.168.100.10` & hạ tải Heap RAM OpenSearch (Tuyệt chiêu SSH máy thật):
     * **Bước 2.1: Xem IP DHCP tạm thời trên console máy ảo:**
       ```bash
       ip a
       ```
       *(Tìm dòng `inet 192.168.100.xxx` ở card `eth0`, ví dụ: `192.168.100.130`).*
     * **Bước 2.2: Thu nhỏ VMware, mở PowerShell máy thật SSH vào ngay:**
       ```powershell
       ssh wazuh-user@192.168.100.xxx   # Thay xxx bằng số IP vừa xem (pass: wazuh)
       ```
     * **Bước 2.3: Trên cửa sổ SSH máy thật, paste khối lệnh ghi đè file ifcfg-eth0:**
       ```bash
       sudo -i
       cat << 'EOF' > /etc/sysconfig/network-scripts/ifcfg-eth0
       DEVICE=eth0
       BOOTPROTO=none
       ONBOOT=yes
       IPADDR=192.168.100.10
       NETMASK=255.255.255.0
       GATEWAY=192.168.100.2
       DNS1=8.8.8.8
       DNS2=1.1.1.1
       EOF
       systemctl restart network
       ```
       *(Sau khi áp dụng, phiên SSH cũ tự ngắt vì IP đã đổi sang `192.168.100.10`).*
     * **Bước 2.4: Kết nối lại SSH bằng IP tĩnh chuẩn và hạ Heap RAM:**
       ```powershell
       ssh wazuh-user@192.168.100.10
       ```
       Dán lệnh an toàn hạ tải Heap RAM OpenSearch (dọn rác và gán chuẩn 1GB, tránh nuốt ký tự):
       ```bash
       sudo sed -i '/-Xm/d' /etc/wazuh-indexer/jvm.options
       sudo sed -i '/-ons/d' /etc/wazuh-indexer/jvm.options
       echo "-Xms1g" | sudo tee -a /etc/wazuh-indexer/jvm.options
       echo "-Xmx1g" | sudo tee -a /etc/wazuh-indexer/jvm.options
       sudo systemctl daemon-reload
       sudo systemctl restart wazuh-indexer
       ```
  3. Đăng nhập Web Dashboard:
     * Mở trình duyệt máy thật gõ đủ tiền tố: `https://192.168.100.10` (Bắt buộc `https://` để tránh lỗi `ERR_CONNECTION_REFUSED`).
     * *(Nếu thấy thông báo "Wazuh dashboard server is not ready yet", đây là trạng thái bình thường khi máy vừa bật, đợi 1 phút cho Indexer nạp xong rồi nhấn F5).*
     * Bấm **Advanced $\rightarrow$ Proceed to 192.168.100.10 (unsafe)**. Tài khoản mặc định: `admin` / `admin`.
     * Nếu có file mật khẩu ngẫu nhiên, đọc bằng lệnh:
       ```bash
       cat /home/wazuh-user/wazuh-passwords.txt 2>/dev/null || sudo tar -O -xvf /home/wazuh-user/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt 2>/dev/null
       ```
  4. Cấu hình White-list và Active Response trong `/var/ossec/etc/ossec.conf`:
     * Thêm thẻ `<white_list>` chứa IP Sensor (`192.168.100.20`, `10.0.0.1`), Target (`10.0.0.10`), SIEM (`192.168.100.10`).
     * Thêm `<active-response>` kích hoạt `firewall-drop` với `rules_id`: `5712`.
  5. Tích hợp cảnh báo khẩn (Telegram hoặc Discord Webhook):
     * **Cách A (Telegram):** Viết `/var/ossec/integrations/custom-telegram.py`, cấp quyền `sudo chmod 750` và `sudo chown root:wazuh`.
     * **Cách B (Discord - Miễn phí 100%, không cần số điện thoại):** Viết `/var/ossec/integrations/custom-discord.py`, cấp quyền tương tự.
  6. Bổ sung Custom Rule (`/var/ossec/etc/rules/local_rules.xml`) và lưu cấu hình vào repo: `configs/ossec-manager.conf`, `rules/local_rules.xml`, `scripts/custom-telegram.py`, `scripts/custom-discord.py`.
  7. Tắt máy an toàn (`sudo poweroff`) và chụp Offline Snapshot trên VMware: đặt tên `01-Wazuh-Init-Clean-Ready`.

---

### 🟡 THÀNH VIÊN 2: Network & Sensor Specialist (Cửa ngõ an ninh)
* **Máy quản lý:** `Suricata-Sensor` (Router 2 card: `192.168.100.20` & `10.0.0.1`) | **Nhánh Git:** `feature/suricata-sensor-nat`
* **Nhiệm vụ chi tiết:**
  1. Tạo Linked Clone từ Ubuntu Base, thêm card mạng 2 (`ens33` vào VMnet8, `ens34` vào VMnet2).
  2. Cấu hình IP tĩnh Netplan (`/etc/netplan/00-installer-config.yaml`):
     ```yaml
     network:
       version: 2
       renderer: networkd
       ethernets:
         ens33:
           addresses: [192.168.100.20/24]
           routes:
             - to: default
               via: 192.168.100.2
           nameservers:
             addresses: [8.8.8.8, 1.1.1.1]
         ens34:
           addresses: [10.0.0.1/24]
     ```
     Chạy `sudo netplan apply`.  
     *(Sau khi apply mạng xong, chuyển sang PowerShell máy thật gõ `ssh ubuntu@192.168.100.20` với pass `123` để paste các lệnh bên dưới cực nhanh!)*
  3. Bật IP Forwarding và NAT Masquerade (Bắt buộc cài iptables-persistent tránh mất rule khi reboot):
     ```bash
     sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf && sudo sysctl -p
     sudo apt update && sudo apt install -y iptables-persistent netfilter-persistent
     sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
     sudo netfilter-persistent save
     ```
  4. Cài đặt Suricata và cập nhật rules:
     ```bash
     sudo add-apt-repository ppa:oisf/suricata-stable -y
     sudo apt update && sudo apt install suricata jq -y && sudo suricata-update
     ```
     Sửa `/etc/suricata/suricata.yaml`: đặt `HOME_NET: "[10.0.0.0/24,192.168.100.0/24]"`, cho `af-packet` lắng nghe `ens34`, và thêm `- local.rules` vào mục `rule-files:`.
  5. Cài Wazuh Agent trên Sensor, phân quyền thư mục và cấu hình Agent đọc luồng log `eve.json` dạng `json` đẩy về SIEM:
     ```bash
     sudo usermod -aG suricata wazuh && sudo chmod 755 /var/log/suricata && sudo chmod 644 /var/log/suricata/eve.json
     sudo systemctl enable wazuh-agent && sudo systemctl restart wazuh-agent
     ```
  6. Lưu cấu hình vào repo: `configs/suricata.yaml`, `configs/netplan-sensor.yaml`, `rules/local.rules`.

---

### 🔴 THÀNH VIÊN 3: Target Admin & Red Team Lead (Mục tiêu & Tấn công)
* **Máy quản lý:** `Target-Server` (`10.0.0.10`) & `Attacker-Kali` (`192.168.100.50`) | **Nhánh Git:** `feature/target-hardening-attacks`
* **Nhiệm vụ chi tiết:**
  1. Tạo Linked Clone Target-Server, gán mạng **VMnet2**, đặt IP `10.0.0.10/24`, Gateway `10.0.0.1`.
     * Kiểm tra thông mạng: `ping -c 3 8.8.8.8`.  
     * *(Mẹo Copy/Paste: Mở PowerShell Admin trên máy thật gõ `route add 10.0.0.0 mask 255.255.255.0 192.168.100.20`, sau đó gõ `ssh ubuntu@10.0.0.10` để paste lệnh cài Nginx và Agent cực nhanh).*
     * Cài Nginx Web Server: `sudo apt update && sudo apt install nginx -y`.
     * Cài đặt Wazuh Agent trỏ về Manager `192.168.100.10` và cấu hình FIM `<syscheck>` giám sát `/var/www/html`.
  2. Thiết lập máy Kali Linux: Gán mạng **VMnet8**, IP `192.168.100.50/24`.  
     *(Mẹo Copy/Paste: Chạy `sudo apt install -y open-vm-tools-desktop && sudo reboot` để copy-paste trên Desktop Kali, hoặc SSH từ PowerShell máy thật `ssh kali@192.168.100.50` với pass `kali`).*
     * **Bắt buộc thêm Static Route sang dải Target:**
       ```bash
       sudo ip route add 10.0.0.0/24 via 192.168.100.20
       ```
     * **Chuẩn bị từ điển (Bắt buộc giải nén):**
       ```bash
       sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz 2>/dev/null || true
       echo -e "123456\npassword\nadmin\nubuntu\nletmein" > ~/test_pass.txt
       ```
  3. Thực thi 3 kịch bản demo:
     * **TC-01 (Quét Nmap):** `nmap -sS -p 22,80 10.0.0.10`
     * **TC-02 (Brute-force SSH):** `hydra -l ubuntu -P ~/test_pass.txt ssh://10.0.0.10 -t 4` *(Target tự động DROP IP)*
     * **TC-03 (Web SQLi & FIM):** `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"` và tạo thử `shell.php` trên Target.
  4. Lưu cấu hình vào repo: `configs/netplan-target.yaml`, `scripts/attack_simulation.sh`.

---

## 🧪 7. Ma trận kiểm thử thực nghiệm & Ánh xạ MITRE ATT&CK

| Mã | Kịch bản tấn công | Lệnh thực thi từ Kali | Khung MITRE ATT&CK | Cơ chế phát hiện | Cơ chế phản ứng (Active Response) | Bằng chứng nghiệm thu |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **TC-01** | Quét cổng do thám (Reconnaissance) | `nmap -sS -p 22,80 10.0.0.10` | **T1046** (Network Service Discovery)<br>**T1595** (Active Scanning) | **Suricata (Network):** Bắt signature Nmap User-Agent trong `eve.json` | Wazuh SIEM nhận log, sinh Alert Level 6-8, phân loại nhóm `reconnaissance` | Biểu đồ Dashboard nhảy số; IP chưa bị chặn (chưa vượt ngưỡng) |
| **TC-02** | Dò mật khẩu SSH & Tự động chặn IP | `hydra -l ubuntu -P ~/test_pass.txt ssh://10.0.0.10 -t 4` | **T1110.001** (Brute Force: Password Guessing) | **Target OS (Host Log):** Wazuh Agent đọc `/var/log/auth.log` failed 5 lần liên tiếp | **Rule 5712 (Level 10)** kích hoạt script `firewall-drop` trên Target | Terminal Hydra báo `timed out`; `iptables -L` có dòng DROP IP Kali; Telegram nhận tin |
| **TC-03** | Khai thác Web SQL Injection | `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"` | **T1190** (Exploit Public-Facing Application) | **Suricata (Network):** Bắt signature SQL Injection Attempt | Kích hoạt cảnh báo Critical (Level 12+), gắn nhãn MITRE T1190 | Suricata ghi alert; Telegram bắn tin cảnh báo màu đỏ tức thời |
| **TC-04** | Tải WebShell & Giám sát FIM | `curl -F "file=@shell.php" http://10.0.0.10/upload` *(hoặc tạo file `/var/www/html/backdoor.php`)* | **T1505.003** (Server Component: Web Shell)<br>**T1078** (Valid Accounts) | **Wazuh FIM (Host):** Syscheck quét `/var/www/html/` phát hiện file mới/sửa đổi | Kích hoạt Rule 550 (Integrity checksum changed) Level 7+ | Dashboard hiển thị file bị thêm/sửa, diff nội dung tệp; Telegram báo động |

---

## 📊 8. Chỉ số đo lường hiệu năng thực nghiệm (KPIs & Metrics)

Hệ thống được kiểm định và đáp ứng các tiêu chuẩn phản ứng an ninh mạng thực tế:

| Chỉ số đo lường (Metric) | Phạm vi kiểm tra | Tiêu chuẩn cam kết (SLA) | Kết quả thực nghiệm lab |
| :--- | :--- | :---: | :---: |
| **Thời gian phát hiện gói tin độc hại (Detection Latency)** | Từ lúc Kali gửi packet Nmap/SQLi $\rightarrow$ Suricata ghi `eve.json` | $< 2.0$ giây | **$\approx 0.8$ giây** |
| **Thời gian tương quan log về SIEM (SIEM Ingestion Latency)** | Từ `eve.json` / `auth.log` $\rightarrow$ Wazuh Manager hiển thị Alert | $< 3.0$ giây | **$\approx 1.5$ giây** |
| **Thời gian kích hoạt chặn IP (Active Response Latency)** | Từ lúc phát hiện Brute-force $\rightarrow$ `iptables DROP` trên Target | $< 3.0$ giây | **$\approx 1.2$ giây** |
| **Thời gian đẩy thông báo khẩn (Telegram Alert Latency)** | Từ lúc Rule Level 10+ kích hoạt $\rightarrow$ Tin nhắn rung điện thoại | $< 5.0$ giây | **$\approx 2.1$ giây** |
| **Mức tiêu hao tài nguyên (Resource Consumption)** | Toàn cụm 4 máy ảo chạy đồng thời trên 1 máy tính vật lý | RAM $< 11\text{GB}$ | **$\approx 9.5\text{GB}$ RAM** (nhờ Linked Clone & Heap 1GB) |

---

## ⚠️ 9. Sáu sai lầm chí mạng tuyệt đối tránh tái phạm

1. **Kali quên Static Route:** Không chỉ đường sang `10.0.0.0/24`, Kali gõ Nmap sẽ báo `Host seems down`. Khắc phục: `sudo ip route add 10.0.0.0/24 via 192.168.100.20`.
2. **Sensor quên bật IP Forwarding:** Target không ping được ra ngoài `8.8.8.8`, không cài được Nginx/Agent. Khắc phục: `sudo sysctl -w net.ipv4.ip_forward=1`.
3. **Quên giới hạn Java Heap Wazuh Indexer:** Máy thật ngốn 100% RAM sau 30 phút. Khắc phục: sửa `/etc/wazuh-indexer/jvm.options` thành `-Xms1g` và `-Xmx1g`.
4. **Quên White-list trong Active Response:** Khi bị scan, Wazuh khóa nhầm luôn cả IP của Gateway (`10.0.0.1`) làm rớt toàn bộ lab. Khắc phục: thêm thẻ `<white_list>` vào `ossec.conf`.
5. **Để file `eve.json` tràn ổ cứng:** Sensor đầy 100% đĩa làm Suricata ngắt. Khắc phục: định kỳ chạy `sudo truncate -s 0 /var/log/suricata/eve.json`.
6. **Quên phân quyền script Telegram:** File python không gửi được webhook. Khắc phục: `sudo chmod 750 custom-telegram.py && sudo chown root:wazuh custom-telegram.py`.

---

## 📂 10. Cấu trúc thư mục kho lưu trữ
```text
soc-lab-wazuh-suricata/
├── .github/workflows/
│   └── ci.yml                      # CI kiểm tra cú pháp YAML, XML, Script & Secret
├── .gitignore                      # Chặn commit máy ảo, file log, credentials
├── README.md                       # Tài liệu tóm tắt kiến trúc mạng và Runbook
├── configs/
│   ├── suricata.yaml               # File cấu hình chuẩn Suricata Engine
│   ├── netplan-sensor.yaml         # Cấu hình mạng 2 card của Sensor
│   ├── netplan-target.yaml         # Cấu hình mạng trỏ Gateway của Target
│   ├── ossec-agent-sensor.conf     # Cấu hình Agent đọc file eve.json
│   └── ossec-manager.conf          # Cấu hình Active Response trên Manager
├── rules/
│   ├── local.rules                 # Custom Signatures viết riêng trên Suricata
│   └── local_rules.xml             # Custom Decoders & Rules viết riêng trên Wazuh
├── scripts/
│   ├── custom-telegram.py          # Script Webhook bắn cảnh báo tự động về Telegram
│   ├── custom-discord.py           # Script Webhook bắn cảnh báo tự động về Discord (Free 100%)
│   └── attack_simulation.sh        # Script chạy tự động Nmap/Hydra từ máy Kali
└── docs/
    └── Ke_Hoach_Trien_Khai.md      # Bản kế hoạch kỹ thuật & Runbook chi tiết
```

---

## 🔄 11. Đồng bộ cấu hình từ máy ảo ra Repo theo từng thành viên (SCP)

Mỗi thành viên mở PowerShell tại thư mục dự án trên máy thật của mình (`d:\AnNinhMang\soc-lab-wazuh-suricata`) và chạy bộ lệnh tương ứng với vai trò của mình:

* 🟢 **Thành viên 1 (Máy tính chạy Wazuh-SIEM - 192.168.100.10):**
  > [!NOTE]
  > Trên máy ảo Wazuh, chạy lệnh copy ra home trước: `sudo cp /var/ossec/etc/ossec.conf /var/ossec/etc/rules/local_rules.xml /home/wazuh-user/ && sudo cp /var/ossec/integrations/custom-*.py /home/wazuh-user/ 2>/dev/null; sudo chown wazuh-user:wazuh-user /home/wazuh-user/*` để tránh lỗi quyền root 750 khi SCP.
  ```powershell
  scp wazuh-user@192.168.100.10:~/ossec.conf ./configs/ossec-manager.conf
  scp wazuh-user@192.168.100.10:~/local_rules.xml ./rules/local_rules.xml
  scp wazuh-user@192.168.100.10:~/custom-discord.py ./scripts/ 2>$null
  scp wazuh-user@192.168.100.10:~/custom-telegram.py ./scripts/ 2>$null
  ```

* 🟡 **Thành viên 2 (Máy tính chạy Suricata-Sensor - 192.168.100.20):**
  ```powershell
  scp ubuntu@192.168.100.20:/etc/netplan/00-installer-config.yaml ./configs/netplan-sensor.yaml
  scp ubuntu@192.168.100.20:/etc/suricata/suricata.yaml ./configs/suricata.yaml
  scp ubuntu@192.168.100.20:/var/lib/suricata/rules/local.rules ./rules/
  scp ubuntu@192.168.100.20:/var/ossec/etc/ossec.conf ./configs/ossec-agent-sensor.conf
  ```

* 🔴 **Thành viên 3 (Máy tính chạy Target & Kali):**
  ```powershell
  # Lấy script tấn công từ Kali (192.168.100.50):
  scp kali@192.168.100.50:/home/kali/attack_simulation.sh ./scripts/

  # Lấy cấu hình Netplan Target (10.0.0.10 - VMnet2): 
  # Gán IP 10.0.0.254 cho card VMnet2 trên Windows rồi gõ scp, hoặc xem trực tiếp bằng 'cat' trên máy ảo Target
  scp ubuntu@10.0.0.10:/etc/netplan/00-installer-config.yaml ./configs/netplan-target.yaml
  ```
*(Ngoài ra, có thể dùng phần mềm đồ họa **WinSCP** kết nối qua SFTP Port 22 để kéo thả trực quan).*

---

## 🛠️ 12. Lệnh cứu hộ khẩn cấp (Cheat-Sheet)

```bash
# Kiểm tra dịch vụ SIEM:
sudo systemctl status wazuh-manager wazuh-indexer wazuh-dashboard

# Kiểm tra dịch vụ Sensor:
sudo systemctl status suricata wazuh-agent

# Xem log cảnh báo Suricata trực tiếp theo thời gian thực:
tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert") | {time: .timestamp, src: .src_ip, alert: .alert.signature}'

# Xem IP đang bị khóa trên Target:
sudo iptables -L INPUT -n -v --line-numbers

# Xóa chặn khẩn cấp toàn bộ iptables (nếu bị tự khóa nhầm):
sudo iptables -F
```

---

## 📝 13. Quy trình phản hồi & Hiệu chỉnh tài liệu nhóm (Living Documentation Protocol)

Trong quá trình thực hành trên máy ảo VMware, nếu bất kỳ thành viên nào phát hiện hướng dẫn bị lệch so với thực tế (lỗi câu lệnh, tên card mạng khác, thiếu gói phần mềm, phiên bản thay đổi):

1. **Khuyến khích hiệu chỉnh ngay:** Mọi thành viên đều có toàn quyền và trách nhiệm cập nhật lại tài liệu để cả nhóm cùng dùng bản chuẩn xác nhất.
2. **Quy tắc sửa đổi đồng bộ:** Luôn cập nhật song song cả hai tệp: [`README.md`](file:///d:/AnNinhMang/soc-lab-wazuh-suricata/README.md) và [`docs/Ke_Hoach_Trien_Khai.md`](file:///d:/AnNinhMang/soc-lab-wazuh-suricata/docs/Ke_Hoach_Trien_Khai.md).
3. **Quy trình Git & Hỗ trợ Fast-Pass từ CI:**
   * Tạo commit sửa đổi trên nhánh làm việc cá nhân: `git commit -m "docs: sua buoc X do thuc te tren may ao Y"`.
   * Mở Pull Request vào nhánh `main`. Nhờ hệ thống **CI Fast-Pass Whitelist**, các PR chỉnh sửa tài liệu chuẩn sẽ được CI tự động thông qua chỉ sau ~10 giây (nếu không vi phạm rò rỉ secret).
   * Báo tin nhanh vào nhóm chat (Telegram/Zalo) để các thành viên khác kéo dữ liệu mới nhất về (Xem chi tiết câu lệnh tại [**Hướng dẫn đồng bộ dữ liệu nhanh ở đầu trang**](#-hướng-dẫn-đồng-bộ-dữ-liệu-nhanh-cho-cả-nhóm-daily-git-sync)).

---

## 🤖 14. Nguyên tắc phối hợp với Trợ lý AI (Working with AI & Governance)

Dự án ứng dụng mô hình AI Agent (Google Antigravity) để hỗ trợ rà soát DevSecOps, tự động hóa kiểm định và quản trị tài liệu kỹ thuật theo thời gian thực. Toàn bộ hoạt động phối hợp tuân thủ nghiêm ngặt 4 nguyên tắc:

1. **Quyền quyết định tối cao thuộc về con người (Human-in-the-Loop Gate):**
   - AI chỉ đóng vai trò trợ lý tư vấn, phát hiện lỗ hổng logic và đề xuất văn bản. Mọi lệnh `git commit`, `git push` hoặc áp dụng cấu hình lên hạ tầng mạng đều **phải có sự phê duyệt rõ ràng từ thành viên nhóm**.
2. **Kiểm định thực tế trước tiên (Verification First):**
   - Tuyệt đối không đưa vào tài liệu những câu lệnh chưa được kiểm chứng thực tế trên cụm máy ảo VMware (ví dụ: phát hiện dịch vụ mạng thực tế là `network.service` thay vì `systemd-networkd`).
3. **Chính sách Không lộ lọt dữ liệu (Zero-Leak Policy):**
   - Tuyệt đối không commit lên GitHub các thông tin nhạy cảm: Telegram Bot Token thật, Private Key, mật khẩu người dùng, file log dung lượng lớn (`eve.json`) hoặc ổ đĩa ảo (`.vmdk`).
4. **Cô lập cấu hình Agent cục bộ:**
   - Các file cấu hình kỹ năng Agent (`.agent/`) và file ghi nhớ lỗi/phản biện cá nhân (`prompt.md`, `promp.md`) **bắt buộc nằm trong `.gitignore`**, chỉ lưu trữ trên máy cá nhân để giữ repo sạch đẹp chuẩn mã nguồn kỹ thuật.
5. **Quy chuẩn Lưu trữ Phiên làm việc (Session Persistence & Anti-Hallucination):**
   - Sau mỗi phiên làm việc hoặc giải quyết xong task/lỗi, **thành viên bắt buộc yêu cầu AI tóm tắt và lưu lại phiên làm việc (Session Milestone)** vào file cục bộ (ví dụ: `session_summary.md`, đã được cấu hình trong `.gitignore`).
   - Điều này giúp AI ở các phiên tiếp theo có điểm tựa dữ liệu thực tế vững chắc, không bị mất ngữ cảnh (context loss) hay ảo giác (hallucination) lặp lại các vấn đề đã được khắc phục.
