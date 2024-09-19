import pbi_pbip_filters


def test_clean_doesnt_fail(json_from_file_str: str) -> None:
    """The most basic test to make sure things are up and running."""
    assert pbi_pbip_filters.clean_json(json_from_file_str) is not None
