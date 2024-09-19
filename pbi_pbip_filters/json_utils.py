import json
import re
import warnings
from collections.abc import Callable, Iterable
from pathlib import Path

from pbi_pbip_filters.type_aliases import JSONType, PathLike


def _process_and_save_json_files(
    json_files: Iterable[PathLike],
    process_func: Callable[[JSONType], str],
) -> int:
    for file in json_files:
        try:
            with Path(file).open(encoding="UTF-8") as f:
                json_from_file_as_str = f.read()

            if contains_line_comments(json_from_file_as_str):
                # We can't currently process files that use JSON5-style comments.
                warning_msg = f'Skipping file with comments: "{file}"'
                warnings.warn(warning_msg, UserWarning, stacklevel=2)
                continue

            json_from_file = json.loads(json_from_file_as_str)
            processed_json = process_func(json_from_file)

            with Path(file).open("w", encoding="UTF-8") as f:
                f.write(processed_json)
        except Exception as e:
            msg = f"Error processing {file}: {e}"
            raise ValueError(msg) from e
    return 0


def contains_line_comments(json_str: str) -> bool:
    single_line_comment_regex = r"(?m)^\s*\/\/.*$"
    return bool(re.search(single_line_comment_regex, json_str))
