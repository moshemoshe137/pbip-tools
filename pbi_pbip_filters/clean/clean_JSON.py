import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path

from pbi_pbip_filters.type_aliases import JSONType, PathLike


def format_nested_json_strings(json_data: JSONType) -> JSONType:
    if not isinstance(json_data, dict | list):
        return json_data

    index = range(len(json_data)) if isinstance(json_data, list) else json_data.keys()
    for list_position_or_dict_key in index:
        value = json_data[list_position_or_dict_key]  # type: ignore[index]
        if isinstance(value, dict | list):
            json_data[list_position_or_dict_key] = format_nested_json_strings(value)  # type:ignore[index]
        elif isinstance(value, str):
            float_pattern = r"^-?\d+\.\d+$"
            boolean_pattern = "true|false"
            float_or_bool_pat = float_pattern + "|" + boolean_pattern
            if re.match(float_or_bool_pat, value):
                # Do NOT parse raw floats and booleans. Doing so may change their
                # datatypes and make cleaning irreversible. Instead, preserve the
                # datatypes as they appeared in the original JSON, even if that's a
                # float or a boolean formatted as a string.
                continue
            try:
                parsed_value = json.loads(value)
                formatted_value = format_nested_json_strings(parsed_value)
                json_data[list_position_or_dict_key] = formatted_value  # type:ignore[index]
            except json.JSONDecodeError:
                continue
    return json_data


def _format_json_files(json_files: Iterable[PathLike]) -> int:
    for file in json_files:
        try:
            with Path(file).open(encoding="UTF-8") as f:
                original_json = json.loads(f.read())

            formatted_json = format_nested_json_strings(original_json)
            formatted_json = json.dumps(formatted_json, ensure_ascii=False, indent=4)

            with Path(file).open("w", encoding="UTF-8") as f:
                f.write(formatted_json)

        except Exception as e:
            msg = f"Error processing {file}: {e}"
            raise ValueError(msg) from e

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="JSON-clean",
        description="Clean PowerBI generated nested JSON files.",
    )
    parser.add_argument(
        "filename",
        nargs="+",  # one or more
        help="One or more filenames or glob patterns to process",
    )

    files = (
        file
        for file_or_glob in parser.parse_args().filename
        for file in Path().glob(file_or_glob)
    )

    _format_json_files(files)


if __name__ == "__main__":
    main()
