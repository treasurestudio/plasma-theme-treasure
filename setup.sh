#!/bin/bash

# Get the current directory path
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Update the .desktop file with the REAL path of the user
sed -i "s|Icon=.*|Icon=$DIR/logo.png|g" atmos-hub.desktop
sed -i "s|Exec=.*|Exec=python3 $DIR/main.py|g" atmos-hub.desktop
sed -i "s|Path=.*|Path=$DIR/|g" atmos-hub.desktop

# Move it to the applications folder
cp atmos-hub.desktop ~/.local/share/applications/
chmod +x main.py

echo "✅ Atmos Hub installed to your Dashboard with the correct paths!"
