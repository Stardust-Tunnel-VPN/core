# tests/test_parser.py
from unittest.mock import patch

import pytest

from core.services.parser import Parser
from utils.reusable.vars import request_url


@patch("core.services.parser.request")
def test_parser_parseURL_ok(mock_request):
    """
    Test successful retrieval of text from the parser.

    This test verifies that the `parseURL` method of the `Parser` class
    correctly retrieves and returns the response text when the request
    is successful. The `mock_request` is used to simulate a successful
    HTTP GET request, returning a mocked response text.

    Assertions:
    - The result of `parseURL` matches the mocked response text.
    - The `request` method is called exactly once with the correct arguments.
    """
    mock_request.return_value.text = "MOCK_RESPONSE"
    parser = Parser(request_url)

    result = parser.parseURL()
    assert result == "MOCK_RESPONSE"
    mock_request.assert_called_once_with("GET", request_url)


@patch("core.services.parser.request", side_effect=Exception("Network error"))
def test_parser_parseURL_exception(mock_request):
    """
    Test handling of exceptions in the parser.

    This test ensures that the `parseURL` method of the `Parser` class
    gracefully handles exceptions raised during the HTTP GET request.
    When an exception occurs, the method should return `None`.

    Assertions:
    - The result of `parseURL` is `None` when an exception is raised.
    - The `request` method is called exactly once with the correct arguments.
    """
    parser = Parser(request_url)
    result = parser.parseURL()
    assert result is None
    mock_request.assert_called_once_with("GET", request_url)
