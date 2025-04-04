import subprocess
from pathlib import Path

import pytest

from core.services.handler import VPNGateHandler
from core.services.packer import Packer
from core.services.parser import Parser
from utils.reusable.vars import request_url


@pytest.fixture
def sample_csv() -> str:
    """
    Reads CSV data from the file `vpngate_mock.csv` and returns it as a string.
    This fixture is used to provide sample CSV data for testing purposes.
    """
    csv_path = Path(__file__).parent / "mock_data" / "vpngate_mock.csv"
    return csv_path.read_text(encoding="utf-8")


@pytest.fixture
def sample_packer(sample_csv):
    """
    Creates a `Packer` instance initialized with real CSV data from the file.
    This fixture is used to test functionality that requires a `Packer` with actual data.
    """
    return Packer(sample_csv)


@pytest.fixture
def empty_packer():
    """
    Creates a `Packer` instance initialized with an empty string (no data).
    This fixture is used to test functionality that requires a `Packer` with no input data.
    """
    return Packer("")


@pytest.fixture
def mocked_parser(sample_csv):
    """
    Creates a `Parser` instance where the `parseURL()` method is mocked to return
    the sample CSV data instead of performing a real HTTP request.
    This fixture is used to test functionality that depends on the `Parser` without
    making actual network calls.
    """
    parser = Parser("fakeurl")
    parser.parseURL = lambda: sample_csv
    return parser


@pytest.fixture(autouse=True)
def ensure_pf_disabled():
    """
    Fixture to ensure that pf is disabled (pfctl -d) after test completes,
    so we don't leave kill-switch active on the system.
    """
    yield
    subprocess.run(["sudo", "pfctl", "-d"], check=False)
