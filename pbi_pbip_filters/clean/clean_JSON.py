import argparse
import glob
import json
import re

from pbi_pbip_filters.json_utils import _process_and_save_json_files
from pbi_pbip_filters.type_aliases import JSONType


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


def main() -> int:
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
        for file in glob.glob(file_or_glob, recursive=True)
    )

    return _process_and_save_json_files(files, clean_json)


if __name__ == "__main__":
    main()
