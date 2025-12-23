#!/bin/bash

# Navigate to the source directory
cd "$(dirname "$0")/src/bridge"

# Check if PipeWire is running (essential for Nobara Audio)
if ! pgrep -x "pipewire" > /dev/null
then
    echo "ERROR: PipeWire is not running. Audio Bridge cannot initialize."
    exit 1
fi

# Run the Bridge
echo "Initializing Nobara Atmos Bridge..."
python3 main.py
