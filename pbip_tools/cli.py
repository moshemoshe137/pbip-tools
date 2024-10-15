"""Shared CLI logic for clean and smudge filters."""

import argparse
import glob
import json
import sys
from collections.abc import Callable

import pbip_tools
from pbip_tools import clean_json, smudge_json
from pbip_tools.json_utils import (
    _process_and_save_json_files,
    _specified_stdin_instead_of_file,
)
from pbip_tools.type_aliases import JSONType


def _run_main(
    tool_name: str, desc: str, filter_function: Callable[[JSONType], str]
) -> int:
    """
    Entry point for the `json-clean` and `json-smudge` scripts.

    This runner performs common tasks that are relevant to both PBIP filters. It reduces
    duplicates code.

    Parameters
    ----------
    tool_name : str
        The name of the tool (e.g., "clean" or "smudge").
    desc : str
        The description of the tool that will be displayed in the CLI help.
    filter_function : Callable
        The function to filter the data through (e.g. `clean_json` or `smudge_json`).
        The passed function must accept JSON-like data and return a string.

    Returns
    -------
    int
        Returns 0 on successful processing of all files.
    """
    parser = argparse.ArgumentParser(prog=f"pbip-tools {tool_name}", description=desc)

    parser.add_argument(
        "filenames",
        nargs="+",  # one or more
        help=(
            "One or more filenames or glob patterns to process, or pass '-' to read"
            "from stdin and write to stdout."
        ),
        metavar="filename_or_glob",  # Name shown in CLI help text.
    )

    args = parser.parse_args()

    # Read from stdin and print to stdout when `-` is given as the filename.
    if _specified_stdin_instead_of_file(args.filenames):
        json_data = json.load(sys.stdin)
        filtered_json = filter_function(json_data)
        sys.stdout.write(filtered_json)
        return 0

    # Otherwise, we're processing one or more files or glob patterns.
    files = (
        file
        for file_or_glob in args.filenames
        for file in glob.glob(file_or_glob, recursive=True)
    )

    return _process_and_save_json_files(files, filter_function)


def main() -> int:
    """Primary entry point for `pbip-tools`."""
    parser = argparse.ArgumentParser("pbip-tools", description="PBIP tools for CLI.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    clean_parser, smudge_parser = (
        subparsers.add_parser("clean"),
        subparsers.add_parser("smudge"),
    )

    for subparser in [parser, clean_parser, smudge_parser]:
        subparser.add_argument(
            "filenames",
            nargs="+",  # one or more
            help=(
                "One or more filenames or glob patterns to process, or pass '-' to read"
                "from stdin and write to stdout."
            ),
            metavar="filename_or_glob",  # Name shown in CLI help text.
        )
    args = parser.parse_args()

    # if args.command == "clean":
    #     return pbip_tools.clean.clean_JSON.main()
    # if args.command == "smudge":
    #     return pbip_tools.smudge_json.smudge_JSON.main()
    if args.command not in ["clean", "smudge"]:
        parser.print_help()
        return 1
    if args.command == "clean":
        filter_function = clean_json
    elif args.command == "smudge":
        filter_function = smudge_json

    # Read from stdin and print to stdout when `-` is given as the filename.
    if _specified_stdin_instead_of_file(args.filenames):
        json_data = json.load(sys.stdin)
        filtered_json = filter_function(json_data)
        sys.stdout.write(filtered_json)
        return 0
    if args.command == "clean":
        return pbip_tools.clean.clean_JSON.main()
    if args.command == "smudge":
        return pbip_tools.smudge.smudge_JSON.main()

    # Otherwise, we're processing one or more files or glob patterns.
    files = (
        file
        for file_or_glob in args.filenames
        for file in glob.glob(file_or_glob, recursive=True)
    )

    return _process_and_save_json_files(files, filter_function)
