from pathlib import Path

import pytest

test_directory = Path(__file__).parent
top_level_directory = test_directory.parent

# We don't want to process any of the JSONs in other directories, such as `.mypy_cache`.
json_glob = "Sales & Returns Sample v201912*/**/*.json"
json_files_list = list(top_level_directory.glob(json_glob))


@pytest.fixture(params=json_files_list)
def json_files() -> list[Path]:
    """All JSON files from the sample Power BI report."""
    return json_files_list


@pytest.fixture(params=json_files_list)
def json_file(request: pytest.FixtureRequest) -> Path:
    """A single JSON file from the sample Power BI report."""
    return request.param


@pytest.fixture
def json_from_file_str(json_file: Path) -> str:
    return Path(json_file).read_text(encoding="UTF-8")
