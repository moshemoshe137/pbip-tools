import argparse
import json
import re
from pathlib import Path

from pbi_pbip_filters.type_aliases import JSONType, PathLike


def smudge_json(data: JSONType) -> JSONType:
    """
    Converts certain keys' values back to JSON strings for use by Power BI.
    """

    # Define the keys that need to be converted to JSON strings
    conditional_keys = {"config", "filters", "value", "parameters"}

    if isinstance(data, dict):
        for key, value in data.items():
            if key in conditional_keys and isinstance(value, dict | list):
                # Convert these keys back to JSON strings
                data[key] = json.dumps(
                    value,
                    ensure_ascii=False,
                    indent=0,
                    separators=(",", ":"),
                ).replace("\n", "")
            else:
                # Recursively apply the smudge operation
                data[key] = smudge_json(value)
    elif isinstance(data, list):
        data = [smudge_json(item) for item in data]

    return data


def _format_json_files(json_files: list[PathLike]) -> int:
    for file in json_files:
        try:
            with Path(file).open() as f:
                cleaned_original_json = json.loads(f.read())

            smudged_json = smudge_json(cleaned_original_json)
            smudged_json = json.dumps(smudged_json, ensure_ascii=False, indent=2)

            # Force all floats to two decimal places with this regex
            pat = r"""(?x)  # (Turns on comments for this regex.)
                (           # ##### Start Capturing Part 1 (text before the value) #####
                    \s*?:       # Zero or more spaces followed by a colon.
                    \s*?        # There *might* be space after the colon.
                )           # #### Finish Capturing Part 1 (text before the value) #####
                (?P<value>  # ################ Start Capturing "value" #################
                    \d+         # One or more digits...
                    \.          # followed by a literal dot...
                    \d          # followed by exactly one digit in the 10ths place.
                )           # ############### Finish Capturing "value" #################
                (           # ##### Start Capturing Part 3 (text after the value) ######
                    \s*?        # There *might* be space after the digit
                    []},]       # Usually ends with ","; might end with "}" or "]
                )           # #### Finish Capturing Part 13 (text after the value) #####
                """
            replacement = r"\1\g<value>0\3"  # Tack on a zero in the 100ths place.
            smudged_json = re.sub(pat, replacement, smudged_json)

            with Path(file).open("w") as f:
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
        help="One or more filenames to process",
        type=Path,
    )

    files = parser.parse_args().filename
    _format_json_files(files)


if __name__ == "__main__":
    main()
