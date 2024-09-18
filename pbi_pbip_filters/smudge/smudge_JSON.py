import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path

from pbi_pbip_filters.type_aliases import JSONType, PathLike


def smudge_json(data: JSONType) -> str:
    """
    Converts certain keys' values back to JSON strings for use by Power BI.
    """

    def recursively_smudge_json(json_subset: JSONType) -> JSONType:
        """
        Converts certain keys' values back to JSON strings for use by Power BI.
        """
        # Define the keys that need to be converted to JSON strings
        conditional_keys = {"config", "filters", "value", "parameters"}

        if isinstance(json_subset, dict):
            for key, value in json_subset.items():
                if key in conditional_keys and isinstance(value, dict | list):
                    # Convert these keys back to JSON strings
                    json_subset[key] = json.dumps(
                        value,
                        ensure_ascii=False,
                        indent=0,
                        separators=(",", ":"),
                    ).replace("\n", "")
                else:
                    # Recursively apply the smudge operation
                    json_subset[key] = recursively_smudge_json(value)
        elif isinstance(json_subset, list):
            json_subset = [recursively_smudge_json(item) for item in json_subset]

        return json_subset

    # Recursively smudge the data
    data = recursively_smudge_json(data)

    # Final post-processing
    data_str = json.dumps(data, ensure_ascii=False, indent=2)
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

replacement = r"\1\g<value>0\3"  # Tack on a zero in the thousandths place.


def _format_json_files(json_files: Iterable[PathLike]) -> int:
    for file in json_files:
        try:
            with Path(file).open(encoding="UTF-8") as f:
                cleaned_original_json = json.loads(f.read())

            smudged_json = smudge_json(cleaned_original_json)

            with Path(file).open("w", encoding="UTF-8") as f:
                f.write(smudged_json)

        except Exception as e:
            msg = f"Error processing {file}: {e}"
            raise ValueError(msg) from e

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="json-smudge",
        description="Smudge PowerBI-generated JSON files that have been cleaned.",
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
