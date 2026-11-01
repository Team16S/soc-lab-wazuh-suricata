# HỆ THỐNG GIÁM SÁT AN NINH MẠNG TẬP TRUNG (SOC LAB)
## KẾT HỢP CENTRAL SIEM (WAZUH) VÀ NIDS/IPS (SURICATA) VỚI PHẢN ỨNG TỰ ĐỘNG

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

## 👥 3. Phân công trách nhiệm nhóm 3 người (RACI)

| Thành viên | Vai trò | Phân vùng quản trị | Nhiệm vụ chính |
| :--- | :--- | :--- | :--- |
| **Thành viên 1** | **SIEM & Integration Lead** | `Wazuh-SIEM` | Dựng Wazuh Server, cấu hình Decoder/Rules, tích hợp Telegram webhook, quản lý repo Git. |
| **Thành viên 2** | **Network & Sensor Specialist** | `Suricata-Sensor` | Cấu hình Router NAT 2 card mạng, cài đặt Suricata, viết Signatures (`local.rules`), forward log `eve.json`. |
| **Thành viên 3** | **Target Admin & Red Team** | `Target-Server` & `Kali` | Cài đặt Nginx/SSH, test Active Response khóa IP, giả lập kịch bản tấn công (Nmap, Hydra, Web Exploit). |

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

