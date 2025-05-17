"""Shared CLI logic for clean and smudge filters."""

import argparse
import glob
import json
import sys
from collections.abc import Callable

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
            " from stdin and write to stdout."
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
    parser = create_argparser()
    args = parser.parse_args()

    if args.command not in ["clean", "smudge"]:
        parser.print_help()
        return 1

    filter_function = {
        "clean": lambda text: clean_json(
            text, indent=args.indent, ignore_list_order=args.ignore_list_order
        ),
        "smudge": smudge_json,
    }[args.command]

    # Read from stdin and print to stdout when `-` is given as the filename.
    if _specified_stdin_instead_of_file(args.filenames):
        json_data = json.load(sys.stdin)
        filtered_json = filter_function(json_data)
        sys.stdout.write(filtered_json)
        return 0

    files = (
        file
        for file_or_glob in args.filenames
        for file in glob.glob(file_or_glob, recursive=True)
    )
    return _process_and_save_json_files(files, filter_function)


def create_argparser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        "pbip-tools",
        description="PBIP tools for CLI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    clean_parser, smudge_parser = (
        subparsers.add_parser("clean", help="Clean JSON files."),
        subparsers.add_parser("smudge", help="Smudge JSON files."),
    )

    for subparser in [clean_parser, smudge_parser]:
        subparser.add_argument(
            "filenames",
            nargs="+",  # one or more
            help=(
                "One or more filenames or glob patterns to process, or pass '-' to read"
                " from stdin and write to stdout."
            ),
            metavar="filename_or_glob",  # Name shown in CLI help text.
        )

    clean_parser.add_argument(
        "--indent", type=int, default=2, help="number of spaces to use for indentation."
    )
    clean_parser.add_argument(
        "--ignore-list-order",
        action="store_true",
        default=False,
        help="Ignore the order of lists when cleaning JSON files.",
    )
    return parser
