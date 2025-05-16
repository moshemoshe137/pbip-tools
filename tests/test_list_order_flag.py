"""Tests for the `ignore_list_order` flag in `clean_json`."""

import json
from typing import TYPE_CHECKING

from pbip_tools.clean.clean_JSON import clean_json
from pbip_tools.smudge.smudge_JSON import smudge_json

if TYPE_CHECKING:
    from pbip_tools.type_aliases import JSONType


def test_default_preserves_list_order() -> None:
    """Test that the default behavior preserves the order of lists."""
    data: JSONType = {"letters": ["b", "a", "c"], "numbers": [2, 1, 3]}
    cleaned = clean_json(data)  # ignore_list_order=False by default
    parsed = json.loads(cleaned)
    # Lists should come out in the same order we passed in
    assert parsed["letters"] == ["b", "a", "c"]
    assert parsed["numbers"] == [2, 1, 3]


def test_flag_sorts_primitives() -> None:
    """Test that the flag sorts primitives in lists."""
    data: JSONType = {"letters": ["b", "a", "c"], "numbers": [2, 1, 3]}
    cleaned = clean_json(data, ignore_list_order=True)
    parsed = json.loads(cleaned)
    # Now everything is sorted lexicographically (for strings) or numerically
    assert parsed["letters"] == ["a", "b", "c"]
    assert parsed["numbers"] == [1, 2, 3]


def test_flag_sorts_complex_objects() -> None:
    """Test that the flag sorts complex objects in lists."""
    data: JSONType = {
        "objs": [
            {"z": 0, "a": 1},
            {"a": 1, "z": 0},
            {"m": 5},
        ]
    }
    cleaned = clean_json(data, ignore_list_order=True)
    parsed = json.loads(cleaned)
    # Both {"a":1,"z":0} variants collapse to the same canonical JSON and
    # come before {"m":5}
    assert parsed["objs"][0] == {"a": 1, "z": 0}
    assert parsed["objs"][1] == {"a": 1, "z": 0}
    assert parsed["objs"][2] == {"m": 5}


def test_roundtrip_idempotence_with_flag() -> None:
    """Test that cleaning and smudging with the flag set is idempotent."""
    # Round-trip through clean→smudge→clean with the flag set
    original: JSONType = {"mixed": ['{"x":2,"y":1}', '{"y":1,"x":2}']}
    first = clean_json(original, ignore_list_order=True)
    smudged = smudge_json(json.loads(first))
    second = clean_json(json.loads(smudged), ignore_list_order=True)
    assert first == second
