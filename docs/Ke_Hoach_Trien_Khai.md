# KẾ HOẠCH TRIỂN KHAI KỸ THUẬT, QUẢN TRỊ GITHUB & RUNBOOK VẬN HÀNH DỰ PHÒNG

## ĐỒ ÁN MÔN HỌC: AN NINH MẠNG
**Đề tài:** Xây dựng hệ thống giám sát an ninh mạng tập trung kết hợp SIEM và IDS/IPS  
**Cơ cấu nhóm:** 03 thành viên  
**Mục đích tài liệu:** Bản thiết kế kỹ thuật chi tiết, cẩm nang thi công từng bước và ngân hàng 20 câu hỏi vấn đáp Viva Voce cho toàn bộ 3 thành viên. *(Bản tóm tắt điều hành, quy hoạch tổng quan & Quick Runbook xem tại [`README.md`](../README.md))*.

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

### 1.3. Sơ đồ dòng chảy dữ liệu sự kiện (Event Data Flow Pipeline)
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

## 2. BẢNG TỆP TIN CẦN TẢI VỀ MÁY TÍNH & KHÓA CỨNG PHIÊN BẢN SỐ CHÍNH XÁC

> ⛔ **CẢNH BÁO TỬ HUYỆT VỀ CON SỐ PHIÊN BẢN (VERSION COMPATIBILITY LOCK):**
> * **Wazuh SIEM (Quan trọng nhất):** Trên menu dropdown phiên bản của trang chủ Wazuh, **BẮT BUỘC CHỌN SỐ: `Version 4.7` HOẶC `Version 4.8`** (File `.ova`).  
>   ❌ **TUYỆT ĐỐI KHÔNG CHỌN:** Dòng trên cùng `Version 4.14 (current)`. Các bản mới này đã xóa đường dẫn file đọc pass `/home/wazuh-user/wazuh-install-files.tar` và đổi kiến trúc quản lý indexer, khiến lệnh trong Runbook bị vô hiệu hóa!
> * **Ubuntu Server (Target & Sensor):** BẮT BUỘC tải bản số **`22.04.4 LTS`** hoặc **`22.04.5 LTS`** (`ubuntu-22.04.x-live-server-amd64.iso`).  
>   ❌ **TUYỆT ĐỐI KHÔNG TẢI:** Bản mới nhất **`Ubuntu 24.04 LTS`** (Khai tử cú pháp Netplan `gateway4`, chặn cài Python bằng lỗi `PEP 668` và lỗi APT GPG key).
> * Tuyệt đối không tải các bản Desktop có giao diện đồ họa (GUI) gây tràn bộ nhớ RAM.

Cả nhóm chỉ cần chuẩn bị đúng các tệp tin theo con số phiên bản quy định trong bảng sau:

| Thành phần | Con số phiên bản CHÍNH XÁC | Tên tệp tin & Link tải trực tiếp | Dung lượng | Môi trường hệ điều hành | Phiên bản TUYỆT ĐỐI TRÁNH |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Wazuh-SIEM** | **`4.7.x`** hoặc **`4.8.x`** | • Bản 4.7: [`wazuh-4.7.5.ova` (Tải trực tiếp)](https://packages.wazuh.com/4.x/vm/wazuh-4.7.5.ova) — [Doc Wazuh 4.7](https://documentation.wazuh.com/4.7/deployment-options/virtual-machine/virtual-machine.html)<br>• Bản 4.8: [`wazuh-4.8.0.ova` (Tải trực tiếp)](https://packages.wazuh.com/4.x/vm/wazuh-4.8.0.ova) — [Doc Wazuh 4.8](https://documentation.wazuh.com/4.8/deployment-options/virtual-machine/virtual-machine.html) | ~4.5 GB | **Amazon Linux** (Dịch vụ mạng: `network`, `vi`)<br>*(❌ Không có `nmcli`)* | ❌ Tránh `4.14 (current)` |
| **Target & Sensor** | **`22.04.4`** hoặc **`22.04.5`** | [`ubuntu-22.04.5-live-server-amd64.iso` (Tải trực tiếp)](https://releases.ubuntu.com/jammy/ubuntu-22.04.5-live-server-amd64.iso) | ~2.5 GB | **Ubuntu 22.04 LTS** (Lệnh: `netplan`, `apt`) | ❌ Tránh `24.04` (Mới nhất) |
| **Attacker-Kali** | **`2023.4`** hoặc **`2024.1` / `2024.2`** | File `.7z` từ [Kali VMware Pre-built](https://www.kali.org/get-kali/#kali-virtual-machines) | ~3.0 GB | **Kali Linux (Debian)** (Có sẵn Nmap/Hydra) | Bản Installer ISO tự cài |
| **Suricata Engine** | **`6.0.x`** hoặc **`7.0.x`** | Cài tự động qua PPA `ppa:oisf/suricata-stable` | N/A | NIDS/IPS Engine | Bản mặc định cũ `5.x` |

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

### Bước 4.7: Hướng dẫn Copy - Paste & Điều khiển từ máy thật (Bí quyết x5 hiệu suất làm lab)
> ⛔ **CẢNH BÁO LỖI PHỔ BIẾN:**  
> Tuyệt đối **KHÔNG bấm nút "Install VMware Tools"** trên thanh menu của VMware Workstation. VMware sẽ báo lỗi `Could not find component on update server...` do Broadcom đã thay đổi cụm máy chủ tải về. Tất cả các hệ điều hành Linux hiện đại đều đã tích hợp hoặc sử dụng **`open-vm-tools`** chính thức!

#### 1. Chiến lược chuẩn DevSecOps: SSH trực tiếp từ PowerShell / Windows Terminal
Các máy chủ Linux Server (Wazuh, Ubuntu Server) chỉ chạy giao diện dòng lệnh (CLI - không có môi trường đồ họa X11), nên console ảo của VMware sẽ không thể bắt clipboard từ Windows một cách mượt mà.  
**Cách làm chuyên nghiệp:** Sau khi gán IP ở bước đầu tiên, hãy thu nhỏ VMware lại và mở **PowerShell / Windows Terminal** trên máy thật để SSH:

| Máy ảo mục tiêu | Địa chỉ IP | Lệnh SSH từ PowerShell máy thật | Tài khoản / Mật khẩu |
| :--- | :--- | :--- | :--- |
| **Wazuh-SIEM** | `192.168.100.10` | `ssh wazuh-user@192.168.100.10` | `wazuh-user` / `wazuh` |
| **Suricata-Sensor** | `192.168.100.20` | `ssh ubuntu@192.168.100.20` | `ubuntu` / `123` |
| **Target-Server** | `10.0.0.10` | `ssh ubuntu@10.0.0.10` *(xem lệnh thêm route bên dưới)* | `ubuntu` / `123` |
| **Attacker-Kali** | `192.168.100.50` | `ssh kali@192.168.100.50` | `kali` / `kali` |

* **Lợi ích:** Bạn hoàn toàn ở trên môi trường máy thật, có thể bôi đen copy bất kỳ khối lệnh cấu hình nào trong tài liệu này và **bấm `Ctrl + V` hoặc nhấp chuột phải** để dán tức thì, không bị sót ký tự, không bị kẹt phím!
* **Mẹo định tuyến truy cập Target-Server (`10.0.0.10`):** Do Target nằm ở dải mạng nội bộ phía sau Router Sensor, để máy thật Windows có thể ping và SSH trực tiếp vào Target, hãy mở **PowerShell (Run as Administrator)** trên máy thật Windows và chạy 1 lệnh duy nhất:
  ```powershell
  route add 10.0.0.0 mask 255.255.255.0 192.168.100.20
  ```

#### 2. Đối với máy Kali Linux (Giao diện đồ họa Desktop)
Để Copy - Paste văn bản và Kéo - Thả file (Drag & Drop) trực tiếp hai chiều giữa màn hình Windows và Desktop Kali Linux:
1. Mở terminal trên Kali Linux và chạy lệnh cài đặt:
   ```bash
   sudo apt update && sudo apt install -y open-vm-tools-desktop && sudo reboot
   ```
2. Trên giao diện VMware: Chuột phải vào máy `Attacker-Kali` $\rightarrow$ **Settings** $\rightarrow$ Thẻ **Options** $\rightarrow$ **Guest Isolation** $\rightarrow$ Đảm bảo đã tích chọn:
   * `[x] Enable drag and drop`
   * `[x] Enable copy and paste`

#### 3. Thao tác bàn phím quan trọng khi chưa có SSH (30 giây đầu cấu hình IP)
* **Thoát chuột từ màn hình máy ảo về Windows:** Nhấn tổ hợp phím **`Ctrl + Alt`**.
* **Wazuh (Amazon Linux 2023):** Dùng trình soạn thảo `vi`. Nhấn phím `i` để bắt đầu nhập văn bản, nhập xong nhấn `Esc` rồi gõ `:wq` và ấn `Enter` để lưu thoát.
* **Ubuntu Server (Sensor/Target):** Dùng `nano`. Nhập xong nhấn `Ctrl + O` $\rightarrow$ `Enter` để lưu, nhấn `Ctrl + X` để thoát.

#### 4. ⚠️ Nguyên tắc phân quyền thực thi (Root / sudo) & Cách xử lý lỗi E212 / E325
> ❌ **CẢNH BÁO LỖI PHỔ BIẾN:**  
> Nếu bạn mở file cấu hình mà **quên gõ `sudo`** hoặc **thư mục cha chưa được tạo**, khi lưu file bạn sẽ gặp ngay lỗi **`E212: Can't open file for writing`** (không lưu được file). Nếu bấm tắt cửa sổ ngang, lần sau mở file sẽ bị dính cảnh báo trùng swap **`E325: ATTENTION`**!

* **2 nguyên nhân cốt tử gây lỗi `E212: Can't open file for writing`:**
  1. *Quên quyền `sudo`:* File thuộc sở hữu của `root`, user thường không có quyền ghi.
  2. *Thư mục cha chưa tồn tại:* `vi` không thể tự tạo folder cha. Trên Amazon Linux 2023, thư mục `/etc/systemd/network` mặc định **chưa tồn tại**, bắt buộc phải chạy `sudo mkdir -p /etc/systemd/network` trước khi tạo file!
* **Cứu nguy trực tiếp trong `vi` khi đã lỡ nhập xong nội dung mà bị lỗi E212:**
  - Nhấn `Esc` $\rightarrow$ Gõ lệnh: `:!mkdir -p /etc/systemd/network` $\rightarrow$ Nhấn `Enter` (để tạo thư mục ngay lập tức) $\rightarrow$ Nhấn `Enter` để quay lại $\rightarrow$ Gõ `:wq` $\rightarrow$ Nhấn `Enter` để lưu thoát 100%!

* **Những lệnh nào BẮT BUỘC phải chạy với `sudo` (hoặc dưới quyền root)?**
  - Mọi thao tác tạo/sửa file trong `/etc/` và `/var/` (file mạng, cấu hình Suricata, Wazuh Agent/Manager, firewall).
  - Mọi lệnh điều khiển dịch vụ hệ thống: `sudo systemctl restart/start/status ...`.
  - Mọi lệnh cấu hình mạng & định tuyến: `sudo iptables ...`, `sudo sysctl ...`, `sudo netplan apply`.
  - Mọi lệnh cài đặt và gỡ bỏ phần mềm: `sudo apt ...`, `sudo dnf ...`.
* **Cách xử lý khi lỡ bị lỗi E212 trong `vi`:**
  - Nhấn phím **`Enter`** $\rightarrow$ Nhấn **`Esc`** $\rightarrow$ Gõ lệnh thoát cưỡng chế: **`:q!`** $\rightarrow$ Nhấn **`Enter`**. Sau đó mở lại bằng `sudo vi ...`.
* **Cách xử lý khi bị cảnh báo trùng Swap (E325: ATTENTION):**
  - Nhấn phím **`q`** để thoát cảnh báo $\rightarrow$ Chạy lệnh dọn sạch tiến trình ngầm và file swap:
    ```bash
    sudo killall vi 2>/dev/null
    sudo rm -f /var/tmp/*.swp 2>/dev/null
    ```
* **💡 Tuyệt chiêu làm lab không lo quên `sudo`:**
  - Ngay sau khi đăng nhập máy ảo hoặc kết nối SSH, hãy gõ 1 lệnh duy nhất để chuyển thẳng sang quyền root:
    ```bash
    sudo -i
    ```
    *(Dấu nhắc lệnh từ `$` sẽ đổi sang `#`, lúc này bạn là root toàn quyền, tha hồ chạy mọi lệnh trong Runbook mà không cần gõ `sudo` ở đầu mỗi dòng).*

---

## 5. QUY CHUẨN QUẢN TRỊ KHO LƯU TRỮ GITHUB NHÓM

### 5.1. Cấu trúc thư mục kho lưu trữ chuẩn
```text
soc-lab-wazuh-suricata/
├── .github/workflows/
│   └── ci.yml                      # CI kiểm tra cú pháp YAML, XML, Script & Secret
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
│   ├── custom-discord.py           # Script Webhook bắn cảnh báo tự động về Discord (Free 100%)
│   └── attack_simulation.sh        # Script chạy tự động Nmap/Hydra từ máy Kali
└── docs/
    ├── Ke_Hoach_Trien_Khai.md      # Bản kế hoạch kỹ thuật & Runbook chi tiết
    └── topology.png                # Sơ đồ kết nối mạng của hệ thống lab (tùy chọn)
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

# Thư mục cấu hình AI Agent & Giao thức QA cục bộ (Tuyệt đối không commit lên GitHub)
.agent/
prompt.md
promp.md
README_2.md
README_*.md
assets/
session_summary.md
```

### 5.3. Quy ước nhánh và Commit
* Nhánh `main`: Chỉ lưu các cấu hình đã được kiểm thử chạy thành công trên cụm máy ảo.
* Nhánh làm việc cá nhân:
  * `feature/wazuh-rules-telegram` (Thành viên 1)
  * `feature/suricata-sensor-nat` (Thành viên 2)
  * `feature/target-hardening-attacks` (Thành viên 3)
* Quy tắc commit: `[loại]: [Mô tả ngắn gọn tiếng Việt không dấu]` (Ví dụ: `feat: Them rule phat hien nmap scan`, `fix: Sua loi netplan card ens34`).

### 5.4. Hướng dẫn đồng bộ tệp cấu hình từ máy ảo ra máy thật (Repository)
Do các máy ảo chạy hệ điều hành **Ubuntu Server không có giao diện đồ họa (GUI)**, thành viên không thể kéo thả chuột (Drag & Drop). Vì mỗi thành viên làm việc trên máy tính cá nhân quản lý máy ảo riêng, hãy sử dụng bộ lệnh `scp` tương ứng với vai trò của mình từ PowerShell máy thật:

#### 🟢 Dành cho THÀNH VIÊN 1 (Trên máy tính chạy Wazuh-SIEM):
> [!IMPORTANT]
> **Lưu ý phân quyền Linux (Zero-Error):** Thư mục `/var/ossec/etc/` thuộc sở hữu `root:wazuh` (quyền `750`). User `wazuh-user` không được đọc trực tiếp qua SCP nếu không qua thư mục cá nhân.
> 1. Trên máy ảo Wazuh, copy file ra thư mục `home` và phân quyền cho `wazuh-user`:
>    ```bash
>    sudo cp /var/ossec/etc/ossec.conf /var/ossec/etc/rules/local_rules.xml /home/wazuh-user/
>    sudo cp /var/ossec/integrations/custom-*.py /home/wazuh-user/ 2>/dev/null || true
>    sudo chown wazuh-user:wazuh-user /home/wazuh-user/*
>    ```
> 2. Mở PowerShell hoặc Git Bash tại thư mục dự án trên máy thật (`d:\AnNinhMang\soc-lab-wazuh-suricata`) để tải về:
>    ```bash
>    scp wazuh-user@192.168.100.10:~/ossec.conf ./configs/ossec-manager.conf
>    scp wazuh-user@192.168.100.10:~/local_rules.xml ./rules/local_rules.xml
>    scp wazuh-user@192.168.100.10:~/custom-discord.py ./scripts/ 2>/dev/null || true
>    scp wazuh-user@192.168.100.10:~/custom-telegram.py ./scripts/ 2>/dev/null || true
>    ```

#### 🟡 Dành cho THÀNH VIÊN 2 (Trên máy tính chạy Suricata-Sensor):
Mở PowerShell tại thư mục dự án trên máy thật:
```powershell
# Lấy cấu hình Netplan 2 card, Suricata YAML, local.rules và Agent config từ Sensor (192.168.100.20):
scp ubuntu@192.168.100.20:/etc/netplan/00-installer-config.yaml ./configs/netplan-sensor.yaml
scp ubuntu@192.168.100.20:/etc/suricata/suricata.yaml ./configs/suricata.yaml
scp ubuntu@192.168.100.20:/var/lib/suricata/rules/local.rules ./rules/
scp ubuntu@192.168.100.20:/var/ossec/etc/ossec.conf ./configs/ossec-agent-sensor.conf
```

#### 🔴 Dành cho THÀNH VIÊN 3 (Trên máy tính chạy Target-Server & Kali Linux):
Mở PowerShell tại thư mục dự án trên máy thật:
```powershell
# 1. Lấy script tấn công tự động từ máy Kali (192.168.100.50):
scp kali@192.168.100.50:/home/kali/attack_simulation.sh ./scripts/

# 2. Lấy cấu hình Netplan từ máy Target (10.0.0.10 - mạng nội bộ VMnet2):
# Lưu ý: Do VMnet2 tắt DHCP, để scp được từ Windows, bạn đặt IP tĩnh cho card 'VMware Network Adapter VMnet2' trên máy thật là 10.0.0.254/24:
scp ubuntu@10.0.0.10:/etc/netplan/00-installer-config.yaml ./configs/netplan-target.yaml
# (Hoặc đơn giản trên terminal Target gõ 'cat /etc/netplan/00-installer-config.yaml' rồi copy-paste nội dung)
```

#### Phương pháp thay thế (Đồ họa & DevSecOps):
* **Dùng WinSCP:** Kết nối SFTP Port 22 vào IP máy ảo trên máy tính của bạn (`ubuntu`/`123` hoặc `wazuh-user`/`wazuh`) để kéo thả file.
* **Dùng Git trực tiếp trên máy ảo:** `git clone` repo về máy ảo, copy file vào thư mục và `git push` thẳng lên nhánh cá nhân của bạn.

---

### 5.5. QUY TRÌNH PHẢN HỒI & ĐỒNG BỘ HIỆU CHỈNH TÀI LIỆU (LIVING DOCUMENTATION PROTOCOL)
Đồ án coi tài liệu là **thực tế sống (Single Source of Truth)**. Trong quá trình các thành viên triển khai trên máy ảo VMware, nếu phát hiện bất kỳ điểm sai khác nào (như câu lệnh không tương thích hệ điều hành, tên card mạng khác `eth0`/`ens33`, thiếu gói tiện ích, lỗi phiên bản):

1. **Quyền hạn & Khuyến khích:** Mọi thành viên đều có toàn quyền và được khuyến khích cập nhật sửa đổi tài liệu ngay lập tức để cả nhóm cùng dùng bản chuẩn nhất.
2. **Quy tắc sửa đổi đồng bộ:** Bắt buộc cập nhật song song trên cả 2 tệp:
   * [`README.md`](file:///d:/AnNinhMang/soc-lab-wazuh-suricata/README.md) (Tóm tắt kiến trúc & Runbook cốt lõi)
   * [`docs/Ke_Hoach_Trien_Khai.md`](file:///d:/AnNinhMang/soc-lab-wazuh-suricata/docs/Ke_Hoach_Trien_Khai.md) (Kế hoạch kỹ thuật chi tiết 13 mục)
3. **Quy trình Git & Hỗ trợ Fast-Pass từ CI:**
   * Tạo commit sửa đổi trên nhánh làm việc cá nhân:
     ```bash
     git add README.md docs/Ke_Hoach_Trien_Khai.md
     git commit -m "docs: cap nhat sua buoc X do thuc te may ao Y"
     git push origin <ten-nhanh>
     ```
   * Mở Pull Request hướng về `main`.
   * Hệ thống **CI GitHub Actions** đã kích hoạt **Doc Whitelist Fast-Pass**: Mọi PR chỉ sửa đổi tài liệu hợp lệ của đồ án sẽ được thông qua cực nhanh (~10s) mà không bị chặn bởi các bài kiểm tra kỹ thuật nặng.
   * Nhắn tin nhanh vào nhóm chat (Telegram/Zalo) để đồng đội cùng `git pull origin main` cập nhật kiến thức mới nhất.

#### Hướng dẫn chuyển sang nhánh main & kéo dữ liệu mới nhất về máy (Daily Sync Guide)
Khi nhận được thông báo trong nhóm chat có cập nhật mới vừa được merge vào nhánh `main`:

* **Cách 1: Cập nhật nhánh `main` trên máy tính:**
  ```bash
  git checkout main
  git pull origin main
  ```

* **Cách 2: Đồng bộ nội dung mới từ `main` vào nhánh cá nhân đang làm dở:**
  ```bash
  # Lưu tạm thay đổi dở dang (nếu có):
  git stash

  # Chuyển sang main và kéo dữ liệu mới:
  git checkout main
  git pull origin main

  # Quay lại nhánh công việc và gộp cập nhật từ main vào:
  git checkout <ten-nhanh-cua-ban>
  git merge main

  # Lấy lại các thay đổi dở dang để làm tiếp:
  git stash pop
  ```

* **Cách 3: Kiểm tra & Sửa lỗi chéo trên Pull Request của đồng đội (Review & Fix PR):**
  ```bash
  # 1. Tải danh sách commit và nhánh mới nhất từ GitHub:
  git fetch origin

  # 2. Chuyển sang nhánh PR của bạn (lần đầu tiên lấy về máy):
  git switch --track origin/<ten-nhanh-pr>   # Ví dụ: git switch --track origin/feature/suricata-sensor-nat

  # 3. Xem các thay đổi so với nhánh main:
  git diff main...HEAD

  # 4. Sửa lỗi, chạy thử nghiệm, sau đó commit và push thẳng lên chính nhánh PR đó:
  git add .
  git commit -m "fix: sua loi cu phap ho dong doi"
  git push origin <ten-nhanh-pr>

  # 5. Khi CI GitHub Actions báo Xanh lá -> Tiến hành Duyệt (Approve) và bấm Merge vào main!
  ```

---

## 6. CƠ CẤU NHÓM 3 NGƯỜI & PHÂN CÔNG CHI TIẾT (RACI MATRIX)

| Thành viên | Vai trò & Trách nhiệm chính | Phân vùng quản lý | Đầu việc kỹ thuật cụ thể |
| :--- | :--- | :--- | :--- |
| **Thành viên 1** | **SIEM & Integration Lead**<br>*(Bộ não trung tâm)* | Quản lý máy ảo **Wazuh-SIEM** | - Import Wazuh OVA, cấu hình IP tĩnh và hạ Heap RAM JVM.<br>- Cấu hình nhận diện Agent từ Sensor và Target.<br>- Viết Custom Decoders và Custom Rules (`local_rules.xml`).<br>- Viết script Python `custom-telegram.py` và tích hợp webhook cảnh báo.<br>- Quản trị kho GitHub nhóm. |
| **Thành viên 2** | **Network & Sensor Specialist**<br>*(Cửa ngõ an ninh)* | Quản lý máy ảo **Suricata-Sensor** | - Dựng máy Ubuntu 2 card mạng, cấu hình IP Forwarding & NAT MASQUERADE.<br>- Cài đặt Suricata, cập nhật ET Open rules.<br>- Viết Custom Signatures (`local.rules`) phát hiện Nmap, SQLi.<br>- Cấu hình Wazuh Agent đọc luồng log `/var/log/suricata/eve.json`. |
| **Thành viên 3** | **Target Admin & Red Team Lead**<br>*(Mục tiêu & Kẻ tấn công)* | Quản lý máy ảo **Target-Server** và **Kali Linux** | - Dựng Web Server Nginx, cấu hình default gateway trỏ về Sensor.<br>- Cài đặt Wazuh Agent, kiểm thử Active Response (`firewall-drop`).<br>- Cấu hình máy Kali, thêm lệnh route tĩnh trỏ dải `10.0.0.0/24`.<br>- Viết script tự động hóa đòn tấn công (Nmap, Hydra Brute-force).<br>- Ghi nhận số liệu độ trễ phản hồi. |

---

## 7. NHỮNG ĐIỀU CẦN LƯU Ý & SAI LẦM CHÍ MẠNG TUYỆT ĐỐI TRÁNH TÁI PHẠM

Mọi thành viên phải đọc kỹ 8 sai lầm kinh điển sau để không làm hỏng bài lab:

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
7. **Sai lầm 7: Cố gắng copy/paste qua màn hình Console của VMware thay vì SSH từ máy thật**
   * *Hiện tượng:* Không thể dán lệnh từ tài liệu vào máy ảo, hoặc bấm "Install VMware Tools" trên VMware bị lỗi `Could not find component on update server`.
   * *Nguyên nhân:* Server Broadcom đã đóng đường dẫn tải cũ của VMware Tools; hơn nữa các bản Linux Server (Wazuh, Ubuntu CLI) không có giao diện đồ họa X11 nên console VMware không nhận clipboard từ Windows.
   * *Cách khắc phục:* 
     * **KHÔNG bấm "Install VMware Tools" trên VMware.**
     * Gõ cấu hình IP ban đầu (chỉ mất 30s), sau đó **mở PowerShell trên máy thật (Windows) và SSH trực tiếp vào IP máy ảo** (`ssh user@IP`). Từ terminal máy thật, copy-paste bằng `Ctrl + V` hoặc Chuột phải mượt mà 100%.
     * Đối với máy Kali Linux (có desktop): Chạy lệnh `sudo apt install -y open-vm-tools-desktop && sudo reboot` và bật tính năng `Guest Isolation` trong VM Settings.
8. **Sai lầm 8: Quên gõ `sudo` hoặc chưa tạo thư mục cha (Lỗi vi E212 & E325 Swap Lock)**
   * *Hiện tượng:* Khi lưu file bằng `vi` bị báo lỗi `E212: Can't open file for writing`; đóng ngang màn hình thì lần sau mở lại bị báo `E325: ATTENTION Swap file already exists`.
   * *Nguyên nhân:* Do tài khoản thường thiếu quyền `sudo` HOẶC do thư mục cha (như `/etc/systemd/network/` trên Amazon Linux 2023) chưa hề tồn tại khiến `vi` không thể tạo file.
   * *Cách khắc phục:*
     * Luôn tạo thư mục cha trước: `sudo mkdir -p /etc/systemd/network`.
     * Cứu nguy khi đang ở trong `vi`: Nhấn `Esc` $\rightarrow$ gõ `:!mkdir -p /etc/systemd/network` $\rightarrow$ `Enter` $\rightarrow$ `Enter` $\rightarrow$ `:wq`.
     * Luôn chạy lệnh với `sudo` (hoặc gõ `sudo -i` để lên quyền root ngay từ đầu).
     * Thoát `vi` khi bị lỗi E212: Nhấn `Enter` $\rightarrow$ `Esc` $\rightarrow$ `:q!` $\rightarrow$ `Enter`.
     * Xóa sạch file swap rác: `sudo killall vi 2>/dev/null; sudo rm -f /var/tmp/*.swp 2>/dev/null`.

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

## 9. HƯỚNG DẪN CẤU HÌNH HỆ THỐNG CHI TIẾT THEO TỪNG THÀNH VIÊN (STEP-BY-STEP RUNBOOK)

---

### 🟢 9.1. QUY TRÌNH DÀNH CHO THÀNH VIÊN 1: SIEM & INTEGRATION LEAD
* **Phân vùng quản lý:** Máy ảo `Wazuh-SIEM` (`192.168.100.10/24`)
* **Nhánh Git làm việc:** `feature/wazuh-rules-telegram`
* **Nhiệm vụ cốt lõi:** Dựng máy chủ SIEM, hạ tải RAM OpenSearch, cấu hình phân tích tương quan, thiết lập danh sách trắng (whitelist) chống tự chặn, tích hợp Webhook Telegram bắn cảnh báo khẩn.

#### Bước 1: Khởi động máy ảo và gán IP tĩnh 192.168.100.10 (Tuyệt chiêu SSH máy thật)
1. Import file `.ova` vào VMware (xem lại [Mục 4.2](#bước-42-import-máy-ảo-wazuh-siem-từ-file-ova)).
2. Đăng nhập terminal: user `wazuh-user` / password `wazuh`.
3. Khi máy ảo khởi động lên mạng NAT VMnet8, VMware tự động cấp IP động qua DHCP:
   * **Bước 3.1: Xem IP DHCP tạm thời hiện tại:**
     ```bash
     ip a
     ```
     *(Tìm dòng `inet 192.168.100.xxx` ở card `eth0`, ví dụ: `192.168.100.130`)*.
   * **Bước 3.2: Mở PowerShell máy thật Windows và SSH vào ngay:**
     ```powershell
     ssh wazuh-user@192.168.100.xxx   # Thay xxx bằng IP vừa xem (mật khẩu: wazuh)
     ```
   * **Bước 3.3: Trên cửa sổ SSH máy thật, paste khối lệnh ghi đè file ifcfg-eth0 để gán tĩnh 192.168.100.10:**
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
     *(Sau khi restart network, phiên SSH cũ sẽ tự ngắt vì IP đã đổi sang `192.168.100.10`)*.
   * **Bước 3.4: Kết nối lại bằng IP tĩnh chuẩn:**
     ```powershell
     ssh wazuh-user@192.168.100.10
     ```

#### Bước 2: Hạ tải Java Heap Size OpenSearch (Bắt buộc tránh đơ máy thật)
Dán khối lệnh an toàn (tự động dọn rác và cấu hình chuẩn 1GB, tránh nuốt ký tự):
```bash
sudo sed -i '/-Xm/d' /etc/wazuh-indexer/jvm.options
sudo sed -i '/-ons/d' /etc/wazuh-indexer/jvm.options
echo "-Xms1g" | sudo tee -a /etc/wazuh-indexer/jvm.options
echo "-Xmx1g" | sudo tee -a /etc/wazuh-indexer/jvm.options
sudo systemctl daemon-reload
sudo systemctl restart wazuh-indexer
```

#### Bước 3: Lấy mật khẩu tài khoản Admin đăng nhập Web Dashboard
* Trên các bản Wazuh OVA chính thức, tài khoản Web Dashboard mặc định là: `admin` / `admin`.
* Nếu hệ thống yêu cầu mật khẩu ngẫu nhiên trong quá trình cài đặt, chạy lệnh:
```bash
cat /home/wazuh-user/wazuh-passwords.txt 2>/dev/null || sudo tar -O -xvf /home/wazuh-user/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt 2>/dev/null
```
*Truy cập trình duyệt máy thật:* `https://192.168.100.10` với user `admin` và mật khẩu tương ứng.

> [!TIP]
> **Xử lý sự cố truy cập Web Dashboard thực tế:**
> 1. **Lỗi `ERR_CONNECTION_REFUSED`:** Trình duyệt tự động dùng `http://` (port 80). Bắt buộc phải gõ rõ ràng tiền tố **`https://192.168.100.10`** (port 443).
> 2. **Thông báo `"Wazuh dashboard server is not ready yet"`:** Đây là hiện tượng bình thường khi máy ảo vừa khởi động lại. Database `wazuh-indexer` mất từ 60 - 90 giây để nạp xong chỉ mục. Chỉ cần chờ 1 phút rồi nhấn **F5 (Reload)** trang web. Nếu cần kiểm tra: `sudo systemctl status wazuh-indexer`.

#### Bước 4: Kiểm tra tường lửa đón kết nối Agent
*Bản OVA chạy Amazon Linux 2023 (quản lý qua `firewalld` thay vì `ufw`):*
```bash
# Mở cổng nếu firewalld đang bật (nếu firewalld inactive thì các cổng đã thông sẵn):
sudo firewall-cmd --add-port={1514/tcp,1514/udp,1515/tcp,443/tcp} --permanent 2>/dev/null && sudo firewall-cmd --reload 2>/dev/null || true
```

#### Bước 5: Cấu hình White-list và Active Response (`/var/ossec/etc/ossec.conf`)
Mở file cấu hình trung tâm: `sudo nano /var/ossec/etc/ossec.conf`. Thêm danh sách IP loại trừ và chính sách khóa IP:
```xml
<ossec_config>
  <!-- 1. Danh sách trắng chống tự khóa chính mình -->
  <global>
    <white_list>127.0.0.1</white_list>
    <white_list>192.168.100.10</white_list> <!-- IP Wazuh SIEM -->
    <white_list>192.168.100.20</white_list> <!-- IP Sensor External -->
    <white_list>10.0.0.1</white_list>       <!-- IP Sensor Internal Gateway -->
  </global>

  <!-- 2. Kích hoạt Active Response chặn IP vi phạm -->
  <active-response>
    <command>firewall-drop</command>
    <location>local</location>
    <rules_id>5712, 100002</rules_id> <!-- Khóa IP khi brute-force SSH hoặc vi phạm nghiêm trọng -->
    <timeout>600</timeout>            <!-- Thời gian khóa: 10 phút (600 giây) -->
  </active-response>

  <!-- 3A. Tích hợp Webhook đẩy cảnh báo Telegram (Tùy chọn) -->
  <integration>
    <name>custom-telegram.py</name>
    <level>10</level>                 <!-- Chỉ gửi cảnh báo từ Level 10 trở lên -->
    <hook_url>https://api.telegram.org</hook_url>
    <alert_format>json</alert_format>
  </integration>

  <!-- 3B. Tích hợp Webhook đẩy cảnh báo Discord (Miễn phí 100%, không cần số điện thoại) -->
  <integration>
    <name>custom-discord.py</name>
    <level>10</level>
    <hook_url>https://discord.com/api/webhooks/</hook_url>
    <alert_format>json</alert_format>
  </integration>
</ossec_config>
```

#### Bước 6: Soạn script Webhook cảnh báo (Telegram hoặc Discord) và cấp quyền thực thi

##### Tùy chọn 6A: Tích hợp Telegram Webhook
Tạo file: `sudo nano /var/ossec/integrations/custom-telegram.py`
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

##### Tùy chọn 6B: Tích hợp Discord Webhook (Khuyên dùng - Miễn phí 100%, tạo Webhook 30s)
Tạo file: `sudo nano /var/ossec/integrations/custom-discord.py`
```python
#!/usr/bin/env python3
import sys
import json
import requests

WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

if len(sys.argv) < 2:
    sys.exit(0)

alert_file = sys.argv[1]
with open(alert_file, "r", encoding="utf-8") as f:
    alert_json = json.load(f)

rule = alert_json.get("rule", {})
rule_id = rule.get("id", "N/A")
description = rule.get("description", "Canh bao khong co mo ta")
level = rule.get("level", 0)

data = alert_json.get("data", {})
src_ip = data.get("src_ip", alert_json.get("srcip", "N/A"))
agent_name = alert_json.get("agent", {}).get("name", "Wazuh-Manager")

payload = {
    "username": "Wazuh SIEM Alert",
    "embeds": [{
        "title": f"🚨 [LEVEL {level}] CẢNH BÁO AN NINH MẠNG",
        "description": f"**Hành vi:** {description}",
        "color": 0xFF0000 if level >= 10 else 0xFFA500,
        "fields": [
            {"name": "🔢 Rule ID", "value": f"`{rule_id}`", "inline": True},
            {"name": "🎯 Mức độ", "value": f"**{level}/15**", "inline": True},
            {"name": "⚠️ IP Tấn công", "value": f"`{src_ip}`", "inline": True},
            {"name": "🖥️ Mục tiêu", "value": f"`{agent_name}`", "inline": True}
        ]
    }]
}

if WEBHOOK_URL != "YOUR_DISCORD_WEBHOOK_URL":
    requests.post(WEBHOOK_URL, json=payload, timeout=5)
```

Phân quyền thực thi chuẩn xác cho cả 2 script:
```bash
sudo chmod 750 /var/ossec/integrations/custom-telegram.py /var/ossec/integrations/custom-discord.py 2>/dev/null || true
sudo chown root:wazuh /var/ossec/integrations/custom-telegram.py /var/ossec/integrations/custom-discord.py 2>/dev/null || true
sudo systemctl restart wazuh-manager
```

#### Bước 7: Cấu hình Custom Rule phát hiện Brute-Force (`/var/ossec/etc/rules/local_rules.xml`)
Chèn Rule ID `100002` (Level 10) để bắt đòn tấn công brute-force SSH và kích hoạt Active Response:
```bash
sudo tee -a /var/ossec/etc/rules/local_rules.xml > /dev/null << 'EOF'

<!-- Custom Lab Rules -->
<group name="local,syslog,">
  <rule id="100002" level="10">
    <if_sid>5710, 5711, 5712</if_sid>
    <description>SOC Lab: Phat hien Brute-Force SSH tan cong lien tuc vao Target</description>
    <mitre>
      <id>T1110.001</id>
    </mitre>
  </rule>
</group>
EOF
sudo systemctl restart wazuh-manager
```

#### Bước 8: Tắt máy ảo an toàn và Chụp Offline Snapshot trên VMware
Sau khi hoàn tất toàn bộ cấu hình, tắt máy ảo từ SSH để bảo vệ cơ sở dữ liệu:
```bash
sudo poweroff
```
*(Đợi máy ảo tắt hẳn trên VMware, vào menu **VM $\rightarrow$ Snapshot $\rightarrow$ Take Snapshot...**, đặt tên `01-Wazuh-Init-Clean-Ready` để đóng băng mốc hoàn thành).*

---

### 🟡 9.2. QUY TRÌNH DÀNH CHO THÀNH VIÊN 2: NETWORK & SENSOR SPECIALIST
* **Phân vùng quản lý:** Máy ảo `Suricata-Sensor` (Router 2 card: `192.168.100.20` & `10.0.0.1`)
* **Nhánh Git làm việc:** `feature/suricata-sensor-nat`
* **Nhiệm vụ cốt lõi:** Cấu hình 2 card mạng, biến Ubuntu thành Router NAT chuyển tiếp lưu lượng, cài đặt và tối ưu Suricata NIDS/IPS, viết Signatures và forward luồng log `eve.json` về SIEM.

#### Bước 1: Thiết lập card mạng và cấu hình Netplan
1. Tạo Linked Clone từ `Ubuntu-Template-Base`, gán 2 card mạng:
   * Card 1 (`ens33`): VMnet8 (NAT).
   * Card 2 (`ens34`): VMnet2 (Host-only).
2. Soạn cấu hình IP tĩnh: `sudo nano /etc/netplan/00-installer-config.yaml`:
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
   Áp dụng mạng: `sudo netplan apply`.  
   *(Mẹo Copy/Paste: Ngay sau khi apply mạng thành công, hãy chuyển sang PowerShell trên máy thật Windows và gõ `ssh ubuntu@192.168.100.20` với pass `123` để paste các lệnh cấu hình bên dưới cực nhanh mà không lo kẹt phím!)*

#### Bước 2: Kích hoạt Router IP Forwarding & NAT Masquerade
```bash
# 1. Bật IP Forwarding vĩnh viễn
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf
sudo sysctl -p

# 2. Cài đặt công cụ lưu trữ iptables (Bắt buộc tránh mất rule NAT khi máy reboot)
sudo apt update && sudo apt install -y iptables-persistent netfilter-persistent

# 3. Cấu hình iptables NAT chuyển tiếp gói tin từ LAN ra Internet
sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
sudo netfilter-persistent save
```

#### Bước 3: Cài đặt Suricata Engine và nạp tập luật ET-Open
```bash
sudo add-apt-repository ppa:oisf/suricata-stable -y
sudo apt update && sudo apt install suricata jq -y
sudo suricata-update
```

#### Bước 4: Tinh chỉnh cấu hình Suricata (`/etc/suricata/suricata.yaml`)
Mở file: `sudo nano /etc/suricata/suricata.yaml`:
* Tìm mục `HOME_NET`, sửa thành: `"[10.0.0.0/24,192.168.100.0/24]"`
* Tìm mục `EXTERNAL_NET`, sửa thành: `"!$HOME_NET"`
* Tại mục `af-packet:`, kiểm tra card mạng lắng nghe lưu lượng nội bộ là `- interface: ens34`.
* **Khai báo nạp Custom Signatures (Bắt buộc):** Tìm mục `rule-files:`, thêm dòng `- local.rules` vào danh sách để Suricata nạp và thực thi các signature tự viết.

#### Bước 5: Viết Custom Signatures kiểm thử (`/var/lib/suricata/rules/local.rules`)
Mở file: `sudo nano /var/lib/suricata/rules/local.rules`:
```text
# Rule 1: Phát hiện lưu lượng Ping ICMP kiểm thử kết nối
alert icmp any any -> any any (msg:"TEST LAB - PING DETECTED"; sid:1000001; rev:1;)

# Rule 2: Phát hiện nỗ lực quét kết nối vào cổng dịch vụ SSH (TCP SYN)
alert tcp any any -> $HOME_NET 22 (msg:"TEST LAB - SSH CONNECTION ATTEMPT"; flags:S; sid:1000002; rev:1;)

# Rule 3: Phát hiện User-Agent công cụ Nmap quét do thám
alert http any any -> $HOME_NET any (msg:"TEST LAB - NMAP HTTP PROBE DETECTED"; content:"Nmap Scripting Engine"; http_user_agent; nocase; sid:1000003; rev:1;)
```
Khởi động lại Suricata: `sudo systemctl restart suricata`.

#### Bước 6: Cài đặt Wazuh Agent và Forward log `eve.json` về SIEM
1. Cài đặt Agent:
   ```bash
   curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH.gpg | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && sudo chmod 644 /usr/share/keyrings/wazuh.gpg
   echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee -a /etc/apt/sources.list.d/wazuh.list
   sudo apt update
   sudo WAZUH_MANAGER="192.168.100.10" apt install wazuh-agent -y
   ```
2. Thêm cấu hình đọc log Suricata: Mở `/var/ossec/etc/ossec.conf`, chèn thêm vào trong thẻ `<ossec_config>`:
   ```xml
   <localfile>
     <log_format>json</log_format>
     <location>/var/log/suricata/eve.json</location>
   </localfile>
   ```
3. Phân quyền thư mục và khởi động lại Agent:
   ```bash
   # Thêm user wazuh vào group suricata và mở quyền thư mục cha để tránh lỗi Permission Denied khi xoay vòng log:
   sudo usermod -aG suricata wazuh
   sudo chmod 755 /var/log/suricata
   sudo chmod 644 /var/log/suricata/eve.json
   sudo systemctl enable wazuh-agent && sudo systemctl restart wazuh-agent
   ```
   *(Kiểm tra log Agent: `sudo tail -n 20 /var/ossec/logs/ossec.log` không có dòng ERROR Permission Denied là chuẩn).*

---

### 🔴 9.3. QUY TRÌNH DÀNH CHO THÀNH VIÊN 3: TARGET ADMIN & RED TEAM LEAD
* **Phân vùng quản lý:** Máy ảo `Target-Server` (`10.0.0.10`) & `Attacker-Kali` (`192.168.100.50`)
* **Nhánh Git làm việc:** `feature/target-hardening-attacks`
* **Nhiệm vụ cốt lõi:** Cấu hình Web Server Nginx, cài Wazuh Agent bật giám sát FIM chống WebShell, định tuyến máy tấn công Kali và chạy kịch bản kiểm thử tấn công.

#### PHẦN A: THIẾT LẬP MÁY MỤC TIÊU (TARGET-SERVER)

##### Bước 1: Cấu hình mạng Netplan trỏ Gateway về Sensor
1. Tạo Linked Clone từ `Ubuntu-Template-Base`, gán card mạng **VMnet2**.
2. Soạn cấu hình: `sudo nano /etc/netplan/00-installer-config.yaml`:
   ```yaml
   network:
     version: 2
     renderer: networkd
     ethernets:
       ens33:
         addresses: [10.0.0.10/24]
         routes:
           - to: default
             via: 10.0.0.1
         nameservers:
           addresses: [8.8.8.8, 1.1.1.1]
   ```
   Áp dụng: `sudo netplan apply`.  
   *Kiểm tra thông mạng:* `ping -c 3 8.8.8.8` (Nếu không có mạng, báo Thành viên 2 kiểm tra NAT Forwarding).  
   *(Mẹo Copy/Paste: Mở PowerShell Admin trên máy thật gõ `route add 10.0.0.0 mask 255.255.255.0 192.168.100.20`, sau đó gõ `ssh ubuntu@10.0.0.10` để paste lệnh cài Nginx và Agent cực nhanh).*

##### Bước 2: Cài Nginx Web Server
```bash
sudo apt update && sudo apt install nginx -y
sudo systemctl enable nginx && sudo systemctl start nginx
```

##### Bước 3: Cài Wazuh Agent và cấu hình Giám sát Toàn vẹn Tệp (FIM)
1. Cài đặt Agent:
   ```bash
   curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH.gpg | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && sudo chmod 644 /usr/share/keyrings/wazuh.gpg
   echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee -a /etc/apt/sources.list.d/wazuh.list
   sudo apt update
   sudo WAZUH_MANAGER="192.168.100.10" apt install wazuh-agent -y
   ```
2. Cấu hình FIM giám sát thời gian thực thư mục Web: Mở `/var/ossec/etc/ossec.conf`, tìm thẻ `<syscheck>` và cấu hình:
   ```xml
   <syscheck>
     <disabled>no</disabled>
     <frequency>300</frequency>
     <scan_on_start>yes</scan_on_start>
     <!-- Giám sát thời gian thực thư mục Web Server chống WebShell -->
     <directories check_all="yes" realtime="yes" report_changes="yes">/var/www/html</directories>
   </syscheck>
   ```
3. Bật dịch vụ:
   ```bash
   sudo systemctl enable wazuh-agent && sudo systemctl restart wazuh-agent
   ```

---

#### PHẦN B: THIẾT LẬP MÁY TẤN CÔNG (ATTACKER-KALI)

##### Bước 1: Gán mạng và thêm Static Route bắt buộc
1. Gán card mạng Kali vào **VMnet8 (NAT)**, đặt IP tĩnh `192.168.100.50/24`.
2. **Lệnh sống còn:** Thêm định tuyến sang mạng nội bộ `10.0.0.0/24` qua Sensor:
   ```bash
   sudo ip route add 10.0.0.0/24 via 192.168.100.20
   ```
   *Kiểm tra kết nối:* `curl -I http://10.0.0.10` (phải trả về mã `HTTP/1.1 200 OK`).  
   *(Lưu ý: Lệnh `ip route add` nằm trong RAM, nếu Kali reboot bạn phải chạy lại hoặc đưa vào script `attack_simulation.sh`).*  
   *(Mẹo Copy/Paste: Chạy `sudo apt install -y open-vm-tools-desktop && sudo reboot` để copy-paste mượt mà trên Desktop Kali, hoặc SSH từ PowerShell máy thật `ssh kali@192.168.100.50` với pass `kali`).*

##### Bước 2: Thực thi các kịch bản kiểm thử tấn công
* **Chuẩn bị từ điển trên Kali (Bắt buộc giải nén):**
  ```bash
  # Giải nén rockyou.txt (mặc định Kali lưu dạng nén .gz):
  sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz 2>/dev/null || true
  # Hoặc tạo file từ điển nhỏ 10 mật khẩu test nhanh:
  echo -e "123456\npassword\nadmin\nubuntu\nletmein" > ~/test_pass.txt
  ```
* **Test 1 - Quét do thám:** `nmap -sS -p 22,80 10.0.0.10`
* **Test 2 - Dò mật khẩu SSH & Kích hoạt tự khóa IP:**
  ```bash
  # Nhắm vào user 'ubuntu' (tránh lỗi cấm password root mặc định của Ubuntu 22.04):
  hydra -l ubuntu -P ~/test_pass.txt ssh://10.0.0.10 -t 4
  ```
  *(Quan sát: Hydra bị timed out sau 5 lần sai, quay lại máy Target gõ `sudo iptables -L -n -v` thấy IP Kali `192.168.100.50` bị DROP).*
* **Test 3 - Tấn công Web Injection:**
  ```bash
  curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"
  ```
* **Test 4 - Tạo WebShell kiểm thử FIM:**
  ```bash
  # Trên Target tạo thử file mã độc:
  sudo bash -c 'echo "<?php system(\$_GET[\"cmd\"]); ?>" > /var/www/html/shell.php'
  # Quan sát trên Wazuh Dashboard: xuất hiện cảnh báo Integrity Checksum Changed Rule 550
  ```

---

## 10. KỊCH BẢN KIỂM THỬ THỰC NGHIỆM TẤN CÔNG - PHÒNG THỦ & MITRE ATT&CK

> **LỆNH BẮT BUỘC TRÊN KALI TRƯỚC KHI TEST:**
> ```bash
> sudo ip route add 10.0.0.0/24 via 192.168.100.20
> ```

| Kịch bản | Công cụ & Lệnh thực thi từ Kali | Khung MITRE ATT&CK | Phản ứng Suricata IDS/IPS | Phản ứng Wazuh SIEM & Active Response | Bằng chứng nghiệm thu |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **TC-01: Quét do thám** | `nmap -sS -p 22,80 10.0.0.10` | **T1046**<br>**T1595** | Bắt signature `ET SCAN Nmap Scripting Engine User-Agent` trong `eve.json` | Wazuh Dashboard hiển thị Alert Level 6-8, phân loại nhóm `reconnaissance` | Biểu đồ cảnh báo trên Dashboard nhảy số; IP chưa bị chặn |
| **TC-02: Dò mật khẩu SSH & Tự chặn** | `hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.10 -t 4` | **T1110.001** | Ghi nhận sự kiện `ET SCAN Potential SSH Scan` | **Target OS (Host Log):** Wazuh Agent đọc `/var/log/auth.log` failed 5 lần liên tiếp $\rightarrow$ kích hoạt Rule 5712 (Level 10) $\rightarrow$ gọi `firewall-drop` | Terminal Hydra báo `Connection timed out`; `iptables -L` trên Target có dòng DROP IP Kali; Telegram nhận tin báo |
| **TC-03: Tấn công Web Injection** | `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"` | **T1190** | Bắt signature `ET WEB_SERVER SQL Injection Attempt` | Kích hoạt cảnh báo Critical (Level 12+), gắn nhãn MITRE ATT&CK T1190 | Suricata ghi log alert; Telegram bắn tin cảnh báo màu đỏ tức thời |
| **TC-04: Tải WebShell & Giám sát FIM** | `echo "<?php system(\$_GET['cmd']); ?>" > /var/www/html/shell.php` | **T1505.003**<br>**T1078** | Không can thiệp (lưu lượng tải có thể mã hóa hoặc bypass qua lỗ hổng logic app) | **Wazuh FIM (Syscheck):** Quét real-time thư mục `/var/www/html/`, bắt quả tang file mới sinh $\rightarrow$ Kích hoạt Rule 550 / 554 Level 7+ | Dashboard hiển thị file bị tạo mới, mã băm sha256 và quyền sở hữu; Telegram bắn cảnh báo vi phạm toàn vẹn |

---

## 11. CHIẾN LƯỢC VẤN ĐÁP & BẢO VỆ ĐỒ ÁN NHÓM 3 NGƯỜI

Chuẩn bị trước câu trả lời cho các câu hỏi giảng viên chắc chắn sẽ hỏi từng thành viên:

### Câu hỏi cho Thành viên 1 (SIEM & Integration Lead):
* **Hỏi 1:** *"Tại sao đã có IDS/IPS rồi mà doanh nghiệp vẫn cần phải đầu tư thêm hệ thống SIEM?"*
* **Trả lời:** IDS/IPS chỉ nhìn thấy lưu lượng mạng đi qua đường truyền và phân tích độc lập từng gói tin. Nó không thể biết chuyện gì xảy ra sâu bên trong máy chủ (như log xác thực đăng nhập hỏng, tệp hệ thống bị thay đổi, tài khoản bị nâng quyền). SIEM đóng vai trò bộ não tập trung: gom cả log mạng từ Suricata và log hệ điều hành từ máy chủ về để **tương quan hóa (correlation)**. Nhờ đó ta phát hiện được các cuộc tấn công phức tạp nhiều giai đoạn (ví dụ: quét mạng bằng Nmap trước, sau đó bruteforce SSH thành công trên máy chủ).
* **Hỏi 2:** *"Hệ thống Wazuh ánh xạ các sự kiện vào khung MITRE ATT&CK như thế nào?"*
* **Trả lời:** Mỗi rule định nghĩa trong Wazuh (`ruleset`) đều được gắn kèm các thẻ metadata `<mitre><id>Txxxx</id></mitre>`. Khi log được giải mã qua decoders và khớp với rules, Wazuh Manager sẽ tự động gán nhãn Tactic và Technique tương ứng (ví dụ: Rule 5712 gắn với T1110.001 - Brute Force). Trên Dashboard, nhà phân tích có thể xem trực tiếp ma trận nhiệt (heatmap) để biết hệ thống đang bị đe dọa ở giai đoạn nào của chuỗi tấn công (Kill Chain).

### Câu hỏi cho Thành viên 2 (Network & Sensor Specialist):
* **Hỏi:** *"Sự khác biệt căn bản giữa chế độ IDS và IPS của Suricata là gì? Trong lab nhóm triển khai như thế nào?"*
* **Trả lời:** IDS chỉ đóng vai trò cảm biến thụ động (lắng nghe bản sao gói tin qua SPAN/Mirror port hoặc AF-PACKET) để phát hiện và ghi log cảnh báo mà không làm gián đoạn lưu lượng mạng. Trong khi đó, IPS đứng chắn ngang đường truyền (Inline mode / NFQUEUE), có quyền can thiệp thả (drop) gói tin độc hại ngay lập tức. Trong bài lab, nhóm sử dụng Suricata để soi chiếu sâu gói tin mạng sinh log chuẩn EVE JSON, kết hợp cơ chế Active Response của Wazuh để khóa IP vi phạm qua iptables.

### Câu hỏi cho Thành viên 3 (Target Admin & Red Team Lead):
* **Hỏi 1:** *"Cơ chế Active Response khóa IP kẻ tấn công hoạt động ra sao và làm sao để hệ thống không tự khóa chính mình?"*
* **Trả lời:** Khi Wazuh Manager phát hiện một sự kiện đạt ngưỡng vi phạm (ví dụ Rule ID 5712 khi dò pass SSH sai 5 lần), Manager sẽ phát lệnh xuống Wazuh Agent trên Target Server. Agent sẽ gọi script `firewall-drop` để thêm một dòng `DROP` chứa IP của kẻ tấn công vào đầu bảng `iptables`. Để tránh hệ thống tự khóa chính mình (tự từ chối dịch vụ), nhóm đã cấu hình danh sách loại trừ `<white_list>` trên file `ossec.conf` của Manager chứa IP của Gateway, IP của máy SIEM và dải loopback.
* **Hỏi 2:** *"Tính năng FIM (File Integrity Monitoring) phát hiện kẻ tấn công sửa đổi file hoặc tải WebShell như thế nào? Có làm nặng máy chủ không?"*
* **Trả lời:** Wazuh Agent tích hợp module `syscheck`, quét và lưu mã băm mật mã học (MD5, SHA1, SHA256) cùng thuộc tính file (quyền, kích thước, mtime) vào cơ sở dữ liệu SQLite cục bộ. Khi kết hợp cờ `realtime="yes"`, Agent sử dụng API `inotify` của nhân Linux Kernel để lắng nghe trực tiếp sự kiện tệp từ hệ điều hành ngay khi file được tạo hoặc sửa đổi mà không cần quét liên tục, do đó mức tiêu thụ CPU/RAM cực kỳ thấp ($< 1\%$).

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
│ 2. Nếu báo timeout, trên Wazuh Server mở cổng tường lửa firewalld:         │
│    sudo firewall-cmd --add-port={1514/tcp,1514/udp,1515/tcp} --permanent    │
│    sudo firewall-cmd --reload                                               │
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

---

## 15. NGUYÊN TẮC QUẢN TRỊ & PHỐI HỢP VỚI TRỢ LÝ AI (AI GOVERNANCE & WORKING WITH AI)

Dự án ứng dụng mô hình AI Agent (Google Antigravity) để hỗ trợ rà soát DevSecOps, tự động hóa kiểm định và quản trị tài liệu kỹ thuật theo thời gian thực. Toàn bộ hoạt động phối hợp tuân thủ nghiêm ngặt 4 nguyên tắc:

1. **Quyền quyết định tối cao thuộc về con người (Human-in-the-Loop Gate):**
   - AI chỉ đóng vai trò trợ lý tư vấn, phát hiện lỗ hổng logic và đề xuất văn bản. Mọi lệnh `git commit`, `git push` hoặc áp dụng cấu hình lên hạ tầng mạng đều **phải có sự phê duyệt rõ ràng từ thành viên nhóm**.
2. **Kiểm định thực tế trước tiên (Verification First):**
   - Tuyệt đối không đưa vào tài liệu những câu lệnh chưa được kiểm chứng thực tế trên cụm máy ảo VMware (ví dụ: phát hiện dịch vụ mạng thực tế là `network.service` thay vì `systemd-networkd`, hoặc cấu hình mạng đọc từ `ifcfg-eth0`).
3. **Chính sách Không lộ lọt dữ liệu (Zero-Leak Policy):**
   - Tuyệt đối không commit lên GitHub các thông tin nhạy cảm: Telegram Bot Token thật, Private Key, mật khẩu người dùng, file log dung lượng lớn (`eve.json`) hoặc ổ đĩa ảo (`.vmdk`).
4. **Cô lập cấu hình Agent cục bộ:**
   - Các file cấu hình kỹ năng Agent (`.agent/`) và file ghi nhớ lỗi/phản biện cá nhân (`prompt.md`, `promp.md`) **bắt buộc nằm trong `.gitignore`**, chỉ lưu trữ trên máy cá nhân để giữ repo sạch đẹp chuẩn mã nguồn kỹ thuật.
5. **Quy chuẩn Lưu trữ & Đóng băng phiên làm việc (Session Persistence & Anti-Hallucination):**
   - Sau mỗi phiên làm việc hoàn thành hoặc giải quyết xong một lỗi/task, **thành viên bắt buộc yêu cầu AI tóm tắt và lưu lại phiên làm việc (Session Milestone)** vào file cục bộ (ví dụ: `session_summary.md`, đã được đưa vào `.gitignore`).
   - *Mục đích phòng ngừa:* Nếu xảy ra sự cố khởi động lại máy/server, ngắt kết nối hoặc phiên chat mới bị reset ngữ cảnh (context loss), file tổng kết này sẽ đóng vai trò "mỏ neo dữ liệu thực tế" giúp AI đọc lại ngay lập tức, không bị mất toàn bộ lịch sử và tuyệt đối tránh ảo giác (hallucination) lặp lại các câu lệnh hay lỗi đã xử lý trên cụm máy ảo.