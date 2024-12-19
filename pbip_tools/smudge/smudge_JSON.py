"""
Filter to "smudge" Power BI files that have been "cleaned" to their original format.

Process Power BI-generated files that have been cleaned by `json-clean`. This is the
source for the command line utility `json-smudge`. Certain values are converted back to
strings so they can be correctly loaded in Power BI.
"""

import json
import re

from pbip_tools.type_aliases import JSONType


def smudge_json(json_data: JSONType) -> str:
    """
    Convert certain sections back to JSON strings for Power BI compatibility.

    Recursively process and "smudge" Power BI-generated JSON files that have been
    cleaned with `json-clean`. Certain specific keys are converted back to JSON strings.

    Parameters
    ----------
    json_data : JSONType
        The JSON object to be smudged. It may be a list, dictionary, or `JSONPrimitive`.

    Returns
    -------
    str
        The smudged JSON as a Unicode string that is compatible with Power BI projects.

    See Also
    --------
    clean_json : Clean Power-BI generated JSON files for human readability.

    Notes
    -----
    - The following keys will have *all* of their values converted to JSON strings
      whenever possible:
        - "config"
        - "filters"
        - "value"
        - "parameters"
    - The resultant JSON is meant to be openable in Power BI Desktop.
    - Any float with one decimal of precision is automatically assigned a zero in its
      hundredths place.
    """

    def recursively_smudge_json(json_data_subset: JSONType) -> JSONType:
        """
        Recursively revert certain values JSON strings for Power BI compatibility.

        Parameters
        ----------
        json_data_subset : JSONType
            The subset of JSON data to be smudged.

        Returns
        -------
        JSONType
            The smudged subset of JSON data
        """
        # Define the keys that need to be converted to JSON strings
        conditional_keys = {"config", "filters", "value", "parameters"}

        if isinstance(json_data_subset, dict):
            for key, value in json_data_subset.items():
                if key in conditional_keys and isinstance(value, dict | list):
                    # Convert these keys back to JSON strings
                    json_data_subset[key] = json.dumps(
                        value,
                        ensure_ascii=False,
                        indent=0,
                        separators=(",", ":"),  # without trailing whitespace
                        sort_keys=True,
                    ).replace("\n", "")
                else:
                    # Recursively apply the smudge operation
                    json_data_subset[key] = recursively_smudge_json(value)
        elif isinstance(json_data_subset, list):
            json_data_subset = [
                recursively_smudge_json(item) for item in json_data_subset
            ]

        return json_data_subset

    # Recursively smudge the data
    json_data = recursively_smudge_json(json_data)

    # Final post-processing
    data_str = json.dumps(json_data, ensure_ascii=False, indent=2, sort_keys=True)
    data_str = re.sub(pattern_decimal_with_tenths_place_only, replacement, data_str)
    return data_str  # noqa: RET504: "Unnecessary assignment to `data_str` before `return` statement"


pattern_decimal_with_tenths_place_only = r"""(?x)  # (Turns on comments for this regex.)
        (           # !!!!!!!!! Start Capturing Part 1 (text before the value) !!!!!!!!!
            \s*?:       # Zero or more spaces followed by a colon.
            \s*?        # There *might* be space after the colon.
        )           # !!!!!!!! Finish Capturing Part 1 (text before the value) !!!!!!!!!

        (?P<value>  # $$$$$$$$$$$$$$$$$$$$ Start Capturing "value" $$$$$$$$$$$$$$$$$$$$$
            \d+         # One or more digits...
            \.          # followed by a literal dot...
            \d          # followed by exactly one digit in the tenths place.
        )           # $$$$$$$$$$$$$$$$$$$ Finish Capturing "value" $$$$$$$$$$$$$$$$$$$$$

        (           # %%%%%%%%% Start Capturing Part 3 (text after the value) %%%%%%%%%%
            \s*?        # There *might* be space after the digit.
            []},]       # Usually ends with ","; might end with "}" or "]".
        )           # %%%%%%%% Finish Capturing Part 13 (text after the value) %%%%%%%%%
        """

replacement = r"\1\g<value>0\3"  # Tack on a zero in the hundredths place.


def main() -> int:
    """Smudge files from CLI with `json-smudge`."""
    from pbip_tools.cli import _run_main

    return _run_main(
        tool_name="json-smudge",
        desc="Smudge PowerBI-generated JSON files that have been cleaned.",
        filter_function=smudge_json,
    )


if __name__ == "__main__":
    main()
