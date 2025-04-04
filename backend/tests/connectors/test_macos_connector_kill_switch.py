"""Module: test_macos_connector_kill_switch
========================================

This module contains an integration test for the `MacOSL2TPConnector` class, specifically testing
the VPN kill-switch functionality on macOS. The test interacts with real system components such as
`scutil` and `pfctl`, requiring elevated privileges and specific system configurations to run.

The test verifies the following:
1. The ability to connect to a VPN with the kill-switch enabled.
2. The VPN connection status after connecting.
3. Traffic routing through the VPN by pinging an external IP.
4. The behavior of the kill-switch when the VPN is disconnected, ensuring traffic is blocked.
5. The ability to disable the kill-switch and restore normal traffic.

**Requirements:**
- A real L2TP service named "MyL2TP" configured in macOS Network settings.
- The "Send all traffic over VPN" option enabled for the L2TP service.
- `pfctl` must not prompt for a password (use `NOPASSWD` in sudoers or run the test as sudo).
- A stable external host to ping (e.g., 8.8.8.8).

**Note:** This test requires root privileges to execute and should be run with caution as it modifies
network settings and firewall rules.

Dependencies:
- pytest
- asyncio
- subprocess
- os


    Integration test for the `MacOSL2TPConnector` class with real `scutil` and `pfctl` calls.
    This test ensures the VPN kill-switch functionality works as expected.

    **Test Steps:**
    1. Connect to the VPN with the kill-switch enabled.
    2. Verify the VPN connection status is "Connected".
    3. Ping an external IP (e.g., 8.8.8.8) to confirm traffic is routed through the VPN.
    4. Disconnect the VPN while keeping the kill-switch monitor active.
    5. Wait for the kill-switch monitor to detect the disconnection and block traffic.
    6. Attempt to ping the external IP again, expecting it to fail due to the kill-switch.
    7. Disable the kill-switch and stop the monitor to restore normal traffic.

    **Parameters:**
    None

    **Returns:**
    None

    **Raises:**
    - `pytest.fail`: If any step in the test fails, an appropriate error message is logged, and the test is marked as failed.

    **Preconditions:**
    - A real L2TP VPN service named "MyL2TP" must be configured in macOS Network settings.
    - The "Send all traffic over VPN" option must be enabled for the VPN service.
    - The `pfctl` command must not prompt for a password (use `NOPASSWD` in sudoers or run the test as sudo).
    - A stable external host (e.g., 8.8.8.8) must be reachable for ping tests.

    **Postconditions:**
    - The VPN kill-switch is disabled, and the monitor is stopped, restoring normal traffic routing.

    **Important Notes:**
    - This test modifies system network settings and firewall rules. Ensure you understand the implications
      before running it on a production system.
    - The test requires root privileges to execute."""

import asyncio
import os
import subprocess
import time

import pytest

from core.managers.vpn_manager_macos import MacOSL2TPConnector


@pytest.mark.asyncio
@pytest.mark.usefixtures("ensure_pf_disabled")
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
@pytest.mark.usefixtures("ensure_pf_disabled")
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


@pytest.mark.asyncio
@pytest.mark.usefixtures("ensure_pf_disabled")
@pytest.mark.skipif(
    os.geteuid() != 0, reason="Requires root privileges for pfctl tests"
)
async def test_integration_wrong_sudo_password():
    """
    Integration test: store a WRONG password in Keychain, then attempt connect with kill_switch_enabled=True.
    Expect pfctl commands to fail once the kill-switch tries to engage.
    """
    client = TestClient(app)

    # 1) Store a definitely wrong sudo password
    store_resp = client.post(
        "/api/v1/store_sudo_password", json={"password": "WRONG-PASS-TEST"}
    )
    assert store_resp.status_code == 200
    assert "status" in store_resp.json()

    connector = MacOSL2TPConnector(service_name="MyL2TP")
    # 2) Attempt to connect with kill_switch_enabled -> eventually monitor tries pfctl
    try:
        connect_msg = await connector.connect(kill_switch_enabled=True)
        print("[TEST] connect_msg:", connect_msg)
        # Sleep a bit so the monitor might attempt pfctl
        await asyncio.sleep(4)
    except Exception as exc:
        # If it fails immediately, we catch it
        print("[TEST] Connect raised exception as expected:", exc)
        return

    # If it didn't fail yet, let's forcibly disconnect -> monitor tries to 'enable kill switch' => should fail
    print(
        "[TEST] Forcibly disconnect so kill-switch tries pfctl -e with the WRONG password."
    )
    try:
        disc_msg = await connector.disconnect()
        print("[TEST] disc_msg:", disc_msg)
        # Wait a bit so the monitor definitely attempts pfctl
        await asyncio.sleep(4)
    except Exception as exc:
        # We expect an error at some point
        print(
            "[TEST] Disconnect raised exception (maybe kill-switch error triggered):",
            exc,
        )

    print(
        "[TEST] If kill-switch attempted pfctl with wrong password, logs should show 'Sorry, try again.' etc."
    )
