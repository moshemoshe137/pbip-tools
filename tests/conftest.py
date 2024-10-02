"""Shared `pytest` fixtures."""

import shutil
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from pbip_tools.clean.clean_JSON import clean_json
from pbip_tools.smudge.smudge_JSON import smudge_json
from pbip_tools.type_aliases import JSONType

tests_directory = Path(__file__).parent
json_files_list = list(tests_directory.glob("Sample PBIP Reports/**/*.json"))


@pytest.fixture(params=json_files_list, ids=str)
def json_files() -> list[Path]:
    """
    All JSON files from the sample Power BI report.

    These JSON files are globbed from the project directory and point to the files in
    the current project.
    """
    return json_files_list


@pytest.fixture
def temp_json_files(json_files: list[Path], tmp_path: Path) -> Iterator[Path]:
    """
    All JSON files from the sample Power BI report in a temporary directory.

    The JSON files are globbed from the project directory then copied to a temporary
    directory. The refer to a copy of the file and not the original project file.

    Returns
    -------
    Iterator[Path]
        A list or iterator over the temporary JSON filepaths.
    """
    for file in json_files:
        shutil.copy2(file, tmp_path / file.name)
    return ((tmp_path / file.name).resolve() for file in json_files)


@pytest.fixture(params=json_files_list, ids=str)
def json_file(request: pytest.FixtureRequest) -> Path:
    """
    Return a single JSON file from the sample Power BI report.

    Returns
    -------
    Path
        Path to the JSON file in the test.
    """
    return request.param


@pytest.fixture
def json_from_file_str(json_file: Path) -> str:
    """
    Return the content of a test JSON file as a string.

    Returns
    -------
    str
        The contents of the test JSON file as a string.
    """
    return Path(json_file).read_text(encoding="UTF-8")


@pytest.fixture(params=[clean_json, smudge_json])
def filter_function(request: pytest.FixtureRequest) -> Callable[[JSONType], str]:
    """
    Fixture that provides either the `clean_json` or `smudge_json` function.

    This parameterized fixture will alternate between the two filter functions. This
    allows tests to apply both filters without duplicating test code.

    Returns
    -------
    Callable[[JSONType], str]
        The `clean_json` or `smudge_json` function.
    """
    return request.param


@pytest.fixture(params=["json-clean", "json-smudge"])
def filter_function_cli_executable(request: pytest.FixtureRequest) -> Path:
    """Return the executable to `json-clean` or `json-smudge`."""
    return Path(sys.executable).parent / request.param
