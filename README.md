# HỆ THỐNG GIÁM SÁT AN NINH MẠNG TẬP TRUNG (SOC LAB)
## KẾT HỢP CENTRAL SIEM (WAZUH) VÀ NIDS/IPS (SURICATA) VỚI PHẢN ỨNG TỰ ĐỘNG

[![SOC Lab CI - Syntax & Security Check](https://github.com/USERNAME_OR_ORG/soc-lab-wazuh-suricata/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME_OR_ORG/soc-lab-wazuh-suricata/actions/workflows/ci.yml)
![Defense-in-Depth](https://img.shields.io/badge/Security-Defense--in--Depth-blue)
![Platform](https://img.shields.io/badge/Platform-VMware%20Workstation-orange)

> **Đồ án môn học:** An ninh mạng  
> **Mô hình triển khai:** Ảo hóa trên nền tảng VMware Workstation  
> **Cơ cấu nhóm:** 03 thành viên  

---

## 📌 1. Giới thiệu tổng quan
Dự án xây dựng một trung tâm điều hành an ninh mạng (SOC) thu nhỏ hoàn chỉnh, bảo vệ đa tầng theo chiều sâu (Defense-in-Depth):
* **Tầng mạng (Network Layer):** Triển khai **Suricata IDS/IPS** tại gateway để soi chiếu gói tin theo thời gian thực (Deep Packet Inspection), phát hiện dò quét, khai thác lỗ hổng và xuất log `eve.json`.
* **Tầng máy chủ (Host Layer):** Triển khai **Wazuh Agent** trên các node để giám sát tiến trình, file integrity (FIM), audit log và xác thực hệ thống.
* **Tầng điều phối trung tâm (Central SIEM):** **Wazuh Manager + Indexer + Dashboard** tương quan hóa sự kiện theo chuẩn **MITRE ATT&CK**.
* **Tầng phản ứng tự động (Active Response):** Tự động phát lệnh khóa IP kẻ tấn công qua `iptables` ngay khi đạt ngưỡng vi phạm và gửi cảnh báo tức thời qua **Telegram Bot**.

---

## 🌐 2. Kiến trúc mạng & Thông số kỹ thuật

### Sơ đồ topology mạng
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
               │   IP (ens33): 10.0.0.10         │
               │   Nginx + SSH + Wazuh Agent     │
               └─────────────────────────────────┘
                                ▲
                                │ Đẩy log xác thực & cảnh báo
                                │
┌──────────────────────────────┴───────────────────────────────┐
│                     Wazuh-SIEM Server                        │
│   IP: 192.168.100.10 (VMnet8)                                │
│   Wazuh Manager + Indexer + Dashboard + Telegram Integration  │
└──────────────────────────────────────────────────────────────┘
```

### Bảng phân bổ địa chỉ IP
| Máy ảo | Vai trò | Card mạng | IP Tĩnh | Gateway | Dịch vụ chính |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wazuh-SIEM** | Central SIEM | VMnet8 | `192.168.100.10/24` | `192.168.100.2` | Dashboard (443), Agent Reg (1514, 1515) |
| **Suricata-Sensor** | Gateway IDS/IPS | VMnet8 + VMnet2 | `ens33`: `192.168.100.20`<br>`ens34`: `10.0.0.1` | `192.168.100.2` | Suricata, NAT Forwarding, Wazuh Agent |
| **Target-Server** | Nơi bị tấn công | VMnet2 | `10.0.0.10/24` | `10.0.0.1` | Nginx (80), SSH (22), Wazuh Agent |
| **Attacker-Kali** | Red Team | VMnet8 | `192.168.100.50/24` | `192.168.100.2` | Nmap, Hydra, SQLMap |

---

## 👥 3. Phân công trách nhiệm nhóm 3 người & Hướng dẫn chi tiết

> 📖 **Tài liệu tham khảo chuyên sâu:** Xem toàn bộ Runbook thiết lập máy ảo VMware, kịch bản vấn đáp và kế hoạch Sprint tại [**docs/Ke_Hoach_Trien_Khai.md**](docs/Ke_Hoach_Trien_Khai.md).

---

### 🟢 THÀNH VIÊN 1: SIEM & Integration Lead (Bộ não trung tâm)
* **Phân vùng quản lý:** Máy ảo `Wazuh-SIEM` (IP: `192.168.100.10/24`)
* **Nhánh Git làm việc:** `feature/wazuh-rules-telegram`
* **Các bước triển khai chi tiết:**
  1. **Khởi tạo máy ảo Wazuh:** Import file OVA vào VMware, gán RAM 4GB, 2 CPU, card mạng **VMnet8**.
  2. **Cấu hình IP tĩnh & Hạ RAM Java:**
     ```bash
     # Đặt IP tĩnh cho Wazuh Manager
     sudo nmcli connection modify ens33 ipv4.addresses 192.168.100.10/24 ipv4.gateway 192.168.100.2 ipv4.dns "8.8.8.8,1.1.1.1" ipv4.method manual
     sudo nmcli connection up ens33
     # Giảm tải RAM Heap Size tránh treo máy thật
     sudo sed -i 's/-Xms2g/-Xms1g/g' /etc/wazuh-indexer/jvm.options
     sudo sed -i 's/-Xmx2g/-Xmx1g/g' /etc/wazuh-indexer/jvm.options
     sudo systemctl restart wazuh-indexer
     ```
  3. **Lấy mật khẩu tài khoản Admin Dashboard:**
     ```bash
     sudo tar -O -xvf /home/wazuh-user/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
     ```
  4. **Cấu hình White-list & Phản ứng tự động (`/var/ossec/etc/ossec.conf`):**
     * Thêm IP Sensor (`192.168.100.20`, `10.0.0.1`), Target (`10.0.0.10`) và SIEM (`192.168.100.10`) vào thẻ `<white_list>` để tránh tự khóa chính mình.
     * Cấu hình Active Response gọi `firewall-drop` khi phát hiện Rule 5712 (dò pass SSH) hoặc Rule 100002.
  5. **Tích hợp Webhook Telegram:**
     * Viết script `/var/ossec/integrations/custom-telegram.py` và lưu bản sao vào `scripts/custom-telegram.py`.
     * Phân quyền thực thi: `sudo chmod 750 /var/ossec/integrations/custom-telegram.py && sudo chown root:wazuh /var/ossec/integrations/custom-telegram.py`.
  6. **Đẩy cấu hình lên Git:** Lưu cấu hình vào `configs/ossec-manager.conf` và `rules/local_rules.xml`.

---

### 🟡 THÀNH VIÊN 2: Network & Sensor Specialist (Cửa ngõ an ninh)
* **Phân vùng quản lý:** Máy ảo `Suricata-Sensor` (Router 2 card: `192.168.100.20` & `10.0.0.1`)
* **Nhánh Git làm việc:** `feature/suricata-sensor-nat`
* **Các bước triển khai chi tiết:**
  1. **Tạo máy từ Template:** Tạo Linked Clone từ Ubuntu Base, thêm card mạng 2:
     * Card 1 (`ens33`): VMnet8 (NAT).
     * Card 2 (`ens34`): VMnet2 (Host-only).
  2. **Cấu hình Netplan & Kích hoạt Router NAT:**
     ```bash
     # Sửa /etc/netplan/00-installer-config.yaml (xem mẫu trong configs/netplan-sensor.yaml)
     sudo netplan apply
     # Bật IP Forwarding
     sudo sysctl -w net.ipv4.ip_forward=1
     echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
     # Bật NAT Masquerade ra Internet
     sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
     sudo netfilter-persistent save
     ```
  3. **Cài đặt & Cấu hình Suricata:**
     ```bash
     sudo add-apt-repository ppa:oisf/suricata-stable -y
     sudo apt update && sudo apt install suricata jq -y
     sudo suricata-update
     ```
     * Chỉnh file `/etc/suricata/suricata.yaml`: cấu hình `HOME_NET: "[10.0.0.0/24,192.168.100.0/24]"` và cho `af-packet` lắng nghe card mạng nội bộ (`ens34`).
  4. **Viết Custom Signatures (`/var/lib/suricata/rules/local.rules`):**
     * Thêm rule phát hiện ICMP Ping, Nmap Scan, SQLi vào `rules/local.rules`.
     * Kiểm tra log sinh ra: `tail -f /var/log/suricata/eve.json`.
  5. **Đẩy log Suricata về Wazuh SIEM:**
     * Cài `wazuh-agent` trỏ về Manager `192.168.100.10`.
     * Thêm cấu hình đọc file `/var/log/suricata/eve.json` dạng `json` vào file `/var/ossec/etc/ossec.conf`.
  6. **Đẩy cấu hình lên Git:** Lưu vào `configs/suricata.yaml` và `configs/netplan-sensor.yaml`.

---

### 🔴 THÀNH VIÊN 3: Target Admin & Red Team Lead (Mục tiêu & Tấn công)
* **Phân vùng quản lý:** Máy ảo `Target-Server` (`10.0.0.10`) & `Attacker-Kali` (`192.168.100.50`)
* **Nhánh Git làm việc:** `feature/target-hardening-attacks`
* **Các bước triển khai chi tiết:**
  1. **Thiết lập máy mục tiêu Target-Server:**
     * Tạo Linked Clone từ Ubuntu Base, gắn card mạng **VMnet2**.
     * Đặt IP tĩnh `10.0.0.10/24`, Gateway trỏ về Sensor: `10.0.0.1`.
     * Kiểm tra thông mạng: `ping -c 3 8.8.8.8` (nếu không thông, báo Thành viên 2 kiểm tra NAT).
     * Cài đặt Nginx làm Web mục tiêu: `sudo apt update && sudo apt install nginx -y`.
     * Cài đặt `wazuh-agent`, kích hoạt dịch vụ kết nối về Manager `192.168.100.10`.
  2. **Thiết lập máy tấn công Kali Linux:**
     * Gắn card mạng **VMnet8**, đặt IP tĩnh `192.168.100.50/24`.
     * **Bắt buộc thêm Static Route sang dải Target:**
       ```bash
       sudo ip route add 10.0.0.0/24 via 192.168.100.20
       ```
     * Kiểm tra kết nối tới web target: `curl -I http://10.0.0.10`.
  3. **Thực thi 3 kịch bản tấn công kiểm thử:**
     * **Test 1 (Reconnaissance):** `nmap -sS -p 22,80 10.0.0.10`.
     * **Test 2 (SSH Brute-force & Trigger Active Response):**
       ```bash
       hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.10 -t 4
       ```
       *Xác minh:* Kiểm tra terminal Hydra bị `timed out`, trên máy Target chạy `sudo iptables -L -n -v` thấy IP Kali bị `DROP`.
     * **Test 3 (Web Injection):** `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"`.
  4. **Viết script tự động hóa:** Lưu script tấn công vào `scripts/attack_simulation.sh`.
  5. **Đẩy cấu hình lên Git:** Lưu `configs/netplan-target.yaml` và `scripts/attack_simulation.sh`.

---

## 📂 4. Cấu trúc thư mục kho lưu trữ
```text
soc-lab-wazuh-suricata/
├── .gitignore                      # Chặn commit máy ảo, log rác, credentials
├── README.md                       # Tài liệu tổng quan kiến trúc và hướng dẫn lab
├── configs/
│   ├── suricata.yaml               # Cấu hình Suricata Engine
│   ├── netplan-sensor.yaml         # Cấu hình mạng 2 card trên Sensor
│   ├── netplan-target.yaml         # Cấu hình mạng trỏ Gateway trên Target
│   ├── ossec-agent-sensor.conf     # Agent cấu hình đọc eve.json
│   └── ossec-manager.conf          # Cấu hình Active Response & Telegram
├── rules/
│   ├── local.rules                 # Signatures riêng của Suricata
│   └── local_rules.xml             # Rules phát hiện và nâng mức cảnh báo của Wazuh
├── scripts/
│   ├── custom-telegram.py          # Script Webhook bắn cảnh báo Telegram
│   └── attack_simulation.sh        # Script giả lập tấn công tự động
└── docs/
    └── topology.png                # Hình ảnh sơ đồ mạng hệ thống
```

---

## 🚀 5. Hướng dẫn thiết lập & Vận hành nhanh

### Bước 1: Chuẩn bị mạng ảo trên VMware
1. Mở **Virtual Network Editor**:
   * **VMnet8 (NAT):** Subnet IP `192.168.100.0`, Gateway `192.168.100.2`.
   * **VMnet2 (Host-only):** Subnet IP `10.0.0.0`, **bỏ tích DHCP**.

### Bước 2: Kích hoạt Router NAT trên Suricata Sensor
```bash
# Bật IP Forwarding
sudo sysctl -w net.ipv4.ip_forward=1
# Bật NAT Masquerade
sudo iptables -t nat -A POSTROUTING -o ens33 -j MASQUERADE
sudo netfilter-persistent save
```

### Bước 3: Định tuyến tĩnh trên Kali Linux
> ⚠️ **Bắt buộc chạy lệnh này trên Kali trước khi thực hiện tấn công:**
```bash
sudo ip route add 10.0.0.0/24 via 192.168.100.20
```

---

## 🧪 6. Kịch bản kiểm thử Demo (Test Cases)

| Mã | Kịch bản | Lệnh thực thi từ Kali | Cơ chế phản hồi | Kết quả mong đợi |
| :---: | :--- | :--- | :--- | :--- |
| **TC-01** | Quét cổng do thám | `nmap -sS -p 22,80 10.0.0.10` | Suricata nhận diện chữ ký Nmap | Xuất hiện cảnh báo trên Wazuh Dashboard |
| **TC-02** | Dò mật khẩu SSH & Tự chặn | `hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.10 -t 4` | Wazuh kích hoạt Active Response Rule 5712 | IP Kali bị `iptables DROP`, Telegram nhận tin nhắn |
| **TC-03** | Tấn công Web SQLi | `curl "http://10.0.0.10/?id=1'%20OR%20'1'='1"` | Suricata bắt signature SQL Injection | Wazuh sinh alert Critical (Level 12+) |

---

## 🛠️ 7. Xử lý sự cố thường gặp (Troubleshooting)
1. **Target không ra được Internet:** Kiểm tra `cat /proc/sys/net/ipv4/ip_forward` trên Sensor xem đã bằng `1` chưa.
2. **Wazuh Agent không kết nối:** Mở cổng UFW trên SIEM: `sudo ufw allow 1514/tcp && sudo ufw allow 1515/tcp`.
3. **Bị khóa nhầm IP chính mình:** Mở console máy Target chạy `sudo iptables -F` để xả toàn bộ rule DROP.
4. **Ổ cứng Sensor bị đầy:** Chạy lệnh làm rỗng log: `sudo truncate -s 0 /var/log/suricata/eve.json`.

---
*Tài liệu thuộc đồ án môn học An toàn mạng - Lưu hành nội bộ nhóm.*

