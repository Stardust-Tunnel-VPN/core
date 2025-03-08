# tests/test_parser.py
from unittest.mock import patch

import pytest

from core.services.parser import Parser
from utils.reusable.vars import request_url


@patch("core.services.parser.request")
def test_parser_parseURL_ok(mock_request):
    """
    Проверяем успешное получение текста.
    """
    mock_request.return_value.text = "MOCK_RESPONSE"
    parser = Parser(request_url)

    result = parser.parseURL()
    assert result == "MOCK_RESPONSE"
    mock_request.assert_called_once_with("GET", request_url)


@patch("core.services.parser.request", side_effect=Exception("Network error"))
def test_parser_parseURL_exception(mock_request):
    """
    Проверяем, что при исключении Parser возвращает None.
    """
    parser = Parser(request_url)
    result = parser.parseURL()
    assert result is None
    mock_request.assert_called_once_with("GET", request_url)
