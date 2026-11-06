#!/usr/bin/env python3
"""
Custom Integration Script: Wazuh to Discord Webhook
Gui canh bao an ninh truc quan (Discord Embed) tu Wazuh SIEM ve Discord Channel
Mien phi 100%, khong can so dien thoai hay phi SMS.
"""
import sys
import json
import requests

# Webhook URL Discord mac dinh (thay bang URL that cua ban tren may ao Wazuh)
DEFAULT_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    alert_file = sys.argv[1]

    # Lay webhook_url tu tham so dong lenh hoac dung mac dinh
    webhook_url = DEFAULT_WEBHOOK_URL
    if len(sys.argv) >= 4 and sys.argv[3] and "discord.com" in sys.argv[3]:
        webhook_url = sys.argv[3]

    if webhook_url == "YOUR_DISCORD_WEBHOOK_URL":
        # Chuoi placeholder trong repo hoac chua duoc cau hinh tren VM
        sys.exit(0)

    try:
        with open(alert_file, "r", encoding="utf-8") as f:
            alert_json = json.load(f)
    except Exception:
        sys.exit(0)

    # Trich xuat thong tin su kien an ninh
    rule = alert_json.get("rule", {})
    rule_id = rule.get("id", "N/A")
    description = rule.get("description", "Canh bao khong co mo ta")
    level = rule.get("level", 0)
    mitre_ids = rule.get("mitre", {}).get("id", [])
    if isinstance(mitre_ids, list):
        mitre_str = ", ".join(mitre_ids) if mitre_ids else "N/A"
    else:
        mitre_str = str(mitre_ids)

    agent = alert_json.get("agent", {})
    agent_name = agent.get("name", "Wazuh-Manager")
    agent_ip = agent.get("ip", "127.0.0.1")

    data = alert_json.get("data", {})
    src_ip = data.get("src_ip", alert_json.get("srcip", "N/A"))
    dest_ip = data.get("dst_ip", alert_json.get("dstip", agent_ip))

    # Xac dinh mau sac theo muc do nghiem trong (Severity Color)
    # Level >= 12: Do sam (0x8B0000), Level >= 10: Do tuoi (0xFF0000), Level >= 7: Cam (0xFFA500)
    color = 0xFF0000 if level >= 10 else 0xFFA500

    payload = {
        "username": "Wazuh SIEM Alert",
        "avatar_url": "https://wazuh.com/uploads/2022/07/wazuh-logo-blue.png",
        "embeds": [
            {
                "title": f"🚨 [LEVEL {level}] CẢNH BÁO AN NINH MẠNG",
                "description": f"**Hành vi:** {description}",
                "color": color,
                "fields": [
                    {"name": "🔢 Rule ID", "value": f"`{rule_id}`", "inline": True},
                    {"name": "🎯 Mức độ (Level)", "value": f"**{level}/15**", "inline": True},
                    {"name": "🛡️ MITRE ATT&CK", "value": f"`{mitre_str}`", "inline": True},
                    {"name": "⚠️ IP Tấn công (Source)", "value": f"`{src_ip}`", "inline": True},
                    {"name": "🖥️ Mục tiêu (Target)", "value": f"`{dest_ip}` ({agent_name})", "inline": True},
                ],
                "footer": {
                    "text": "SOC Lab Team16S - Centralized Wazuh SIEM Monitoring"
                }
            }
        ]
    }

    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception:
        pass

if __name__ == "__main__":
    main()
