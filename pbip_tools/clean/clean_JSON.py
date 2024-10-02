"""
Filter to "clean" Power BI-generated JSON files for human-readability.

Process Power BI-generated JSON files by recursively de-nesting JSON and JSON strings
for human readability. This is the source for the command line utility `json-clean`. The
cleaned files *must* be smudged with the `json-smudge` filter before they are loaded
in Power BI again.
"""

import argparse
import glob
import json
import re
import sys

from pbip_tools.json_utils import (
    _process_and_save_json_files,
    _specified_stdin_instead_of_file,
)
from pbip_tools.type_aliases import JSONType


def clean_json(json_data: JSONType) -> str:
    """
    Clean and format nested JSON data for human-readability.

    Recursively process and "clean" JSON data using `format_nested_json_strings`. If a
    string contains valid JSON, it is also recursively cleaned. This function makes a
    best-effort to preserve the original JSON datatypes for Power BI compatibility.

    Parameters
    ----------
    json_data : JSONType
        The JSON data to be cleaned and formatted. It may be a list, dictionary, or
        `JSONPrimitive`.

    Returns
    -------
    str
        The cleaned and formatted JSON as a Unicode string

    See Also
    --------
    smudge_json : Smudge cleaned JSON files.

    Notes
    -----
    - This function makes a best-effort attempt to preserve datatypes from the original
      JSON to ensure reversibility.
    - If a string value contains valid JSON, it is also recursively parsed and cleaned.
    """

    def format_nested_json_strings(json_data_subset: JSONType) -> JSONType:
        """
        Recursively format nested JSON with nested JSON strings.

        Parameters
        ----------
        json_data_subset : JSONType
            The subset of JSON data to process.

        Returns
        -------
        JSONType
            The cleaned subset of JSON data
        """
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
    """
    Clean files from CLI with `json-clean`.

    Process command line files or glob patterns and clean each file in-place.

    Returns
    -------
    int
        Returns 0 on successful processing of all files.
    """
    parser = argparse.ArgumentParser(
        prog="json-clean",
        description="Clean PowerBI generated nested JSON files.",
    )
    parser.add_argument(
        "filenames",
        nargs="+",  # one or more
        help=(
            "One or more filenames or glob patterns to process, or pass '-' to read "
            "from stdin and write to stdout."
        ),
        metavar="filename_or_glob",  # Name shown in CLI help text.
    )

    args = parser.parse_args()

    # Read from stdin and print to stdout when `-` is given as the filename.
    if _specified_stdin_instead_of_file(args.filenames):
        json_data = json.load(sys.stdin)
        filtered_json = clean_json(json_data)
        sys.stdout.write(filtered_json)
        return 0

    # Otherwise, we're processing one or more files or glob patterns.
    files = (
        file
        for file_or_glob in args.filenames
        for file in glob.glob(file_or_glob, recursive=True)
    )

    return _process_and_save_json_files(files, clean_json)


if __name__ == "__main__":
    main()
