"""Utility functions to process and save JSON files."""

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
    """
    Apply a processing function to a JSON file and save it in-place.

    Read each JSON file specified in `json_files`, process its content using the
    provided `process_func`, and save the processed contents back to the original file.
    If a file contains JSON5-style comments, **it is skipped completely** and is
    unchanged.

    Parameters
    ----------
    json_files : Iterable[PathLike]
        A `list` or `Iterable` of PathLike representations of your JSON files.
    process_func : Callable[[JSONType], str]
        A callable processing function that takes loaded JSON objects and returns a
        `str` of the processed content.

    Returns
    -------
    int
        Returns 0 on successful processing (or skipping) of all files.

    Raises
    ------
    ValueError
        Raised when there is an issue loading or processing the file.

    Warns
    -----
    UserWarning
        A warning is raised if a file with JSON5-style comments is skipped.

    Notes
    -----
    Any document that is detected to contain JSON5-style line comments (denoted by `//`)
    will be automatically skipped. These file will not be processed or overwritten.
    """
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
    """
    Check a JSON string for line comments, denoted by `//`.

    Parameters
    ----------
    json_str : str
        The JSON text to check for line comments.

    Returns
    -------
    bool
        Returns `True` if the JSON string contains line comments and `False` otherwise.

    Examples
    --------
    >>> contains_line_comments('''{
    ...     "key": "value"
    ...     // v cool
    ... }
    ... ''')
    True
    >>> contains_line_comments('''{
    ...     "key": "value"
    ... }
    ... ''')
    False
    """
    single_line_comment_regex = r"(?m)^\s*\/\/.*$"
    return bool(re.search(single_line_comment_regex, json_str))
