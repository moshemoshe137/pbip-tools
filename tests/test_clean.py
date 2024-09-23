import json
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

from pbi_pbip_filters import clean_json


def test_clean_doesnt_fail(json_from_file_str: str) -> None:
    """The most basic test to make sure things are up and running."""
    assert clean_json(json_from_file_str) is not None


def test_consistency(json_from_file_str: str) -> None:
    """Test that the function is well-defined."""
    first_time = clean_json(json_from_file_str)
    second_time = clean_json(json_from_file_str)

    assert first_time == second_time


def test_idempotence(json_from_file_str: str) -> None:
    """Test that applying `clean_json` twice is the same as applying it once."""
    cleaned_once = clean_json(json_from_file_str)
    cleaned_twice = clean_json(json.loads(cleaned_once))

    assert cleaned_once == cleaned_twice


def test_process_batch_files(temp_json_files: Iterable[Path]) -> None:
    # Fixes [S607](https://docs.astral.sh/ruff/rules/start-process-with-partial-path/).
    # Find the absolute path to the `json-clean` executable.
    json_clean_executable = Path(sys.executable).parent / "json-clean"

    result = subprocess.run(  # noqa: S603
        [json_clean_executable, *temp_json_files],
        check=True,
    )

    assert result.returncode == 0
