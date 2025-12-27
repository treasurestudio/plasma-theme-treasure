#!/bin/bash
# Forces the script to move to the project folder first
cd /home/john/nobara-atmos-bridge

echo "------------------------------------------"
echo "   NOBARA ATMOS BRIDGE: STARTING UP      "
echo "------------------------------------------"

# Launch the monitor and hub using the full system path
python3 /home/john/nobara-atmos-bridge/src/bridge_monitor.py &
python3 /home/john/nobara-atmos-bridge/src/main.py
