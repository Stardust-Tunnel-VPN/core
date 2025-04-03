import asyncio
import os
import subprocess
import time

import pytest

from core.managers.vpn_manager_macos import MacOSL2TPConnector


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.geteuid() != 0, reason="Requires root privileges (sudo) to run pfctl."
)
async def test_integration_vpn_kill_switch():
    """
    Integration test for MacOSL2TPConnector with real scutil/pfctl calls.
    Requires:
      1) A real L2TP service named "MyL2TP" in macOS Network settings.
      2) 'Send all traffic over VPN' enabled for that L2TP service.
      3) `pfctl` must not prompt for a password (NOPASSWD or run test as sudo).
      4) A stable external host to ping (like 8.8.8.8).

    Steps:
      1) Connect with kill_switch_enabled=True.
      2) Verify status is 'Connected', try pinging an external IP – should succeed via VPN.
      3) Disconnect (do NOT stop kill-switch monitor).
      4) Wait a few seconds for the monitor to see 'Disconnected'.
      5) Ping again – it should fail, because kill-switch is active.
      6) Disable kill-switch and stop monitor to restore normal traffic.
    """

    print("\n[TEST] Starting real integration test with kill-switch monitor.")
    connector = MacOSL2TPConnector(service_name="MyL2TP")

    print("[TEST] 1) Attempting to connect to VPN with kill-switch enabled...")
    try:
        connect_result = await connector.connect(kill_switch_enabled=True)
        print(f"[TEST] Connect result: {connect_result}")
    except Exception as e:
        pytest.fail(f"[TEST] Failed to connect: {e}")

    print("[TEST] Checking connector.status() right after connect...")
    st = await connector.status()
    print(f"[TEST] Current VPN status: {st}")
    assert st.lower() == "connected", "VPN should be 'Connected' after connect."

    print("[TEST] 2) Attempting to ping 8.8.8.8 to verify traffic over VPN...")
    try:
        output = subprocess.check_output(
            ["ping", "-c", "4", "-W", "5", "8.8.8.8"],
            timeout=15,
        )
        print(f"[TEST] Ping output:\n{output.decode('utf-8')}")
        if b"0 packets received" in output:
            pytest.fail(
                "[TEST] Ping returned 0 packets received while VPN is connected."
            )
    except Exception as e:
        pytest.fail(f"[TEST] Ping while VPN is connected failed unexpectedly: {e}")

    print("[TEST] 3) Disconnecting from VPN. The kill-switch monitor remains active.")
    try:
        disc_result = await connector.disconnect()
        print(f"[TEST] Disconnect result: {disc_result}")
        assert "Disconnected VPN" in disc_result, "disconnect() should return success."
    except Exception as e:
        pytest.fail(f"[TEST] Failed to disconnect: {e}")

    print(
        "[TEST] 4) Waiting 4 seconds for kill-switch monitor to detect 'Disconnected' and block traffic."
    )
    await asyncio.sleep(4)

    print("[TEST] 5) Attempting ping again – it should fail if kill-switch is active.")
    ping_failed = False
    try:
        output = subprocess.check_output(
            ["ping", "-c", "2", "-W", "2", "8.8.8.8"], timeout=10
        )
        print("[TEST] Ping output after disconnect:\n", output.decode("utf-8"))
        # If we got here, ping surprisingly succeeded
    except subprocess.CalledProcessError:
        print("[TEST] Ping returned non-zero exit code -> means it was blocked. Good!")
        ping_failed = True
    except subprocess.TimeoutExpired:
        print("[TEST] Ping timed out -> also means blocked.")
        ping_failed = True

    assert ping_failed, "[TEST] We expected ping to fail after kill-switch triggered."

    print(
        "[TEST] 6) Disabling kill-switch to restore normal traffic. Also stopping monitor."
    )
    try:
        disable_result = await connector.disable_kill_switch()
        print(f"[TEST] disable_kill_switch result: {disable_result}")
        await connector.stop_kill_switch_monitor()
        print("[TEST] Stopped kill-switch monitor.")
        assert (
            "disabled" in disable_result.lower()
        ), "Should successfully disable kill-switch."
    except Exception as e:
        pytest.fail(f"[TEST] Error disabling kill-switch or stopping monitor: {e}")

    print("[TEST] Completed test_integration_vpn_kill_switch successfully.")


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.geteuid() != 0, reason="Requires root privileges (sudo) to run pfctl."
)
async def test_integration_vpn_kill_switch_forced_drop():
    """
    Integration test that forcibly drops the VPN outside the connector
    (e.g. scutil --nc stop or ifconfig ppp0 down) while kill-switch monitor
    is running, to ensure that upon 'Disconnected' the kill-switch is enabled.

    Requirements:
      - Real L2TP service 'MyL2TP'.
      - 'Send all traffic over VPN' toggled ON.
      - pfctl with no password prompt.
      - scutil --nc stop MyL2TP or ifconfig ppp0 down forcibly kills the VPN.

    Steps:
      1) Connect with kill_switch_enabled=True.
      2) Verify 'Connected', ping 8.8.8.8 -> success.
      3) Force drop the VPN: scutil --nc stop MyL2TP
      4) Wait for monitor to see 'Disconnected', enable kill-switch -> block traffic
      5) Try ping again -> fails
      6) Clean up: disable kill-switch, stop monitor
    """

    print("\n[TEST] Starting forced-drop integration test.")
    connector = MacOSL2TPConnector(service_name="MyL2TP")

    print("[TEST] 1) Connecting with kill-switch enabled...")
    try:
        connect_msg = await connector.connect(kill_switch_enabled=True)
        print(f"[TEST] Connect result: {connect_msg}")
    except Exception as e:
        pytest.fail(f"[TEST] VPN connect failed: {e}")

    st = await connector.status()
    print(f"[TEST] Current VPN status after connect: {st}")
    assert st.lower() == "connected", "Expected 'connected' but got something else."

    print("[TEST] 2) Pinging 8.8.8.8 -> should succeed over VPN.")
    try:
        output = subprocess.check_output(
            ["ping", "-c", "4", "-W", "5", "8.8.8.8"],
            timeout=15,
        )
        print("[TEST] Ping output:\n", output.decode("utf-8"))
        if b"0 packets received" in output:
            pytest.fail(
                "[TEST] Ping returned 0 packets received while VPN is connected."
            )
    except Exception as e:
        pytest.fail(f"[TEST] Ping while VPN is connected failed unexpectedly: {e}")

    print(
        "[TEST] 3) Forcibly stopping VPN from outside the connector (scutil --nc stop)..."
    )
    try:
        subprocess.check_call(["scutil", "--nc", "stop", "MyL2TP"])
        print("[TEST] scutil stop invoked successfully.")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"[TEST] Failed to forcibly stop VPN: {e}")

    print(
        "[TEST] 4) Wait 4s for kill-switch monitor to see 'Disconnected' and block traffic."
    )
    await asyncio.sleep(4)

    print(
        "[TEST] 5) Attempt ping -> expected to fail since kill-switch should be active."
    )
    ping_failed = False
    try:
        output = subprocess.check_output(
            ["ping", "-c", "2", "-W", "2", "8.8.8.8"], timeout=10
        )
        print("[TEST] Ping output after forced drop:\n", output.decode("utf-8"))
    except subprocess.CalledProcessError:
        print("[TEST] Ping returned non-zero exit code -> means block. Good!")
        ping_failed = True
    except subprocess.TimeoutExpired:
        print("[TEST] Ping timed out -> also means block.")
        ping_failed = True

    assert (
        ping_failed
    ), "[TEST] We expected ping to fail after forced drop with kill-switch."

    print("[TEST] 6) Disable kill-switch, stop monitor, restore traffic.")
    try:
        disable_msg = await connector.disable_kill_switch()
        print(f"[TEST] disable_kill_switch result: {disable_msg}")
        await connector.stop_kill_switch_monitor()
        print("[TEST] Stopped kill-switch monitor.")
        assert "disabled" in disable_msg.lower()
    except Exception as e:
        print(
            f"[TEST] Warning: disabling kill-switch or stopping monitor encountered error: {e}"
        )

    print("[TEST] Completed test_integration_vpn_kill_switch_forced_drop successfully.")
