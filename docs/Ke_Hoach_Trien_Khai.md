# KẾ HOẠCH TRIỂN KHAI KỸ THUẬT, QUẢN TRỊ GITHUB & RUNBOOK VẬN HÀNH DỰ PHÒNG

## ĐỒ ÁN MÔN HỌC: AN NINH MẠNG
**Đề tài:** Xây dựng hệ thống giám sát an ninh mạng tập trung kết hợp SIEM và IDS/IPS  
**Cơ cấu nhóm:** 03 thành viên  
**Đối tượng sử dụng:** Toàn bộ thành viên nhóm dự án (Lưu trữ cục bộ làm tài liệu chuẩn thực hiện, đối phó sự cố và chuẩn bị bảo vệ)

---

## MỤC LỤC
1. [Mục tiêu Kỹ thuật & Phạm vi Hệ thống](#1-mục-tiêu-kỹ-thuật--phạm-vi-hệ-thống)
2. [Bảng Tệp Tin Cần Tải Về Máy Tính](#2-bảng-tệp-tin-cần-tải-về-máy-tính)
3. [Thông số Kỹ thuật Chuẩn & Quy hoạch Địa chỉ Mạng](#3-thông-số-kỹ-thuật-chuẩn--quy-hoạch-địa-chỉ-mạng)
4. [Hướng Dẫn Thiết Lập Máy Ảo Chi Tiết Trên VMware](#4-hướng-dẫn-thiết-lập-máy-ảo-chi-tiết-trên-vmware)
5. [Quy chuẩn Quản trị Kho lưu trữ GitHub Nhóm](#5-quy-chuẩn-quản-trị-kho-lưu-trữ-github-nhóm)
6. [Cơ Cấu Nhóm 3 Người & Phân Công Chi Tiết (RACI Matrix)](#6-cơ-cấu-nhóm-3-người--phân-công-chi-tiết-raci-matrix)
7. [Những Điều Cần Lưu Ý & Sai Lầm Chí Mạng Tuyệt Đối Tránh Tái Phạm](#7-những-điều-cần-lưu-ý--sai-lầm-chí-mạng-tuyệt-đối-tránh-tái-phạm)
8. [Lộ Trình Triển Khai Từng Sprint (1 - 4)](#8-lộ-trình-triển-khai-từng-sprint-1---4)
9. [Hướng Dẫn Cấu Hình Hệ Thống Chi Tiết (Step-by-Step Runbook)](#9-hướng-dẫn-cấu-hình-hệ-thống-chi-tiết-step-by-step-runbook)
10. [Kịch Bản Kiểm Thử Thực Nghiệm Tấn Công - Phòng Thủ](#10-kịch-bản-kiểm-thử-thực-nghiệm-tấn-công---phòng-thủ)
11. [Chiến Lược Vấn Đáp & Bảo Vệ Đồ Án Nhóm 3 Người](#11-chiến-lược-vấn-đáp--bảo-vệ-đồ-án-nhóm-3-người)
12. [Runbook Xử Lý Sự Cố & Phục Hồi Thảm Họa (Troubleshooting)](#12-runbook-xử-lý-sự-cố--phục-hồi-thảm-họa-troubleshooting)
13. [Bộ Lệnh Cứu Hộ & Kiểm Tra Nhanh (Cheat-Sheet)](#13-bộ-lệnh-cứu-hộ--kiểm-tra-nhanh-cheat-sheet)

---

## 1. MỤC TIÊU KỸ THUẬT & PHẠM VI HỆ THỐNG

### 1.1. Mục tiêu cốt lõi
* **Tầng mạng (Network Layer):** Triển khai Suricata làm Network IDS/IPS, soi chiếu lưu lượng theo thời gian thực, nhận diện signature tấn công dò quét, dò mật khẩu, khai thác web và kích hoạt chặn gói tin độc hại.
* **Tầng máy chủ (Host Layer):** Triển khai Wazuh Agent trên các node dịch vụ để ghi nhận Event Log, Audit log, xác thực hệ thống, và giám sát tính toàn vẹn tệp (FIM).
* **Tầng điều hành trung tâm (Central SIEM):** Triển khai Wazuh Server, Indexer và Dashboard để thu thập tập trung, bóc tách trường (decoding), tương quan hóa sự kiện (correlation rules) theo khung tham chiếu MITRE ATT&CK.
* **Tầng phản ứng tự động (Active Response):** Thiết lập cơ chế tự động chặn IP qua `iptables` khi phát hiện hành vi xâm nhập vượt ngưỡng cho phép và đẩy thông báo tức thời qua Telegram Bot.

### 1.2. Giới hạn phạm vi
* Toàn bộ hệ thống chạy trên nền tảng ảo hóa **VMware Workstation Pro / Player**.
* Đảm bảo mọi thành viên có máy tính cấu hình từ **8GB – 16GB RAM** và dung lượng trống từ **25GB – 35GB** đều có thể cài đặt và vận hành mượt mà.
* Chế độ phân bổ linh hoạt:
  * *Phương án A (1 máy $\ge$ 16GB RAM):* Chạy toàn bộ 4 máy ảo trên 1 máy tính để làm demo.
  * *Phương án B (chia tải máy $\le$ 8GB RAM):* Thành viên 1 & 2 chạy Wazuh + Suricata; Thành viên 3 chạy Target + Kali, kết nối qua mạng Bridge hoặc cùng switch ảo.

---

## 2. BẢNG TỆP TIN CẦN TẢI VỀ MÁY TÍNH

Cả nhóm chỉ cần chuẩn bị đúng **3 tệp tin** này lưu trữ vào một thư mục chung hoặc USB (tuyệt đối không tải các bản Desktop có giao diện đồ họa gây tốn RAM):

| Tệp tin | Định dạng | Dung lượng | Nguồn tải chính thức | Mục đích sử dụng |
| :--- | :--- | :--- | :--- | :--- |
| **1. Wazuh Virtual Appliance** | `.ova` | ~4.5 GB | Trang chủ Wazuh (mục *Virtual Machine appliance / OVA*) | Dựng nhanh cụm SIEM Manager + Indexer + Dashboard |
| **2. Ubuntu Server 22.04 LTS** | `.iso` | ~2.5 GB | `releases.ubuntu.com/jammy/` (`ubuntu-22.04.x-live-server-amd64.iso`) | Cài máy Template gốc để clone ra Sensor và Target |
| **3. Kali Linux VMware Pre-built** | `.7z` | ~3.0 GB | `kali.org/get-kali/#kali-virtual-machines` (tab *VMware*) | Giải nén dùng ngay cho Red Team, không cần cài |

---

## 3. THÔNG SỐ KỸ THUẬT CHUẨN & QUY HOẠCH ĐỊA CHỈ MẠNG

Mọi thành viên bắt buộc tuân thủ đúng bảng thông số này để tránh xung đột cấu hình khi ghép lab:

| Node mạng | Vai trò | Card mạng VMware | IP gán tĩnh | Tài khoản hệ thống | Cấu hình & Dịch vụ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wazuh-SIEM** | Central SIEM | VMnet8 (NAT) | `192.168.100.10/24`<br>GW: `192.168.100.2` | `wazuh-user` / `wazuh`<br>Web: `admin` / *(file pass)* | Web HTTPS: 443<br>Agent port: 1514, 1515<br>RAM: 4GB, CPU: 2 Cores |
| **Suricata-Sensor** | Gateway & IDS/IPS | Card 1: VMnet8<br>Card 2: VMnet2 | `ens33`: `192.168.100.20/24`<br>`ens34`: `10.0.0.1/24` | `ubuntu` / `123` | Suricata Engine, IP Forwarding, NAT MASQUERADE<br>RAM: 2GB, CPU: 2 Cores |
| **Target-Server** | Web/DB mục tiêu | VMnet2 (Internal LAN) | `ens33`: `10.0.0.10/24`<br>GW: `10.0.0.1` | `ubuntu` / `123` | Nginx HTTP: 80, SSH: 22, Wazuh Agent<br>RAM: 2GB, CPU: 1 Core |
| **Attacker-Kali** | Red Team giả lập | VMnet8 (External NAT) | `eth0`: `192.168.100.50/24`<br>GW: `192.168.100.2` | `kali` / `kali` | Nmap, Hydra, SQLMap, Route tĩnh đến `10.0.0.0/24`<br>RAM: 2GB, CPU: 1 Core |

---

## 4. HƯỚNG DẪN THIẾT LẬP MÁY ẢO CHI TIẾT TRÊN VMWARE

### Bước 4.1: Cấu hình Virtual Network Editor (Thực hiện trước tiên)
1. Mở VMware Workstation $\rightarrow$ Chọn menu **Edit** $\rightarrow$ **Virtual Network Editor...**
2. Nhấn nút **Change Settings** (biểu tượng Administrator ở góc dưới bên phải).
3. **Cấu hình VMnet8 (NAT):**
   * Chọn dòng **VMnet8**.
   * Đảm bảo đã tích chọn **NAT (shared host's IP address with VMs)**.
   * Tại ô **Subnet IP**, nhập: `192.168.100.0`.
   * Tại ô **Subnet mask**, nhập: `255.255.255.0`.
   * Nhấn nút **NAT Settings...** $\rightarrow$ Kiểm tra Gateway IP là `192.168.100.2` $\rightarrow$ Nhấn **OK**.
4. **Cấu hình VMnet2 (Host-only - Mạng LAN nội bộ):**
   * Nhấn nút **Add Network...** $\rightarrow$ Chọn **VMnet2** $\rightarrow$ Nhấn **OK**.
   * Chọn dòng **VMnet2** vừa tạo $\rightarrow$ Chọn tùy chọn **Host-only**.
   * **BỎ TÍCH** ô **Use local DHCP service to distribute IP addresses to VMs** (bắt buộc bỏ tích để gán IP tĩnh, không để DHCP cấp lung tung).
   * Tại ô **Subnet IP**, nhập: `10.0.0.0`.
   * Tại ô **Subnet mask**, nhập: `255.255.255.0`.
5. Nhấn **Apply** $\rightarrow$ Nhấn **OK**.

### Bước 4.2: Import máy ảo Wazuh-SIEM (Từ file .OVA)
1. Trên menu VMware: Chọn **File** $\rightarrow$ **Open...**
2. Trỏ đến file `wazuh-4.x.x.ova` $\rightarrow$ Nhấn **Open**.
3. Đặt tên máy ảo: `Wazuh-SIEM` $\rightarrow$ Chọn thư mục lưu trữ còn trống $\ge 30\text{GB}$ $\rightarrow$ Nhấn **Import**.
4. Cấu hình phần cứng trước khi bật:
   * Chuột phải vào máy `Wazuh-SIEM` $\rightarrow$ **Settings**.
   * Mục **Memory**: Đặt **4096 MB (4 GB)**.
   * Mục **Processors**: Đặt **2 cores**.
   * Mục **Network Adapter**: Chọn **Custom** $\rightarrow$ Chọn **VMnet8 (NAT)** $\rightarrow$ Nhấn **OK**.
5. Bật máy, đăng nhập `wazuh-user` / `wazuh`.

### Bước 4.3: Cài đặt máy mẫu Ubuntu Base Template (Từ file .ISO)
1. Chọn **File** $\rightarrow$ **New Virtual Machine...** $\rightarrow$ Chọn **Typical** $\rightarrow$ **Next**.
2. Chọn **Installer disc image file (iso)** $\rightarrow$ Trỏ tới file `ubuntu-22.04.x-live-server-amd64.iso` $\rightarrow$ **Next**.
3. Đặt tên máy: `Ubuntu-Template-Base` $\rightarrow$ **Next**.
4. Đĩa cứng: Đặt **20.0 GB**, chọn **Split virtual disk into multiple files** (Tuyệt đối **không tích** ô *Allocate all disk space now*) $\rightarrow$ **Finish**.
5. Bật máy, tiến hành cài đặt Ubuntu:
   * Chọn ngôn ngữ English, giữ nguyên các tùy chọn mặc định của bộ cài.
   * Tạo tài khoản: User `ubuntu` / Password `123`.
   * Bỏ qua các snap package, chọn **Reboot Now** khi cài xong.
6. Sau khi máy khởi động lại vào terminal, cài sẵn các gói công cụ cốt lõi:
   ```bash
   sudo apt update && sudo apt install -y net-tools curl git jq iptables-persistent
   ```
7. Tắt máy hoàn toàn: `sudo poweroff`.
8. **Tạo mốc Snapshot mốc:**
   * Chuột phải vào máy `Ubuntu-Template-Base` $\rightarrow$ **Snapshot** $\rightarrow$ **Take Snapshot...**
   * Đặt tên snapshot: `Base_Clean` $\rightarrow$ Nhấn **Take Snapshot**.

### Bước 4.4: Tạo Linked Clone cho Sensor và Target (Tiết kiệm 70% ổ cứng)
#### 1. Tạo node Suricata-Sensor:
1. Chuột phải vào `Ubuntu-Template-Base` $\rightarrow$ **Manage** $\rightarrow$ **Clone...** $\rightarrow$ **Next**.
2. Chọn từ snapshot **Base_Clean** $\rightarrow$ **Next**.
3. Chọn tùy chọn **Create a linked clone** $\rightarrow$ **Next**.
4. Đặt tên máy: `Suricata-Sensor` $\rightarrow$ **Finish**.
5. Thêm card mạng thứ 2:
   * Chuột phải vào `Suricata-Sensor` $\rightarrow$ **Settings**.
   * Card mạng 1 (**Network Adapter**): Chuyển sang **Custom** $\rightarrow$ Chọn **VMnet8 (NAT)**.
   * Nhấn nút **Add...** $\rightarrow$ Chọn **Network Adapter** $\rightarrow$ **Finish**.
   * Card mạng 2 (**Network Adapter 2**): Chuyển sang **Custom** $\rightarrow$ Chọn **VMnet2** $\rightarrow$ **OK**.

#### 2. Tạo node Target-Server:
1. Chuột phải vào `Ubuntu-Template-Base` $\rightarrow$ **Manage** $\rightarrow$ **Clone...** $\rightarrow$ Chọn snapshot **Base_Clean**.
2. Chọn **Create a linked clone** $\rightarrow$ Đặt tên: `Target-Server` $\rightarrow$ **Finish**.
3. Cấu hình mạng:
   * Chuột phải vào `Target-Server` $\rightarrow$ **Settings**.
   * Card mạng (**Network Adapter**): Chuyển sang **Custom** $\rightarrow$ Chọn **VMnet2** $\rightarrow$ **OK**.

### Bước 4.5: Setup máy Kali Linux (Từ bản VMware Pre-built)
1. Dùng 7-Zip giải nén file `kali-linux-202x.x-vmware-amd64.7z` ra ổ cứng.
2. Trên VMware: Chọn **File** $\rightarrow$ **Open...** $\rightarrow$ Trỏ tới file `.vmx` trong thư mục vừa giải nén.
3. Chuột phải vào máy Kali $\rightarrow$ **Settings**:
   * **Memory:** Đặt **2048 MB (2 GB)**.
   * **Network Adapter:** Chuyển sang **Custom** $\rightarrow$ Chọn **VMnet8 (NAT)** $\rightarrow$ **OK**.
4. Bật máy Kali. Khi VMware hỏi *"This virtual machine might have been moved or copied"*, **bắt buộc chọn "I Copied It"** (để VMware tạo địa chỉ MAC mới, không trùng lặp mạng).
5. Đăng nhập với tài khoản: `kali` / `kali`.

### Bước 4.6: Tối ưu bộ nhớ VMware Preferences (Tránh treo máy thật)
1. Trên VMware: Chọn **Edit** $\rightarrow$ **Preferences...**
2. Chọn mục **Memory**: Tại dòng *Additional memory*, tích chọn **Allow most virtual machine memory to be paged** (cho phép hệ điều hành đưa bớt RAM nhàn rỗi xuống pagefile, tránh chiếm trọn RAM vật lý).
3. Nhấn **OK**.

---

## 5. QUY CHUẨN QUẢN TRỊ KHO LƯU TRỮ GITHUB NHÓM

### 5.1. Cấu trúc thư mục kho lưu trữ chuẩn
```text
soc-lab-wazuh-suricata/
├── .gitignore                      # Chặn commit file máy ảo, file log, secrets
├── README.md                       # Tài liệu tóm tắt kiến trúc mạng, thông số IP và cách chạy lab
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
│   └── attack_simulation.sh        # Script chạy tự động Nmap/Hydra từ máy Kali
└── docs/
    └── topology.png                # Sơ đồ kết nối mạng của hệ thống lab
```

### 5.2. Nội dung file `.gitignore` bắt buộc
```gitignore
# Tệp tin máy ảo và đĩa cứng
*.ova
*.iso
*.vmdk
*.vmem
*.nvram
*.log
*.gz

# Tệp nhật ký và dữ liệu tự sinh
*.json
eve.json
/var/log/

# Tệp bảo mật và cấu hình nhạy cảm
.env
*_passwords.txt
secrets.yml

# Tệp rác hệ thống
.DS_Store
Thumbs.db
```

### 5.3. Quy ước nhánh và Commit
* Nhánh `main`: Chỉ lưu các cấu hình đã được kiểm thử chạy thành công trên cụm máy ảo.
* Nhánh làm việc cá nhân:
  * `feature/wazuh-rules-telegram` (Thành viên 1)
  * `feature/suricata-sensor-nat` (Thành viên 2)
  * `feature/target-hardening-attacks` (Thành viên 3)
* Quy tắc commit: `[loại]: [Mô tả ngắn gọn tiếng Việt không dấu]` (Ví dụ: `feat: Them rule phat hien nmap scan`, `fix: Sua loi netplan card ens34`).

---

## 6. CƠ CẤU NHÓM 3 NGƯỜI & PHÂN CÔNG CHI TIẾT (RACI MATRIX)

| Thành viên | Vai trò & Trách nhiệm chính | Phân vùng quản lý | Đầu việc kỹ thuật cụ thể |
| :--- | :--- | :--- | :--- |
| **Thành viên 1** | **SIEM & Integration Lead**<br>*(Bộ não trung tâm)* | Quản lý máy ảo **Wazuh-SIEM** | - Import Wazuh OVA, cấu hình IP tĩnh và hạ Heap RAM JVM.<br>- Cấu hình nhận diện Agent từ Sensor và Target.<br>- Viết Custom Decoders và Custom Rules (`local_rules.xml`).<br>- Viết script Python `custom-telegram.py` và tích hợp webhook cảnh báo.<br>- Quản trị kho GitHub nhóm. |
| **Thành viên 2** | **Network & Sensor Specialist**<br>*(Cửa ngõ an ninh)* | Quản lý máy ảo **Suricata-Sensor** | - Dựng máy Ubuntu 2 card mạng, cấu hình IP Forwarding & NAT MASQUERADE.<br>- Cài đặt Suricata, cập nhật ET Open rules.<br>- Viết Custom Signatures (`local.rules`) phát hiện Nmap, SQLi.<br>- Cấu hình Wazuh Agent đọc luồng log `/var/log/suricata/eve.json`. |
| **Thành viên 3** | **Target Admin & Red Team Lead**<br>*(Mục tiêu & Kẻ tấn công)* | Quản lý máy ảo **Target-Server** và **Kali Linux** | - Dựng Web Server Nginx, cấu hình default gateway trỏ về Sensor.<br>- Cài đặt Wazuh Agent, kiểm thử Active Response (`firewall-drop`).<br>- Cấu hình máy Kali, thêm lệnh route tĩnh trỏ dải `10.0.0.0/24`.<br>- Viết script tự động hóa đòn tấn công (Nmap, Hydra Brute-force).<br>- Ghi nhận số liệu độ trễ phản hồi. |

---

## 7. NHỮNG ĐIỀU CẦN LƯU Ý & SAI LẦM CHÍ MẠNG TUYỆT ĐỐI TRÁNH TÁI PHẠM

Mọi thành viên phải đọc kỹ 6 sai lầm kinh điển sau để không làm hỏng bài lab:

1. **Sai lầm 1: Kali không thêm Static Route sang dải Target**
   * *Hiện tượng:* Kali gõ `nmap 10.0.0.10` báo `Host seems down`, không thể tấn công.
   * *Nguyên nhân:* Kali ở dải `192.168.100.x` không biết dải `10.0.0.x` nằm ở đâu nếu chưa chỉ đường.
   * *Cách khắc phục:* Trên Kali, luôn chạy lệnh: `sudo ip route add 10.0.0.0/24 via 192.168.100.20`.
2. **Sai lầm 2: Quên bật IP Forwarding trên máy Sensor**
   * *Hiện tượng:* Máy Target không thể ping ra ngoài Internet (`ping 8.8.8.8` báo timeout), không cài được gói `nginx` hay `wazuh-agent`.
   * *Cách khắc phục:* Trên Sensor, kiểm tra `cat /proc/sys/net/ipv4/ip_forward`. Nếu là `0`, phải chạy ngay `sudo sysctl -w net.ipv4.ip_forward=1` và lưu lại vào `/etc/sysctl.conf`.
3. **Sai lầm 3: Không giới hạn Java Heap Size của Wazuh Indexer**
   * *Hiện tượng:* Máy thật bị đơ cứng, VMware ngốn 100% RAM vật lý sau 30 phút chạy máy ảo.
   * *Cách khắc phục:* Sửa file `/etc/wazuh-indexer/jvm.options` giới hạn `-Xms1g` và `-Xmx1g`.
4. **Sai lầm 4: Không thêm White-list vào Active Response của Wazuh**
   * *Hiện tượng:* Khi kẻ tấn công quét cổng, Wazuh tự động chặn nhầm luôn cả IP của Gateway (`10.0.0.1` hoặc `192.168.100.20`), làm mất toàn bộ kết nối trong lab.
   * *Cách khắc phục:* Trong file `ossec.conf` của Wazuh Manager, bắt buộc thêm thẻ `<white_list>` chứa IP của Sensor, Target và Manager.
5. **Sai lầm 5: Để file log `eve.json` phình to làm tràn ổ đĩa**
   * *Hiện tượng:* Máy Sensor bị đầy 100% dung lượng ổ cứng, Suricata tự động ngắt dịch vụ.
   * *Cách khắc phục:* Chạy lệnh làm rỗng file log định kỳ: `sudo truncate -s 0 /var/log/suricata/eve.json`.
6. **Sai lầm 6: Quên phân quyền cho script `custom-telegram.py`**
   * *Hiện tượng:* Wazuh sinh cảnh báo mức 10+ nhưng Telegram không có tin nhắn.
   * *Cách khắc phục:* Bắt buộc chạy lệnh `sudo chmod 750 /var/ossec/integrations/custom-telegram.py` và `sudo chown root:wazuh /var/ossec/integrations/custom-telegram.py`.

---

## 8. LỘ TRÌNH TRIỂN KHAI TỪNG SPRINT (1 - 4)

```
[Tuần 1: Sprint 1] ────────► [Tuần 2: Sprint 2] ────────► [Tuần 3: Sprint 3] ────────► [Tuần 4: Sprint 4]
Dựng hạ tầng mạng ảo         Dựng Core SIEM,              Tích hợp luồng log,          Kịch bản kiểm thử,
Tạo Template & Clones        Suricata & Nginx             Active Response, Bot         Đóng băng Snapshot Demo
```

* **Sprint 1 (Hạ tầng mạng):** Cấu hình Virtual Network Editor (VMnet8, VMnet2). Import Wazuh OVA. Cài Ubuntu Template Base và tạo 2 Linked Clones. Thiết lập định tuyến Router trên Sensor.
* **Sprint 2 (Cài đặt dịch vụ lõi):** Cấu hình Suricata nạp ET Open Rules. Dựng Nginx trên Target. Cài Wazuh Agent trên cả 2 node, kết nối thành công về Dashboard với trạng thái Active xanh lá.
* **Sprint 3 (Tích hợp & Phản ứng tự động):** Cấu hình Agent trên Sensor đọc `eve.json`. Cấu hình Active Response tự động drop IP trên Target. Viết script `custom-telegram.py` và kiểm tra tin nhắn bắn về điện thoại.
* **Sprint 4 (Tổng duyệt & Đóng gói):** Chạy 3 kịch bản demo (Nmap, Hydra, Web Exploit). Đo đạc độ trễ phản hồi. Tạo snapshot chốt trạng thái sạch (`Final_Demo_Ready`) trên tất cả máy ảo. Đẩy toàn bộ cấu hình lên GitHub.

---

## 9. HƯỚNG DẪN CẤU HÌNH HỆ THỐNG CHI TIẾT (STEP-BY-STEP RUNBOOK)

### 9.1. Cấu hình máy Wazuh-SIEM
1. Đăng nhập terminal: `wazuh-user` / `wazuh`.
2. Gán IP tĩnh:
   ```bash
   sudo nmcli connection modify ens33 ipv4.addresses 192.168.100.10/24 ipv4.gateway 192.168.100.2 ipv4.dns "8.8.8.8,1.1.1.1" ipv4.method manual
   sudo nmcli connection up ens33
   ```
3. Giới hạn Heap Size OpenSearch:
   ```bash
   sudo sed -i 's/-Xms2g/-Xms1g/g' /etc/wazuh-indexer/jvm.options
   sudo sed -i 's/-Xmx2g/-Xmx1g/g' /etc/wazuh-indexer/jvm.options
   sudo systemctl restart wazuh-indexer
   ```
4. Đọc mật khẩu admin:
   ```bash
   sudo tar -O -xvf /home/wazuh-user/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
   ```

### 9.2. Cấu hình máy Suricata-Sensor (Router Gateway)
1. Cấu hình IP tĩnh 2 card mạng (`sudo nano /etc/netplan/00-installer-config.yaml`):
   ```yaml
   network:
     version: 2
     ethernets:
       ens33:
         addresses: [192.168.100.20/24]
         gateway4: 192.168.100.2
         nameservers:
           addresses: [8.8.8.8, 1.1.1.1]
       ens34:
         addresses: [10.0.0.1/24]
   ```
   Chạy lệnh: `sudo netplan apply`.
2. Bật IP Forwarding và NAT:
   ```bash
   sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf
   sudo sysctl -p
   sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
   sudo netfilter-persistent save
   ```
3. Cài đặt Suricata:
   ```bash
   sudo add-apt-repository ppa:oisf/suricata-stable -y
   sudo apt update && sudo apt install suricata jq -y
   sudo suricata-update
   ```
4. Sửa cấu hình `/etc/suricata/suricata.yaml`:
   * Chỉnh `HOME_NET`: `"[10.0.0.0/24,192.168.100.0/24]"`
   * Chỉnh `EXTERNAL_NET`: `"!$HOME_NET"`
   * Tại mục `af-packet:`, kiểm tra `- interface: ens34` (hoặc card mạng LAN nội bộ).
5. Thêm rule custom kiểm tra ping (`sudo nano /var/lib/suricata/rules/local.rules`):
   ```text
   alert icmp any any -> any any (msg:"TEST LAB - PING DETECTED"; sid:1000001; rev:1;)
   ```
6. Bật dịch vụ: `sudo systemctl restart suricata`.

### 9.3. Cấu hình máy Target-Server & Cài Agent
1. Cấu hình IP tĩnh trỏ Gateway về Sensor (`sudo nano /etc/netplan/00-installer-config.yaml`):
   ```yaml
   network:
     version: 2
     ethernets:
       ens33:
         addresses: [10.0.0.10/24]
         gateway4: 10.0.0.1
         nameservers:
           addresses: [8.8.8.8, 1.1.1.1]
   ```
   Chạy lệnh: `sudo netplan apply`.  
   *Kiểm tra thông mạng:* `ping -c 3 8.8.8.8` (phải nhận được phản hồi).
2. Cài Nginx làm dịch vụ mục tiêu:
   ```bash
   sudo apt update && sudo apt install nginx -y
   ```
3. Cài đặt Wazuh Agent:
   ```bash
   curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH.gpg | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && sudo chmod 644 /usr/share/keyrings/wazuh.gpg
   echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee -a /etc/apt/sources.list.d/wazuh.list
   sudo apt update
   sudo WAZUH_MANAGER="192.168.100.10" apt install wazuh-agent -y
   sudo systemctl enable wazuh-agent && sudo systemctl restart wazuh-agent
   ```

### 9.4. Đẩy log Suricata từ Sensor về Wazuh
1. Cài đặt Wazuh Agent lên máy **Suricata-Sensor** (tương tự mục 9.3 bước 3).
2. Mở `/var/ossec/etc/ossec.conf` trên Sensor, chèn thêm vào trong thẻ `<ossec_config>`:
   ```xml
   <localfile>
     <log_format>json</log_format>
     <location>/var/log/suricata/eve.json</location>
   </localfile>
   ```
3. Phân quyền và restart Agent:
   ```bash
   sudo chmod 644 /var/log/suricata/eve.json
   sudo systemctl restart wazuh-agent
   ```

### 9.5. Cấu hình Active Response & Telegram Alert trên Wazuh Server
1. Mở `/var/ossec/etc/ossec.conf` trên Wazuh Server, thêm cấu hình White-list và Active Response:
   ```xml
   <ossec_config>
     <global>
       <white_list>127.0.0.1</white_list>
       <white_list>192.168.100.10</white_list>
       <white_list>192.168.100.20</white_list>
       <white_list>10.0.0.1</white_list>
     </global>

     <active-response>
       <command>firewall-drop</command>
       <location>local</location>
       <rules_id>5712, 100002</rules_id>
       <timeout>600</timeout>
     </active-response>

     <integration>
       <name>custom-telegram.py</name>
       <level>10</level>
       <hook_url>https://api.telegram.org</hook_url>
       <alert_format>json</alert_format>
     </integration>
   </ossec_config>
   ```
2. Tạo script Webhook `/var/ossec/integrations/custom-telegram.py`:
   ```bash
   sudo nano /var/ossec/integrations/custom-telegram.py
   ```
   *Dán mã nguồn Python:*
   ```python
   #!/usr/bin/env python3
   import sys
   import json
   import requests

   BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

   alert_file = sys.argv[1]
   with open(alert_file) as f:
       alert_json = json.load(f)

   rule_id = alert_json.get('rule', {}).get('id', 'N/A')
   description = alert_json.get('rule', {}).get('description', 'N/A')
   level = alert_json.get('rule', {}).get('level', 0)
   src_ip = alert_json.get('data', {}).get('src_ip', alert_json.get('srcip', 'N/A'))

   message = (
       f"🚨 *CẢNH BÁO AN NINH MẠNG (SIEM)* 🚨\n\n"
       f"📌 *Hành vi:* {description}\n"
       f"🔢 *Rule ID:* {rule_id} | *Mức độ (Level):* {level}\n"
       f"🎯 *IP Nguồn Tấn Công:* `{src_ip}`\n"
   )

   url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
   requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
   ```
3. Cấp quyền thực thi bắt buộc:
   ```bash
   sudo chmod 750 /var/ossec/integrations/custom-telegram.py
   sudo chown root:wazuh /var/ossec/integrations/custom-telegram.py
   sudo systemctl restart wazuh-manager
   ```

---

## 10. KỊCH BẢN KIỂM THỬ THỰC NGHIỆM TẤN CÔNG - PHÒNG THỦ

> **LỆNH BẮT BUỘC TRÊN KALI TRƯỚC KHI TEST:**
> ```bash
> sudo ip route add 10.0.0.0/24 via 192.168.100.20
> ```

| Kịch bản | Công cụ & Lệnh thực thi từ Kali | Phản ứng Suricata IDS/IPS | Phản ứng Wazuh SIEM & Active Response | Bằng chứng nghiệm thu |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01: Quét do thám** | `nmap -sS -p 22,80 10.0.0.10` | Bắt signature `ET SCAN Nmap Scripting Engine User-Agent` trong `eve.json` | Wazuh Dashboard hiển thị Alert Level 6-8, phân loại nhóm `reconnaissance` | Biểu đồ cảnh báo trên Dashboard nhảy số; IP chưa bị chặn |
| **TC-02: Dò mật khẩu SSH & Tự chặn** | `hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.10 -t 4` | Ghi nhận sự kiện `ET SCAN Potential SSH Scan` | Xâu chuỗi: Log SSH failed liên tiếp $\rightarrow$ kích hoạt Rule 5712 (Level 10) | Terminal Hydra báo `Connection timed out`; `iptables -L` trên Target có dòng DROP IP Kali; Telegram nhận tin báo |
| **TC-03: Tấn công Web Injection** | `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"` | Bắt signature `ET WEB_SERVER SQL Injection Attempt` | Kích hoạt cảnh báo Critical (Level 12+), gắn nhãn MITRE ATT&CK T1190 | Suricata ghi log alert; Telegram bắn tin cảnh báo màu đỏ tức thời |

---

## 11. CHIẾN LƯỢC VẤN ĐÁP & BẢO VỆ ĐỒ ÁN NHÓM 3 NGƯỜI

Chuẩn bị trước câu trả lời cho các câu hỏi giảng viên chắc chắn sẽ hỏi từng thành viên:

### Câu hỏi cho Thành viên 1 (SIEM & Integration Lead):
* **Hỏi:** *"Tại sao đã có IDS/IPS rồi mà doanh nghiệp vẫn cần phải đầu tư thêm hệ thống SIEM?"*
* **Trả lời:** IDS/IPS chỉ nhìn thấy lưu lượng mạng đi qua đường truyền và phân tích độc lập từng gói tin. Nó không thể biết chuyện gì xảy ra sâu bên trong máy chủ (như log xác thực đăng nhập hỏng, tệp hệ thống bị thay đổi, tài khoản bị nâng quyền). SIEM đóng vai trò bộ não tập trung: gom cả log mạng từ Suricata và log hệ điều hành từ máy chủ về để **tương quan hóa (correlation)**. Nhờ đó ta phát hiện được các cuộc tấn công phức tạp nhiều giai đoạn (ví dụ: quét mạng bằng Nmap trước, sau đó bruteforce SSH thành công trên máy chủ).

### Câu hỏi cho Thành viên 2 (Network & Sensor Specialist):
* **Hỏi:** *"Sự khác biệt căn bản giữa chế độ IDS và IPS của Suricata là gì? Trong lab nhóm triển khai như thế nào?"*
* **Trả lời:** IDS chỉ đóng vai trò cảm biến thụ động (lắng nghe bản sao gói tin qua SPAN/Mirror port hoặc AF-PACKET) để phát hiện và ghi log cảnh báo mà không làm gián đoạn lưu lượng mạng. Trong khi đó, IPS đứng chắn ngang đường truyền (Inline mode / NFQUEUE), có quyền can thiệp thả (drop) gói tin độc hại ngay lập tức. Trong bài lab, nhóm sử dụng Suricata để soi chiếu sâu gói tin mạng sinh log chuẩn EVE JSON, kết hợp cơ chế Active Response của Wazuh để khóa IP vi phạm qua iptables.

### Câu hỏi cho Thành viên 3 (Target Admin & Red Team Lead):
* **Hỏi:** *"Cơ chế Active Response khóa IP kẻ tấn công hoạt động ra sao và làm sao để hệ thống không tự khóa chính mình?"*
* **Trả lời:** Khi Wazuh Manager phát hiện một sự kiện đạt ngưỡng vi phạm (ví dụ Rule ID 5712 khi dò pass SSH sai 5 lần), Manager sẽ phát lệnh xuống Wazuh Agent trên Target Server. Agent sẽ gọi script `firewall-drop` để thêm một dòng `DROP` chứa IP của kẻ tấn công vào đầu bảng `iptables`. Để tránh hệ thống tự khóa chính mình (tự từ chối dịch vụ), nhóm đã cấu hình danh sách loại trừ `<white_list>` trên file `ossec.conf` của Manager chứa IP của Gateway, IP của máy SIEM và dải loopback.

---

## 12. RUNBOOK XỬ LÝ SỰ CỐ & PHỤC HỒI THẢM HỌA (TROUBLESHOOTING)

Tra cứu và xử lý ngay khi gặp 4 sự cố thường gặp nhất:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ SỰ CỐ 1: TARGET SERVER KHÔNG CÓ MẠNG, KHÔNG TẢI ĐƯỢC NGINX/AGENT            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Kiểm tra IP Forwarding trên Sensor:                                      │
│    cat /proc/sys/net/ipv4/ip_forward  --> Nếu ra 0, chạy:                   │
│    sudo sysctl -w net.ipv4.ip_forward=1                                     │
│ 2. Kiểm tra NAT iptables trên Sensor:                                       │
│    sudo iptables -t nat -L -v -n  --> Phải thấy MASQUERADE trên ens33       │
│ 3. Kiểm tra Default Gateway trên Target:                                    │
│    ip route  --> Phải thấy dòng: default via 10.0.0.1 dev ens33             │
└─────────────────────────────────────────────────────────────────────────────┘
```

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ SỰ CỐ 2: WAZUH AGENT BÁO "NEVER CONNECTED" HOẶC "DISCONNECTED"              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Kiểm tra kết nối từ Agent tới Manager:                                   │
│    nc -zvu 192.168.100.10 1514                                              │
│    nc -zv 192.168.100.10 1515                                               │
│ 2. Nếu báo timeout, trên Wazuh Server mở tường lửa UFW:                     │
│    sudo ufw allow 1514/tcp && sudo ufw allow 1514/udp                       │
│    sudo ufw allow 1515/tcp                                                  │
│ 3. Khởi động lại Agent:                                                     │
│    sudo systemctl restart wazuh-agent                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ SỰ CỐ 3: KALI QUÉT NMAP NHƯNG SURICATA HOÀN TOÀN KHÔNG RA LOG ALERT         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Kiểm tra Suricata đang lắng nghe card mạng nào:                          │
│    grep -A 5 "af-packet:" /etc/suricata/suricata.yaml                       │
│    (Đảm bảo tên card mạng trùng khớp với card mạng hứng lưu lượng từ ip a)  │
│ 2. Kiểm tra số lượng rule đang nạp:                                         │
│    grep -c "alert" /var/lib/suricata/rules/suricata.rules                   │
│    Nếu bằng 0, chạy: sudo suricata-update && sudo systemctl restart suricata│
└─────────────────────────────────────────────────────────────────────────────┘
```

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ SỰ CỐ 4: BỊ TỰ CHẶN NHẦM IP, KHÔNG SSH VÀO ĐƯỢC TARGET SERVER               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Mở console máy ảo Target trực tiếp trên màn hình VMware.                 │
│ 2. Xóa sạch toàn bộ các rule DROP đang có trong bảng iptables:              │
│    sudo iptables -F                                                         │
│ 3. Kiểm tra lại danh sách chặn:                                             │
│    sudo iptables -L -n -v                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. BỘ LỆNH CỨU HỘ & KIỂM TRA NHANH (CHEAT-SHEET)

Sao chép và chạy trực tiếp các lệnh này trên terminal khi cần kiểm tra nhanh trạng thái toàn hệ thống:

```bash
# ============================================================
# 1. KIỂM TRA TRẠNG THÁI DỊCH VỤ TRÊN CÁC MÁY
# ============================================================
# Trên Wazuh Server:
sudo systemctl status wazuh-manager wazuh-indexer wazuh-dashboard

# Trên Suricata Sensor:
sudo systemctl status suricata wazuh-agent

# Trên Target Server:
sudo systemctl status nginx wazuh-agent

# ============================================================
# 2. XEM LOG TRỰC TIẾP THỜI GIAN THỰC (LIVE MONITORING)
# ============================================================
# Theo dõi log bắt gói độc hại của Suricata (lọc chỉ lấy alert):
tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert") | {time: .timestamp, src: .src_ip, alert: .alert.signature}'

# Theo dõi log hoạt động của Wazuh Agent:
tail -f /var/ossec/logs/ossec.log

# ============================================================
# 3. QUẢN TRỊ TƯỜNG LỬA VÀ ACTIVE RESPONSE
# ============================================================
# Xem danh sách IP đang bị khóa trên Target:
sudo iptables -L INPUT -n -v --line-numbers

# Làm rỗng file log eve.json khi đĩa cứng bị đầy:
sudo truncate -s 0 /var/log/suricata/eve.json

# Xóa chặn khẩn cấp toàn bộ iptables:
sudo iptables -F
```