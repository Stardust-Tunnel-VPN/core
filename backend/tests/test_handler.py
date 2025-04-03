# tests/test_handler.py

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.services.handler import VPNGateHandler
from core.services.packer import Packer
from core.services.parser import Parser
from main import app  # Make sure 'app' is your FastAPI instance


def test_vpn_servers_list_endpoint():
    """
    Integration test that checks if the /api/v1/vpn_servers_list endpoint
    correctly processes query parameters (e.g., search=66, sort_by=Ping)
    and returns a valid response.

    Steps:
    1. Make a GET request to /api/v1/vpn_servers_list?search=66&sort_by=Ping.
    2. Expect HTTP 200 status code.
    3. Optionally parse the JSON response and verify keys/structure.

    Returns:
        None. Asserts the endpoint is reachable and responds with 200.
    """
    client = TestClient(app)
    resp = client.get("/api/v1/vpn_servers_list?search=66&sort_by=Ping")
    assert resp.status_code == 200

    data = resp.json()


def test_vpngate_handler_init():
    """
    Test that the VPNGateHandler is properly initialized with
    the given Parser and Packer instances.

    Steps:
    1. Create a Parser and a Packer with dummy inputs.
    2. Pass them to the VPNGateHandler constructor.
    3. Assert that the handler stores them in self.parser and self.packer.

    Returns:
        None. Asserts the handler references the exact objects we passed in.
    """
    parser = Parser("some_url")
    packer = Packer("some_csv")
    handler = VPNGateHandler(parser=parser, packer=packer)

    assert handler.parser is parser
    assert handler.packer is packer


def test_vpngate_handler_get_vpn_servers(mocked_parser):
    """
    Test the normal scenario for get_vpn_servers(), assuming 'mocked_parser'
    returns valid CSV data that includes at least one 'RU' row.
    The handler should remove RU rows and return the rest.

    Steps:
    1. 'mocked_parser' fixture has parseURL() that returns a CSV with ~5 lines total,
       at least 1 with CountryShort='RU'.
    2. Create a Packer with that CSV content.
    3. Create a VPNGateHandler using parser=mocked_parser, packer=that packer.
    4. Call handler.get_vpn_servers().
    5. Assert the result has the expected number of rows after removing RU.

    Args:
        mocked_parser (Parser): A pytest fixture that has parseURL()
            returning a small CSV sample with one RU row.

    Returns:
        None. Asserts the length of the final list is 5 (based on your CSV structure).
    """
    packer = Packer(mocked_parser.parseURL())
    handler = VPNGateHandler(parser=mocked_parser, packer=packer)

    result = handler.get_vpn_servers()
    assert len(result) == 4


@patch(
    "core.services.handler.Packer.transform_content",
    side_effect=Exception("Some error"),
)
def test_vpngate_handler_get_vpn_servers_exception(mock_transform):
    """
    Test that get_vpn_servers() handles exceptions thrown by the packer
    and returns a dictionary with the error message.

    Steps:
    1. Patch Packer.transform_content to raise an Exception("Some error").
    2. Create a VPNGateHandler with any dummy Parser/Packer (not used).
    3. Call handler.get_vpn_servers().
    4. Expect the returned value to be a dict with
       {\"You've got an error in getting vpn server list method, \": "Some error"}.

    Args:
        mock_transform (MagicMock): A mock that replaces transform_content with
            side_effect=Exception("Some error").

    Returns:
        None. Asserts that the result is a dict containing "Some error".
    """
    parser = Parser("fakeurl")
    packer = Packer("not_important")
    handler = VPNGateHandler(parser=parser, packer=packer)

    result = handler.get_vpn_servers()
    assert isinstance(result, dict), "Expected a dict with error info."
    assert (
        "Some error" in list(result.values())[0]
    ), "Error message not found in result."
