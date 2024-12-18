"""Test input from `stdin` and piping to `stdout`."""

import json
import subprocess

from pbip_tools.cli import create_argparser

example_bad_json = (
    '{"foo": "bar", "nested": {"values": [0,1,2], "hidden":false},'
    ' "list_o_things": [0, true, 3.14, "things have spaces"]}'
)

example_formatted_json = (
    '{\n  "foo": "bar",\n  "nested": {\n    "values": [\n      0,\n      1,\n      2\n'
    '    ],\n    "hidden": false\n  },\n  "list_o_things": [\n    0,\n    true,\n    '
    '3.14,\n    "things have spaces"\n  ]\n}'
)


def test_stdin(any_cli_executable: list[str]) -> None:
    """Test that we get the expected output when piping through stdin."""
    try:
        indent = create_argparser().parse_args([*any_cli_executable[1:], "-"]).indent
    except (
        AttributeError,  # i.e. when using the `smudge` subcommand.
        SystemExit,  # i.e. when using the legacy `json-clean` or `json-smudge` tools.
    ):
        indent = 2
    print(f"{indent=}")
    result = subprocess.run(  # noqa: S603
        [*any_cli_executable, "-"],
        input=example_bad_json.encode("UTF-8"),
        check=True,
        capture_output=True,
    )
    result_text = result.stdout.decode("UTF-8").replace("\r\n", "\n")

    expected_text = example_formatted_json.replace("  ", " " * indent)
    assert result_text == expected_text
    assert json.loads(result_text) == json.loads(example_formatted_json)
    assert result.returncode == 0  # Return with exit code 0
    assert result.stderr == b""  # Check nothing in stderr
