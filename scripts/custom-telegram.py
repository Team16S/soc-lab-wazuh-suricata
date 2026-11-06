#!/usr/bin/env python3
import sys
import json
import requests

# Token Bot va Chat ID Telegram gia dinh cho moi truong Lab / Mau code
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

if len(sys.argv) < 2:
    sys.exit(1)

alert_file = sys.argv[1]
with open(alert_file, "r", encoding="utf-8") as f:
    alert_json = json.load(f)

rule_id = alert_json.get("rule", {}).get("id", "N/A")
description = alert_json.get("rule", {}).get("description", "N/A")
level = alert_json.get("rule", {}).get("level", 0)
src_ip = alert_json.get("data", {}).get("src_ip", alert_json.get("srcip", "N/A"))

message = (
    f"🚨 *CẢNH BÁO AN NINH MẠNG (SIEM)* 🚨\n\n"
    f"📌 *Hành vi:* {description}\n"
    f"🔢 *Rule ID:* {rule_id} | *Mức độ (Level):* {level}\n"
    f"🎯 *IP Nguồn Tấn Công:* `{src_ip}`\n"
)

if BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN":
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception:
        pass
