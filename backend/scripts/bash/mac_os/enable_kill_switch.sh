#!/bin/bash

#!!! This script still doesn't wanna to work due to Apple inner restrictions, it's fucking crazy. !!!#

# enable_kill_switch.sh
#
# Must be run with bash (not sh)!
# "Universal partial kill-switch" for macOS using PF.
#
# Steps:
# 1) Detect default physical interface (PHY_IF) and gateway (via route get 0.0.0.0).
# 2) Parse DNS servers from scutil --dns (any system config).
# 3) Find the VPN interface among POINTOPOINT (ppp0, utunX) by ifconfig lines.
# 4) Extract local/remote IP from "inet x.x.x.x --> y.y.y.y netmask ...".
# 5) Generate PF rules:
#    - pass DNS to discovered servers on port 53
#    - pass minimal traffic (DHCP, broadcast, ICMP)
#    - pass L2TP/IPSec traffic to remote IP (ports 500,4500,1701)
#    - pass all on the VPN interface
#    - block everything else
#
# This allows any DNS config that macOS is actually using (not just local router).
# So the user doesn't have to specify or guess if they use 8.8.8.8 or 192.168.0.1.

# Make sure we run under bash:
if [[ -z "$BASH_VERSION" ]]; then
  echo "Please run this script with bash, not sh."
  exit 1
fi

########################################
# 1) Physical interface + gateway
########################################

PHY_IF=$(route get 0.0.0.0 2>/dev/null | awk '/interface: /{print $2}')
if [ -z "$PHY_IF" ]; then
  echo "Error: Could not detect physical interface (route get)."
  exit 1
fi

PHY_GW=$(route -n get 0.0.0.0 2>/dev/null | awk '/gateway: /{print $2}')
echo "Physical interface: $PHY_IF"
echo "Physical gateway:   $PHY_GW"

########################################
# 2) Collect DNS servers from scutil --dns
########################################

DNS_SERVERS=()
while IFS= read -r dnsip; do
  DNS_SERVERS+=("$dnsip")
done < <(scutil --dns | awk '/nameserver\[[0-9]+\] : / {print $NF}' | sort -u)

echo "Discovered DNS servers: ${DNS_SERVERS[*]:-(none)}"

########################################
# 3) Find the VPN interface (ppp0, utunX, etc.)
########################################

VPN_IF=""
VPN_LOCAL_IP=""
VPN_REMOTE_IP=""

IFACES=$(ifconfig -a | awk '/POINTOPOINT/{print $1}')
for iface in $IFACES; do
  clean_iface=$(echo "$iface" | sed 's/://')
  line=$(ifconfig "$clean_iface" 2>/dev/null | awk '/inet /{print $2 " " $3 " " $4 " " $5}')
  if [ -n "$line" ]; then
    VPN_LOCAL_IP=$(echo "$line" | awk '{print $1}')
    VPN_REMOTE_IP=$(echo "$line" | awk '{print $3}')
    # fallback parse if needed
    if [[ "$VPN_REMOTE_IP" == "netmask" || -z "$VPN_REMOTE_IP" ]]; then
      VPN_REMOTE_IP=$(ifconfig "$clean_iface" 2>/dev/null | sed -nE 's/.*inet ([0-9\.]+) --> ([0-9\.]+).*/\2/p')
    fi
    if [ -n "$VPN_LOCAL_IP" ] && [ -n "$VPN_REMOTE_IP" ]; then
      VPN_IF="$clean_iface"
      break
    fi
  fi
done

if [ -z "$VPN_IF" ]; then
  echo "Error: No suitable VPN interface found (ppp0, utunX, etc.)."
  exit 1
fi

echo "Detected VPN interface: $VPN_IF"
echo "Local IP (VPN):  $VPN_LOCAL_IP"
echo "Remote IP (VPN): $VPN_REMOTE_IP"

########################################
# 4) Generate PF config
########################################

PF_CONF=$(mktemp)
echo "Creating PF config at $PF_CONF"

cat > "$PF_CONF" <<EOF
int_if = "$PHY_IF"
vpn_if = "$VPN_IF"
vpn_local_ip = "$VPN_LOCAL_IP"
vpn_remote_ip = "$VPN_REMOTE_IP"
EOF

# Add universal PF header
cat >> "$PF_CONF" <<'EOF'
set block-policy drop
set skip on lo0

block all
block out inet6

################################
# Minimal allowances on the physical interface
################################

# 1) DHCP, broadcast, ICMP
pass from any to 255.255.255.255 keep state
pass from 255.255.255.255 to any keep state
pass proto udp from any to 224.0.0.0/4 keep state
pass proto udp from 224.0.0.0/4 to any keep state
pass on $int_if proto {tcp,udp} from any port 67:68 to any port 67:68 keep state
pass on $int_if inet proto icmp all icmp-type 8 code 0 keep state
EOF

##
## 4a) Allow DNS to each discovered server
##

if [ "${#DNS_SERVERS[@]}" -eq 0 ]; then
  cat >> "$PF_CONF" <<'EOF'
# No DNS servers found via scutil --dns
EOF
else
  echo "# DNS servers found:" >> "$PF_CONF"
  for dnsip in "${DNS_SERVERS[@]}"; do
    echo "pass quick proto {tcp,udp} from any to $dnsip port 53 keep state" >> "$PF_CONF"
  done
fi

cat >> "$PF_CONF" <<EOF

################################
# 4b) IPSec/L2TP traffic to REMOTE IP
################################
# ensure the VPN tunnel stays alive
pass on \$int_if proto {tcp, udp} to \$vpn_remote_ip port { 500, 4500, 1701 } keep state

################################
# 4c) VPN interface: allow everything
################################
pass on \$vpn_if all keep state

EOF

########################################
# 5) Apply the PF config
########################################

echo "----------- PF config -----------"
cat "$PF_CONF"
echo "---------------------------------"

sudo pfctl -Fa -f "$PF_CONF" -E || {
  echo "Failed to load PF rules."
  exit 1
}

echo "Kill-switch activated (PF enabled)."
echo "Physical interface: $PHY_IF"
echo "VPN interface:      $VPN_IF"
echo "DNS servers:        ${DNS_SERVERS[*]:-(none)}"
echo "Remote IP (VPN):    $VPN_REMOTE_IP"
echo "Partial kill-switch with dynamic DNS rules is now active."
