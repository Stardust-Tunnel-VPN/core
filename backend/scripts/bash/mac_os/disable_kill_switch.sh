#!/bin/bash

# disable_kill_switch.sh
#
# Disables the PF firewall or resets it to default rules from /etc/pf.conf
# Must be run with sudo or configured in sudoers (NOPASSWD).

PF_MAIN_CONF="/etc/pf.conf"

echo "Disabling kill-switch and restoring default PF settings..."

# Disable PF entirely
sudo pfctl -d

# Flush all rules and reload the default /etc/pf.conf
sudo pfctl -Fa -f "$PF_MAIN_CONF"

echo "Kill-switch disabled, PF restored to default rules."
