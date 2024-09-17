import argparse
import json
import os
from pathlib import Path
from typing import Any, TypeAlias

from pbi_pbip_filters.json_types import JSONType

PathLike: TypeAlias = str | Path | os.PathLike[Any]


def format_nested_json_strings(json_data: JSONType) -> JSONType:
    if not isinstance(json_data, dict | list):
        return json_data

    if isinstance(json_data, list):
        # Turn it into a `dict`.
        json_data = dict(enumerate(json_data))

    index = range(len(json_data)) if isinstance(json_data, list) else json_data.keys()
    for list_position_or_dict_key in index:
        value = json_data[list_position_or_dict_key]
        if isinstance(value, dict | list):
            json_data[list_position_or_dict_key] = format_nested_json_strings(value)
        elif isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                formatted_value = format_nested_json_strings(parsed_value)
                json_data[list_position_or_dict_key] = formatted_value
            except json.JSONDecodeError:
                continue
    return json_data


def _format_json_files(json_files: list[PathLike]) -> int:
    for file in json_files:
        try:
            with Path(file).open() as f:
                original_json = json.loads(f.read())

            formatted_json = format_nested_json_strings(original_json)
            formatted_json = json.dumps(formatted_json, ensure_ascii=False, indent=4)

            with Path(file).open("w") as f:
                f.write(formatted_json)

        except Exception as e:
            msg = f"Error processing {file}: {e}"
            raise ValueError(msg) from e

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="clean_JSON",
        description="Clean PowerBI generated nested JSON files.",
    )
    parser.add_argument(
        "filename",
        nargs="+",  # one or more
        help="One or more filenames to process",
        type=Path,
    )

    files = parser.parse_args().filename
    _format_json_files(files)


if __name__ == "__main__":
    main()
