#!/bin/bash

# Only God knows what this script does.

# enable_kill_switch.sh
#
# Must be run with bash (not sh)!
# Kill-switch setup for macOS using PF.
# Blocks ALL network traffic except traffic going through the detected PPP/UTUN interface.
# This script:
# 1) Detects the default (physical) interface for outgoing Internet (via route get 0.0.0.0).
# 2) Finds the actual VPN interface among POINTOPOINT interfaces (e.g. ppp0, utun0)
#    by looking for 'inet <IP>' in ifconfig output.
# 3) Generates a temporary PF config blocking all traffic except DNS, DHCP, ICMP echo,
#    and traffic specifically over the VPN interface or to the local VPN IP for IPSec/L2TP ports.
#
# Usage:
#   sudo ./enable_kill_switch.sh
# or configure sudoers to avoid password prompts.

# 1) Detect physical interface
PHY_IF=$(route get 0.0.0.0 2>/dev/null | awk '/interface: /{print $2}')
if [ -z "$PHY_IF" ]; then
    echo "Error: Could not detect physical interface (route get)."
    exit 1
fi

VPN_IF=""
VPN_LOCAL_IP=""

# 2) Among all POINTOPOINT interfaces (pppX, utunX, gif0, etc.), find the one with a valid inet address
IFACES=$(ifconfig -a | awk '/POINTOPOINT/{print $1}')
for iface in $IFACES; do
    clean_iface=$(echo "$iface" | sed 's/://')         # Remove trailing colon (if any), e.g. "ppp0:" -> "ppp0"
    ip=$(ifconfig "$clean_iface" 2>/dev/null | awk '/inet /{print $2}')  # e.g. "10.236.6.43"
    if [ -n "$ip" ]; then
        VPN_IF="$clean_iface"
        VPN_LOCAL_IP="$ip"
        break
    fi
done

if [ -z "$VPN_IF" ]; then
    echo "Error: No suitable VPN interface found (ppp0, utunX, etc.)."
    exit 1
fi

echo "Detected VPN interface: $VPN_IF, local IP: $VPN_LOCAL_IP"

# 3) Create temporary PF config
PF_CONF=$(mktemp)
cat > "$PF_CONF" <<EOF
int_if = "$PHY_IF"
vpn_if = "$VPN_IF"
vpn_ip = "$VPN_LOCAL_IP"

set block-policy drop
set skip on lo0
block all
block out inet6

# Allow DNS lookups (UDP/TCP 53), DHCP, some broadcast traffic:
pass quick proto {tcp,udp} from any to any port 53 keep state
pass from any to 255.255.255.255 keep state
pass from 255.255.255.255 to any keep state
pass proto udp from any to 224.0.0.0/4 keep state
pass proto udp from 224.0.0.0/4 to any keep state
pass on \$int_if proto {tcp,udp} from any port 67:68 to any port 67:68 keep state
pass on \$int_if inet proto icmp all icmp-type 8 code 0 keep state

# Allow traffic to the local VPN IP for L2TP/IPsec (ports 500, 4500, 1701):
pass on \$int_if proto {tcp, udp} to \$vpn_ip port { 500, 4500, 1701 } keep state

# Allow all traffic on the VPN interface:
pass on \$vpn_if all keep state
EOF

sudo pfctl -Fa -f "$PF_CONF" -E || {
    echo "Failed to load PF rules."
    exit 1
}

echo "Kill-switch activated (PF enabled)."
echo "VPN interface: $VPN_IF, local IP: $VPN_LOCAL_IP"
