#!/bin/bash

# VPN Kill-Switch setup for macOS using PF
# Blocks ALL network traffic except VPN traffic on the detected VPN interface
# Requires sudo access

VPN_SERVER_IP="{{VPN_SERVER_IP}}"

if [ -z "$VPN_SERVER_IP" ]; then
    echo "Error: No VPN server IP provided."
    exit 1
fi

# Dynamically detect the VPN interface by searching for VPN_SERVER_IP in ifconfig output.
VPN_INTERFACE=$(ifconfig | grep -B 1 "$VPN_SERVER_IP" | head -n 1 | awk '{print $1}' | sed 's/://')

if [ -z "$VPN_INTERFACE" ]; then
    echo "Error: VPN interface not found for IP $VPN_SERVER_IP."
    exit 1
fi

ANCHOR_FILE="/etc/pf.anchors/mykillswitch"
PF_CONF="/etc/pf.conf"

echo "Creating PF rules to allow only VPN traffic on interface $VPN_INTERFACE..."

sudo tee "$ANCHOR_FILE" > /dev/null <<EOF
block all
pass out quick on $VPN_INTERFACE
pass out quick on en0 to $VPN_SERVER_IP port { 500, 4500, 1701 }
EOF

if ! grep -q 'anchor "mykillswitch"' "$PF_CONF"; then
    echo "Adding anchor to /etc/pf.conf..."
    echo 'anchor "mykillswitch"' | sudo tee -a "$PF_CONF" > /dev/null
fi

echo "Applying PF rules..."
sudo pfctl -f "$PF_CONF"
sudo pfctl -e

echo "Kill-switch enabled: only VPN traffic is allowed on interface $VPN_INTERFACE."
