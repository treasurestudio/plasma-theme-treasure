#!/bin/bash
# 1. Enter the directory
cd /home/john/nobara-atmos-bridge/src/bridge

# 2. Setup environment
export PYTHONPATH=$PYTHONPATH:.
export WINEASIO_NUMBER_OUTPUTS=8
export PIPEWIRE_LATENCY="512/48000"
export WINE_LARGE_ADDRESS_AWARE=1

# 3. Clean up any old "ghost" sinks before starting
pactl unload-module module-null-sink 2>/dev/null

# 4. Start the Bridge with High Priority
# The screen brightness change confirms this is working!
nice -n -10 python3 main.py
