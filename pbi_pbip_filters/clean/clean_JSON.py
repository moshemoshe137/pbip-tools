import argparse
import json
from pathlib import Path

from pbi_pbip_filters.json_types import JSONType


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


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="clean_JSON",
        description="Clean PowerBI generated nested JSON files.",
    )
    parser.add_argument("filename", nargs="+", help="One or more filenames to process")

    files = parser.parse_args().filename
    for file in files:
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


if __name__ == "__main__":
    main()
