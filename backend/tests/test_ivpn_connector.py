"""
Unit tests for the IVpnConnector interface/protocol.

Since IVpnConnector is a Protocol describing required methods,
we typically test concrete implementations. However, we can verify
that classes implementing IVpnConnector have all expected methods, etc.

"""

import pytest

from core.interfaces.ivpn_connector import IVpnConnector


def test_ivpn_connector_protocol_shape():
    """
    Test that IVpnConnector has the required abstract methods
    connect, disconnect, status, enable_kill_switch, disable_kill_switch.

    This is a simple example – often there's no direct 'runtime test'
    for a Protocol, as it's mostly checked by static typing (mypy).
    """
    required_methods = [
        "connect",
        "disconnect",
        "status",
        "enable_kill_switch",
        "disable_kill_switch",
    ]
    for method_name in required_methods:
        assert hasattr(
            IVpnConnector, method_name
        ), f"IVpnConnector is missing method: {method_name}"
