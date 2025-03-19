"""
Unit tests for the SupportedOS Enum in utils/reusable/supported_os.py.
"""

import pytest

from utils.reusable.supported_os import SupportedOS


def test_supported_os_values():
    """
    Verify that the SupportedOS enum contains the expected values:
    WINDOWS, MACOS, LINUX, ANDROID, IOS.
    We also check if string comparison matches the name.
    """
    assert SupportedOS.WINDOWS.value == "WINDOWS"
    assert SupportedOS.MACOS.value == "MACOS"
    assert SupportedOS.LINUX.value == "LINUX"
    assert SupportedOS.ANDROID.value == "ANDROID"
    assert SupportedOS.IOS.value == "IOS"


def test_supported_os_iteration():
    """
    Ensure that iteration or listing all items returns exactly five OS entries.
    """
    all_values = list(SupportedOS)
    assert len(all_values) == 5
    expected = {"WINDOWS", "MACOS", "LINUX", "ANDROID", "IOS"}
    actual = {item.value for item in all_values}
    assert actual == expected
