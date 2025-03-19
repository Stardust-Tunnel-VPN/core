from enum import Enum

"""
Reusable Enum class for supported OS in the application.
"""


class SupportedOS(str, Enum):
    WINDOWS = "WINDOWS"
    MACOS = "MACOS"
    LINUX = "LINUX"
    ANDROID = "ANDROID"
    IOS = "IOS"
