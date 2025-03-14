#!/bin/bash
PHY_IF=$(route get 0.0.0.0 2>/dev/null | awk '/interface: /{print $2}')
VPN_IF=$(ifconfig -a | awk '/POINTOPOINT/{print $1; exit}')
VPN_SERVER=$(scutil --nc show "Имя VPN" | awk '/CommRemoteAddress/{print $NF}')


PF_CONF=$(mktemp)  
cat > "$PF_CONF" <<EOF
int_if = "$PHY_IF"
vpn_if = "$VPN_IF"
vpn_ip = "$VPN_SERVER"

set block-policy drop
set skip on lo0
block all
block out inet6

pass quick proto {tcp, udp} from any to any port 53 keep state
pass from any to 255.255.255.255 keep state
pass from 255.255.255.255 to any keep state
pass proto udp from any to 224.0.0.0/4 keep state
pass proto udp from 224.0.0.0/4 to any keep state
pass on $int_if proto {tcp,udp} from any port 67:68 to any port 67:68 keep state
pass on $int_if inet proto icmp all icmp-type 8 code 0 keep state
pass on $int_if proto {tcp, udp} to $vpn_ip keep state
pass on $vpn_if all keep state
EOF

sudo pfctl -Fa -f "$PF_CONF" -E
echo "Kill-switch activated (pf enabled). VPN interface: $VPN_IF, VPN server: $VPN_SERVER"















# #!/bin/bash

# # VPN Kill-Switch setup for macOS using PF
# # Blocks ALL network traffic except VPN traffic on the detected VPN interface
# # Requires sudo access

# VPN_SERVER_IP="{{VPN_SERVER_IP}}"

# if [ -z "$VPN_SERVER_IP" ]; then
#     echo "Error: No VPN server IP provided."
#     exit 1
# fi

# # Dynamically detect the VPN interface by searching for VPN_SERVER_IP in ifconfig output.
# VPN_INTERFACE=$(ifconfig | grep -B 1 "$VPN_SERVER_IP" | head -n 1 | awk '{print $1}' | sed 's/://')

# if [ -z "$VPN_INTERFACE" ]; then
#     echo "Error: VPN interface not found for IP $VPN_SERVER_IP."
#     exit 1
# fi

# ANCHOR_FILE="/etc/pf.anchors/mykillswitch"
# PF_CONF="/etc/pf.conf"

# echo "Creating PF rules to allow only VPN traffic on interface $VPN_INTERFACE..."

# sudo tee "$ANCHOR_FILE" > /dev/null <<EOF
# block all
# pass out quick on $VPN_INTERFACE
# pass out quick on en0 to $VPN_SERVER_IP port { 500, 4500, 1701 }
# EOF

# if ! grep -q 'anchor "mykillswitch"' "$PF_CONF"; then
#     echo "Adding anchor to /etc/pf.conf..."
#     echo 'anchor "mykillswitch"' | sudo tee -a "$PF_CONF" > /dev/null
# fi

# echo "Applying PF rules..."
# sudo pfctl -f "$PF_CONF"
# sudo pfctl -e

# echo "Kill-switch enabled: only VPN traffic is allowed on interface $VPN_INTERFACE."
