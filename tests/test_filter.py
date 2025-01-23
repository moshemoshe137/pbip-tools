"""Shared tests for both filters, `clean_json` and `smudge_json`."""

import json
import subprocess
from collections.abc import Callable, Iterable
from pathlib import Path

from pbip_tools import clean_json, smudge_json
from pbip_tools.type_aliases import JSONType, PathLike


def test_filter_doesnt_fail(
    filter_function: Callable[[JSONType], str], json_from_file_str: str
) -> None:
    """The most basic test to make sure things are up and running."""
    assert filter_function(json_from_file_str) is not None


def test_filter_consistency(
    filter_function: Callable[[JSONType], str], json_from_file_str: str
) -> None:
    """Test that the function is well-defined."""
    first_time = filter_function(json_from_file_str)
    second_time = filter_function(json_from_file_str)

    assert first_time == second_time


def test_filter_idempotence(
    filter_function: Callable[[JSONType], str], json_from_file_str: str
) -> None:
    """Test that cleaning or smudging twice is the same as applying the filter once."""
    filtered_once = filter_function(json_from_file_str)
    filtered_twice = filter_function(json.loads(filtered_once))

    assert filtered_once == filtered_twice


def test_process_batch_files(
    filter_func_cli_executable: Iterable[PathLike], temp_json_files: Iterable[Path]
) -> None:
    """Test processing a list of files on the command line."""
    result = subprocess.run(  # noqa: S603
        [*filter_func_cli_executable, *temp_json_files],
        check=True,
    )

    assert result.returncode == 0


def test_roundtrip(json_from_file_str: str) -> None:
    """Test that cleaning undoes smudging."""
    cleaned = clean_json(json.loads(json_from_file_str))
    smudged = smudge_json(json.loads(cleaned))
    smudged_then_cleaned = clean_json(json.loads(smudged))

    assert cleaned == smudged_then_cleaned


def test_no_nan_or_infinity(json_from_file_str: str) -> None:
    """Ensure that the JSON file does not contain NaN or Infinity."""
    cleaned = clean_json(json.loads(json_from_file_str))
    dumped = json.dumps(
        json.loads(cleaned),
        allow_nan=False,  # This will raise a ValueError if NaN or Infinity are present
    )

    assert json.loads(dumped) != {}  # Not an empty dict
