
# SOC LAB - TEAM 16
## Member 3 - Target Admin & Red Team Lead

## 1. Lab Environment

- Target: Ubuntu Server 22.04.5 LTS
- Target IP: 10.0.0.10
- Attacker: Kali Linux 2024.2
- Attacker IP: 192.168.100.50
- Sensor IP: 192.168.100.20 / 10.0.0.1
- Wazuh Manager: 192.168.100.10
- Wazuh Agent: 4.7.5
- Web Server: Nginx

## 2. Test Prerequisites

- Wazuh Manager is running.
- Suricata Sensor is running.
- Wazuh Agent is connected to Manager.
- FIM initial scan is completed.
- Kali can reach Target through Sensor.
- Temporary NAT adapter on Target is removed.

## 3. Test Cases

### TC-01: Nmap Port Scan

Objective:
Verify network scanning detection.

Source: 192.168.100.50
Destination: 10.0.0.10

Command:

    sudo nmap -sS -Pn -p 22,80 10.0.0.10

Expected:
- Nmap identifies open SSH and HTTP ports.
- Suricata detects traffic matching configured rules.
- Relevant alerts are forwarded to Wazuh.

Evidence:
- Nmap output.
- Suricata eve.json alert.
- Wazuh Dashboard alert.

Status: NOT TESTED

### TC-02: SSH Brute Force

Objective:
Verify detection of repeated SSH authentication failures.

Target account: ubuntu
Password list: ~/test_pass.txt

Command:

    hydra -l ubuntu -P ~/test_pass.txt -t 1 -f -V ssh://10.0.0.10

Expected:
- Failed login attempts appear in /var/log/auth.log.
- Wazuh detects repeated authentication failures.
- Active Response blocks the attacker if configured
  and the rule threshold is reached.

Evidence:
- Hydra output.
- Target authentication log.
- Wazuh alert.
- Active Response log and blocking result.

Status: NOT TESTED

### TC-03: SQL Injection Simulation

Objective:
Verify detection of suspicious HTTP request content.

Command:

    curl -v --max-time 10 --get --data-urlencode "id=1' OR '1'='1" "http://10.0.0.10/"

Expected:
- Nginx records the HTTP request.
- Suricata detects the SQL injection pattern if a
  matching rule is enabled.
- The corresponding alert appears in Wazuh.

Note:
The website is static. This test simulates a SQL
injection request, not a successful database exploit.

Evidence:
- Curl output.
- Nginx access.log.
- Suricata and Wazuh alerts.

Status: NOT TESTED

### TC-04: File Integrity Monitoring

Objective:
Verify realtime monitoring of /var/www/html.

Run on Target-Server:

    echo "SOC LAB FIM TEST" | sudo tee /var/www/html/fim-test.php

Modify the test file:

    echo "SOC LAB FIM MODIFIED" | sudo tee -a /var/www/html/fim-test.php

Expected:
- Wazuh detects creation of the test file.
- Wazuh detects subsequent content modification.
- File path and change details appear in Dashboard.

Cleanup:

    sudo rm /var/www/html/fim-test.php

Note:
The PHP file contains harmless text only.
It is not an executable webshell.

Evidence:
- File creation and modification commands.
- Wazuh FIM alerts.
- Dashboard screenshots.

Status: NOT TESTED

## 4. Results Summary

| Test Case | Detection | Evidence | Result |
|-----------|-----------|----------|--------|
| TC-01 | Pending | Pending | NOT TESTED |
| TC-02 | Pending | Pending | NOT TESTED |
| TC-03 | Pending | Pending | NOT TESTED |
| TC-04 | Pending | Pending | NOT TESTED |

## 5. Current Progress

- Target installation: Completed.
- Nginx and SSH: Completed.
- Wazuh Agent installation: Completed.
- FIM configuration: Completed.
- Initial FIM scan completion: Pending.
- Kali installation and network setup: Completed.
- Attack script syntax and menu: Verified.
- Manager enrollment: Pending.
- Sensor integration: Pending.
- Final lab testing: Pending.
