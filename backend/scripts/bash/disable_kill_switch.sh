#!/bin/bash

# Disable VPN Kill-Switch on macOS
# Requires sudo access

ANCHOR_FILE="/etc/pf.anchors/mykillswitch"

echo "Disabling Kill-Switch..."

sudo rm -f "$ANCHOR_FILE"
sudo pfctl -d

echo "Kill-switch disabled: all network traffic is restored."
