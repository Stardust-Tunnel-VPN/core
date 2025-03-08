# tests/test_packer.py

import pytest
from unittest.mock import patch
from core.services.packer import Packer
from utils.reusable.sort_directions import SortDirection


def test_packer_transform_content_basic(sample_packer):
    """
    Test that transform_content() correctly filters out restricted countries and
    retains only the allowed fields by default (no extra parameters).

    Expected behavior:
      - If the CSV has lines with 'CountryShort' == restricted countries codes,
        those lines should be removed.
      - The resulting list should only have columns that are in filters_VPN_GATE.

    Args:
        sample_packer (Packer): A pytest fixture that provides
            a Packer instance with sample CSV data containing
            at least one is restricted country row.

    Returns:
        None. Asserts that the final list matches the expected length
        (depending on how many restricted country lines were in the CSV).
    """
    data = sample_packer.transform_content()
    assert len(data) == 4


def test_packer_transform_content_with_search(sample_packer):
    """
    Test that transform_content() can filter by partial hostname
    using the 'search' parameter.

    We search for a substring like '66', expecting to get only rows
    whose #HostName contains '66'.

    Args:
        sample_packer (Packer): The Packer instance loaded with CSV.

    Returns:
        None. Asserts that the resulting list size matches the expected
        number of matches and that each row's #HostName actually contains '66'.
    """
    data = sample_packer.transform_content(search="66")
    assert len(data) == 1
    for row in data:
        assert "66" in row.get("#HostName", "")


def test_packer_transform_content_no_results(sample_packer):
    """
    Test that transform_content() returns an empty list if no row
    matches the 'search' parameter.

    Args:
        sample_packer (Packer): The Packer instance with CSV data.

    Returns:
        None. Asserts that the output list is empty when searching
        for a non-existing string.
    """
    data = sample_packer.transform_content(search="some_non_existing_name")
    assert data == []


def test_packer_transform_content_sort_ping_asc(sample_packer):
    """
    Test that transform_content() sorts data by Ping in ascending order
    when provided sort_by='Ping' and order_by=SortDirection.ASC.

    It checks the final list to ensure the Ping values are strictly
    sorted in ascending order.

    Args:
        sample_packer (Packer): The Packer instance with CSV data.

    Returns:
        None. Asserts that the 'Ping' values in the result are sorted ascending.
    """
    data = sample_packer.transform_content(sort_by="Ping", order_by=SortDirection.ASC)
    pings = [int(row.get("Ping", "0")) for row in data]
    assert pings == sorted(pings)


def test_packer_transform_content_sort_ping_desc(sample_packer):
    """
    Test that transform_content() sorts data by Ping in descending order
    with sort_by='Ping' and order_by=SortDirection.DESC.

    Args:
        sample_packer (Packer): The Packer instance with CSV data.

    Returns:
        None. Asserts that the 'Ping' values in the result are sorted descending.
    """
    data = sample_packer.transform_content(sort_by="Ping", order_by=SortDirection.DESC)
    pings = [int(row.get("Ping", "0")) for row in data]
    assert pings == sorted(pings, reverse=True)


def test_packer_transform_content_sort_score_asc(sample_packer):
    """
    Test that transform_content() sorts data by 'Score' ascending.

    Args:
        sample_packer (Packer): The Packer instance.

    Returns:
        None. Asserts that 'Score' is sorted from smallest to largest.
    """
    data = sample_packer.transform_content(sort_by="Score", order_by=SortDirection.ASC)
    scores = [int(row.get("Score", "0")) for row in data]
    assert scores == sorted(scores)


def test_packer_transform_content_sort_speed_desc(sample_packer):
    """
    Test that transform_content() sorts data by 'Speed' in descending order.

    Args:
        sample_packer (Packer): The Packer instance.

    Returns:
        None. Asserts that 'Speed' is sorted from largest to smallest.
    """
    data = sample_packer.transform_content(sort_by="Speed", order_by=SortDirection.DESC)
    speeds = [int(row.get("Speed", "0")) for row in data]
    assert speeds == sorted(speeds, reverse=True)


def test_packer_transform_content_search_and_sort(sample_packer):
    """
    Test that transform_content() can apply both search and sort in one call.
    We search for '66' in #HostName, then sort results by 'Speed' ascending.

    If only one matching row has '66', sorting doesn't do much, but
    if there's more than one, we can confirm the order.

    Args:
        sample_packer (Packer): The Packer instance.

    Returns:
        None. Asserts that if multiple rows contain '66', they are
        sorted in ascending order by Speed.
    """
    data = sample_packer.transform_content(search="66", sort_by="Speed", order_by=SortDirection.ASC)
    if len(data) > 1:
        speeds = [int(row.get("Speed", "0")) for row in data]
        assert speeds == sorted(speeds)


def test_packer_transform_content_empty(empty_packer):
    """
    Test that transform_content() returns an empty list if the CSV content is empty.

    Args:
        empty_packer (Packer): A fixture with no CSV data at all.

    Returns:
        None. Asserts an empty list is returned.
    """
    data = empty_packer.transform_content()
    assert data == []


@patch("core.services.packer.traceback")
def test_packer_transform_content_exception(mock_tb, sample_packer):
    """
    Test the exception block in transform_content() by invalidating self.content.

    We set sample_packer.content = None, which triggers an AttributeError
    on split(). We verify that the method returns [] and calls traceback.print_exc().

    Args:
        mock_tb (MagicMock): Mocked version of the 'traceback' module.
        sample_packer (Packer): The Packer instance with normal CSV data.

    Returns:
        None. Asserts an empty list is returned and traceback is printed.
    """
    sample_packer.content = None
    data = sample_packer.transform_content()
    assert data == []
    mock_tb.print_exc.assert_called_once()


@patch("core.services.packer.traceback")
def test_packer_sort_content_exception(mock_tb, sample_packer):
    """
    Test the exception block in sort_content() by patching it to raise an Exception.

    We patch 'sort_content' so that it throws an Exception("Sort fail").
    Then transform_content() should catch that exception and return [].

    Args:
        mock_tb (MagicMock): Mock for traceback.
        sample_packer (Packer): A normal Packer instance.

    Returns:
        None. Asserts that transform_content() returns [] and traceback is printed.
    """
    with patch.object(sample_packer, "sort_content", side_effect=Exception("Sort fail")):
        data = sample_packer.transform_content(sort_by="Ping")
        assert data == []
    mock_tb.print_exc.assert_called_once()


@patch("core.services.packer.traceback")
def test_packer_filter_by_hostname_exception(mock_tb, sample_packer):
    """
    Test the exception block in filter_by_hostname() by passing None instead of a data list.

    This forces row.get(...) calls on None, raising an exception,
    which should be caught, resulting in an empty list and a printed traceback.

    Args:
        mock_tb (MagicMock): Mocked traceback.
        sample_packer (Packer): A normal Packer instance.

    Returns:
        None. Asserts that filter_by_hostname(...) returns [] and calls print_exc().
    """
    result = sample_packer.filter_by_hostname(None, "66")
    assert result == []
    mock_tb.print_exc.assert_called_once()


@patch("core.services.packer.traceback")
def test_packer_remove_restricted_countries_exception(mock_tb, sample_packer):
    """
    Test the exception block in remove_restricted_countries() by passing None.

    This ensures that the method tries to iterate over None,
    triggering an exception. The method should catch it and return [].

    Args:
        mock_tb (MagicMock): Mocked traceback.
        sample_packer (Packer): The Packer instance.

    Returns:
        None. Asserts that remove_restricted_countries(...) returns []
        and calls print_exc().
    """
    result = sample_packer.remove_restricted_countries(None)
    assert result == []
    mock_tb.print_exc.assert_called_once()


def test_packer_format_content(sample_packer):
    """
    Test that format_content() returns a well-formatted string representation (using pformat).

    We first obtain a list of rows by transform_content(), then call format_content()
    to produce a pretty-printed string. We expect the string to contain known
    column names like 'HostName' or '#HostName'.

    Args:
        sample_packer (Packer): The Packer instance with sample CSV.

    Returns:
        None. Asserts that the result is a string containing at least
        one known column name.
    """
    data = sample_packer.transform_content()
    assert isinstance(data, list)
    text_repr = sample_packer.format_content(data)
    assert isinstance(text_repr, str)
    assert "HostName" in text_repr or "#HostName" in text_repr
