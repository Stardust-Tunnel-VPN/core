from pathlib import Path

import pytest

from core.services.handler import VPNGateHandler
from core.services.packer import Packer
from core.services.parser import Parser
from utils.reusable.vars import request_url


@pytest.fixture
def sample_csv() -> str:
    """
    Читает CSV-данные из файла vpngate_mock.csv и возвращает как строку.
    """
    csv_path = Path(__file__).parent / "mock_data" / "vpngate_mock.csv"
    return csv_path.read_text(encoding="utf-8")


@pytest.fixture
def sample_packer(sample_csv):
    """Packer с реальным CSV из файла."""
    return Packer(sample_csv)


@pytest.fixture
def empty_packer():
    """Packer с пустой строкой (нет данных)."""
    return Packer("")


@pytest.fixture
def mocked_parser(sample_csv):
    """
    Parser, у которого parseURL() замокан, чтобы возвращал sample_csv,
    без реального HTTP-запроса.
    """
    parser = Parser("fakeurl")
    # Мокаем метод:
    parser.parseURL = lambda: sample_csv
    return parser
