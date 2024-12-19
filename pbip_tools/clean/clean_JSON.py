"""
Filter to "clean" Power BI-generated JSON files for human-readability.

Process Power BI-generated JSON files by recursively de-nesting JSON and JSON strings
for human readability. This is the source for the command line utility `json-clean`. The
cleaned files *must* be smudged with the `json-smudge` filter before they are loaded
in Power BI again.
"""

import json
import re

from pbip_tools.type_aliases import JSONType

MAX_LINE_LEN: int = 88


def clean_json(json_data: JSONType, indent: int = 2) -> str:
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

    json_str = json.dumps(json_data, ensure_ascii=False, indent=indent)
    return post_process_json_string(json_str)


def post_process_json_string(json_string: str) -> str:
    """
    Condense JSON key-value pairs where possible, preserving indentation and structure.

    Parameters
    ----------
    json_string : str
        The JSON string to process.
    max_line_len : int
        Maximum allowed length for a single line.

    Returns
    -------
    str
        Condensed JSON string.
    """
    lines = json_string.splitlines()
    result = []
    buffer: list[str] = []

    for line in lines:
        stripped_line = line.strip()

        # If buffer has collected a JSON key and a partial value
        if buffer:
            buffer.append(line)
            if stripped_line.endswith(("}", "]")):
                # Check if the buffered lines can fit on one line
                combined = " ".join(buf.strip() for buf in buffer)
                if len(combined) <= MAX_LINE_LEN:
                    result.append(combined)
                else:
                    result.extend(buffer)  # If not, append as-is
                buffer = []  # Clear the buffer
            continue

        # Detect start of a potential single-line condensible structure
        if stripped_line.endswith(("{", "[")):
            buffer.append(line)
        else:
            result.append(line)  # Regular line, add to result

    return "\n".join(result)


def main() -> int:
    """Clean files from CLI with `json-clean`."""
    from pbip_tools.cli import _run_main

    return _run_main(
        tool_name="json-clean",
        desc="Clean PowerBI generated nested JSON files.",
        filter_function=clean_json,
    )


if __name__ == "__main__":
    main()
