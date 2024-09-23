import shutil
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from pbi_pbip_filters.clean.clean_JSON import clean_json
from pbi_pbip_filters.smudge.smudge_JSON import smudge_json
from pbi_pbip_filters.type_aliases import JSONType

tests_directory = Path(__file__).parent
top_level_directory = tests_directory.parent

# We don't want to process any of the JSONs in other directories, such as `.mypy_cache`.
json_glob = "Sales & Returns Sample v201912*/**/*.json"
json_files_list = list(top_level_directory.glob(json_glob))


@pytest.fixture(params=json_files_list, ids=str)
def json_files() -> list[Path]:
    """All JSON files from the sample Power BI report."""
    return json_files_list


@pytest.fixture
def temp_json_files(json_files: list[Path], tmp_path: Path) -> Iterator[Path]:
    for file in json_files:
        shutil.copy2(file, tmp_path / file.name)
    return ((tmp_path / file.name).resolve() for file in json_files)


@pytest.fixture(params=json_files_list, ids=str)
def json_file(request: pytest.FixtureRequest) -> Path:
    """A single JSON file from the sample Power BI report."""
    return request.param


@pytest.fixture
def json_from_file_str(json_file: Path) -> str:
    return Path(json_file).read_text(encoding="UTF-8")


@pytest.fixture(params=[clean_json, smudge_json])
def filter_function(request: pytest.FixtureRequest) -> Callable[[JSONType], str]:
    return request.param
