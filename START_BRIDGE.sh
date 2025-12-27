#!/bin/bash
echo "🚀 Launching Nobara Atmos Bridge..."
# Using full paths so it never breaks again
python3 /home/john/nobara-atmos-bridge/src/bridge_monitor.py &
python3 /home/john/nobara-atmos-bridge/src/main.py
