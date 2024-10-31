"""Test input from `stdin` and piping to `stdout`."""

import json
import subprocess
from collections.abc import Iterator

example_bad_json = (
    '{"foo": "bar", "nested": {"values": [0,1,2], "hidden":false},'
    ' "list_o_things": [0, true, 3.14, "things have spaces"]}'
)

example_formatted_json = (
    '{\n    "foo": "bar",\n    "nested": {\n        "values": [\n            0,\n'
    '            1,\n            2\n        ],\n        "hidden": false\n    },\n    '
    '"list_o_things": [\n        0,\n        true,\n        3.14,\n        '
    '"things have spaces"\n    ]\n}'
)


def test_stdin(any_cli_executable: Iterator[str]) -> None:
    """Test that we get the expected output when piping through stdin."""
    result = subprocess.run(  # noqa: S603
        [*any_cli_executable, "-"],
        input=example_bad_json.encode("UTF-8"),
        check=True,
        capture_output=True,
    )
    result_text = result.stdout.decode("UTF-8").replace("\r\n", "\n")

    assert result_text in (
        # The `result_text` matches the expected output exactly or...
        example_formatted_json,
        # ...or it possibly uses 2 spaces for indentation, not 4 (as the `json-smudge`
        # script does to its output).
        example_formatted_json.replace("    ", "  "),
    )
    assert json.loads(result_text) == json.loads(example_formatted_json)
    assert result.returncode == 0  # Return with exit code 0
    assert result.stderr == b""  # Check nothing in stderr
