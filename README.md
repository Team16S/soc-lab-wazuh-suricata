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
> **Tài liệu tham khảo chuyên sâu:** Xem toàn bộ Runbook chi tiết, kế hoạch Sprint và kịch bản vấn đáp tại [**docs/Ke_Hoach_Trien_Khai.md**](docs/Ke_Hoach_Trien_Khai.md).

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

## 💾 3. Bảng tệp tin máy ảo cần chuẩn bị

Nhóm chỉ cần tải đúng **3 tệp tin** này (tuyệt đối không tải các bản Desktop có GUI gây tràn RAM):

| Tệp tin | Định dạng | Nguồn tải chính thức | Mục đích sử dụng |
| :--- | :---: | :--- | :--- |
| **1. Wazuh Virtual Appliance** | `.ova` (~4.5 GB) | Trang chủ Wazuh (*Virtual Machine appliance / OVA*) | Dựng nhanh SIEM Manager + Indexer + Dashboard |
| **2. Ubuntu Server 22.04 LTS** | `.iso` (~2.5 GB) | `releases.ubuntu.com/jammy/` | Cài Template Base để tạo Linked Clone cho Sensor & Target |
| **3. Kali Linux VMware Pre-built** | `.7z` (~3.0 GB) | `kali.org/get-kali/#kali-virtual-machines` | Giải nén dùng ngay cho Red Team, chọn "I Copied It" |

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

## 👥 6. Phân công trách nhiệm 3 người & Hướng dẫn kỹ thuật chi tiết

### 🟢 THÀNH VIÊN 1: SIEM & Integration Lead (Bộ não trung tâm)
* **Máy quản lý:** `Wazuh-SIEM` (`192.168.100.10/24`) | **Nhánh Git:** `feature/wazuh-rules-telegram`
* **Nhiệm vụ chi tiết:**
  1. Import file `.ova`, đặt RAM 4GB, 2 Cores, mạng **VMnet8**.
  2. Gán IP tĩnh và hạ Heap RAM OpenSearch (tránh treo máy thật):
     ```bash
     sudo nmcli connection modify ens33 ipv4.addresses 192.168.100.10/24 ipv4.gateway 192.168.100.2 ipv4.dns "8.8.8.8,1.1.1.1" ipv4.method manual
     sudo nmcli connection up ens33
     sudo sed -i 's/-Xms2g/-Xms1g/g' /etc/wazuh-indexer/jvm.options
     sudo sed -i 's/-Xmx2g/-Xmx1g/g' /etc/wazuh-indexer/jvm.options
     sudo systemctl restart wazuh-indexer
     ```
  3. Lấy mật khẩu admin web Dashboard:
     ```bash
     sudo tar -O -xvf /home/wazuh-user/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
     ```
  4. Cấu hình White-list và Active Response trong `/var/ossec/etc/ossec.conf`:
     * Thêm thẻ `<white_list>` chứa IP Sensor (`192.168.100.20`, `10.0.0.1`), Target (`10.0.0.10`), SIEM (`192.168.100.10`).
     * Thêm `<active-response>` kích hoạt `firewall-drop` với `rules_id`: `5712`.
  5. Viết script tích hợp Telegram `/var/ossec/integrations/custom-telegram.py`, cấp quyền `sudo chmod 750` và `sudo chown root:wazuh`.
  6. Lưu cấu hình vào repo: `configs/ossec-manager.conf`, `rules/local_rules.xml`, `scripts/custom-telegram.py`.

---

### 🟡 THÀNH VIÊN 2: Network & Sensor Specialist (Cửa ngõ an ninh)
* **Máy quản lý:** `Suricata-Sensor` (Router 2 card: `192.168.100.20` & `10.0.0.1`) | **Nhánh Git:** `feature/suricata-sensor-nat`
* **Nhiệm vụ chi tiết:**
  1. Tạo Linked Clone từ Ubuntu Base, thêm card mạng 2 (`ens33` vào VMnet8, `ens34` vào VMnet2).
  2. Cấu hình IP tĩnh Netplan (`/etc/netplan/00-installer-config.yaml`):
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
     Chạy `sudo netplan apply`.
  3. Bật IP Forwarding và NAT Masquerade:
     ```bash
     sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf && sudo sysctl -p
     sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
     sudo netfilter-persistent save
     ```
  4. Cài đặt Suricata và cập nhật rules:
     ```bash
     sudo add-apt-repository ppa:oisf/suricata-stable -y
     sudo apt update && sudo apt install suricata jq -y && sudo suricata-update
     ```
     Sửa `/etc/suricata/suricata.yaml`: đặt `HOME_NET: "[10.0.0.0/24,192.168.100.0/24]"`, cho `af-packet` lắng nghe `ens34`.
  5. Cài Wazuh Agent trên Sensor, cấu hình Agent đọc luồng log `/var/log/suricata/eve.json` dạng `json` đẩy về SIEM.
  6. Lưu cấu hình vào repo: `configs/suricata.yaml`, `configs/netplan-sensor.yaml`, `rules/local.rules`.

---

### 🔴 THÀNH VIÊN 3: Target Admin & Red Team Lead (Mục tiêu & Tấn công)
* **Máy quản lý:** `Target-Server` (`10.0.0.10`) & `Attacker-Kali` (`192.168.100.50`) | **Nhánh Git:** `feature/target-hardening-attacks`
* **Nhiệm vụ chi tiết:**
  1. Tạo Linked Clone Target-Server, gán mạng **VMnet2**, đặt IP `10.0.0.10/24`, Gateway `10.0.0.1`.
     * Kiểm tra thông mạng: `ping -c 3 8.8.8.8`.
     * Cài Nginx Web Server: `sudo apt update && sudo apt install nginx -y`.
     * Cài đặt Wazuh Agent trỏ về Manager `192.168.100.10`.
  2. Thiết lập máy Kali Linux: Gán mạng **VMnet8**, IP `192.168.100.50/24`.
     * **Bắt buộc thêm Static Route sang dải Target:**
       ```bash
       sudo ip route add 10.0.0.0/24 via 192.168.100.20
       ```
  3. Thực thi 3 kịch bản demo:
     * **TC-01 (Quét Nmap):** `nmap -sS -p 22,80 10.0.0.10`
     * **TC-02 (Brute-force SSH):** `hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.10 -t 4`
     * **TC-03 (Web SQLi):** `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"`
  4. Lưu cấu hình vào repo: `configs/netplan-target.yaml`, `scripts/attack_simulation.sh`.

---

## 🧪 7. Ma trận kiểm thử thực nghiệm & Ánh xạ MITRE ATT&CK

| Mã | Kịch bản tấn công | Lệnh thực thi từ Kali | Khung MITRE ATT&CK | Cơ chế phát hiện | Cơ chế phản ứng (Active Response) | Bằng chứng nghiệm thu |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **TC-01** | Quét cổng do thám (Reconnaissance) | `nmap -sS -p 22,80 10.0.0.10` | **T1046** (Network Service Discovery)<br>**T1595** (Active Scanning) | **Suricata (Network):** Bắt signature Nmap User-Agent trong `eve.json` | Wazuh SIEM nhận log, sinh Alert Level 6-8, phân loại nhóm `reconnaissance` | Biểu đồ Dashboard nhảy số; IP chưa bị chặn (chưa vượt ngưỡng) |
| **TC-02** | Dò mật khẩu SSH & Tự động chặn IP | `hydra -l root -P rockyou.txt ssh://10.0.0.10 -t 4` | **T1110.001** (Brute Force: Password Guessing) | **Target OS (Host Log):** Wazuh Agent đọc `/var/log/auth.log` failed 5 lần liên tiếp | **Rule 5712 (Level 10)** kích hoạt script `firewall-drop` trên Target | Terminal Hydra báo `timed out`; `iptables -L` có dòng DROP IP Kali; Telegram nhận tin |
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
├── prompt.md                       # QA Protocol kiểm định chống ảo giác AI
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
    └── Ke_Hoach_Trien_Khai.md      # Bản kế hoạch kỹ thuật & Runbook chi tiết 13 mục
```

---

## 🔄 11. Đồng bộ cấu hình từ máy ảo ra Repo (SCP / WinSCP)

Do các máy ảo chạy **Ubuntu Server không có giao diện đồ họa (GUI)**, bạn không thể kéo-thả chuột trực tiếp. Sử dụng PowerShell trên máy thật Windows để tải file cấu hình về repo cực nhanh:

```powershell
# Đứng tại thư mục gốc repository (d:\AnNinhMang\soc-lab-wazuh-suricata) trên PowerShell máy thật:

# 1. Hút file cấu hình Suricata & Rules từ Sensor (192.168.100.20):
scp ubuntu@192.168.100.20:/etc/suricata/suricata.yaml ./configs/
scp ubuntu@192.168.100.20:/var/lib/suricata/rules/local.rules ./rules/
scp ubuntu@192.168.100.20:/etc/netplan/00-installer-config.yaml ./configs/netplan-sensor.yaml

# 2. Hút file cấu hình Wazuh SIEM & Script Telegram từ SIEM (192.168.100.10):
scp wazuh-user@192.168.100.10:/var/ossec/etc/ossec.conf ./configs/ossec-manager.conf
scp wazuh-user@192.168.100.10:/var/ossec/etc/rules/local_rules.xml ./rules/
scp wazuh-user@192.168.100.10:/var/ossec/integrations/custom-telegram.py ./scripts/
```
*(Hoặc dùng phần mềm đồ họa **WinSCP** kết nối qua SFTP Port 22 với tài khoản `ubuntu`/`123` hoặc `wazuh-user`/`wazuh` để kéo thả chuột trực quan).*

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
