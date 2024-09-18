import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path

from pbi_pbip_filters.type_aliases import JSONType, PathLike


def clean_json(json_data: JSONType) -> str:
    def format_nested_json_strings(json_data_subset: JSONType) -> JSONType:
        if not isinstance(json_data_subset, dict | list):
            return json_data_subset

        index = (
            range(len(json_data_subset))
            if isinstance(json_data_subset, list)
            else json_data_subset.keys()
        )
        for list_position_or_dict_key in index:
            value = json_data_subset[list_position_or_dict_key]  # type: ignore[index]
            if isinstance(value, dict | list):
                json_data_subset[list_position_or_dict_key] = (  # type:ignore[index]
                    format_nested_json_strings(value)
                )
            elif isinstance(value, str):
                number_pattern = r"^-?\d+(?:\.\d+)?$"
                boolean_pattern = r"true|false"
                num_or_bool_pat = number_pattern + "|" + boolean_pattern
                if re.match(num_or_bool_pat, value, flags=re.IGNORECASE):
                    # Do NOT parse raw numbers and booleans. Doing so may change their
                    # datatypes and make cleaning irreversible. Instead, preserve the
                    # datatypes as they appeared in the original JSON, even if that's a
                    # number or a boolean formatted as a string.
                    continue
                try:
                    parsed_value = json.loads(value)
                    formatted_value = format_nested_json_strings(parsed_value)
                    json_data_subset[list_position_or_dict_key] = (  # type:ignore[index]
                        formatted_value
                    )
                except json.JSONDecodeError:
                    continue
        return json_data_subset

    json_data = format_nested_json_strings(json_data)

    return json.dumps(json_data, ensure_ascii=False, indent=4)


def _format_json_files(json_files: Iterable[PathLike]) -> int:
    for file in json_files:
        try:
            with Path(file).open(encoding="UTF-8") as f:
                original_json = json.loads(f.read())

            formatted_json = clean_json(original_json)

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
