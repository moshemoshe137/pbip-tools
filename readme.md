# PBIP Tools

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-312/)
[![License: MIT](https://img.shields.io/github/license/moshemoshe137/pbip-tools)](https://github.com/moshemoshe137/pbip-tools/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

**PBIP-tools** is a Python package designed to process Power BI-generated JSON files for
enhanced human-readability and seamless version control integration. The package
provides two key programs:

1. **`pbip-tools clean`**: Converts nested and complex Power BI-generated JSON files
   into a human-readable format.

2. **`pbip-tools smudge`**: Reverses the cleaning process, restoring the JSON files to a
   format that Power BI can properly load.

## Features

- **Human-readable JSON**: The `pbip-tools clean` utility de-nests JSON objects and JSON
  strings for easier understanding and editing.

- **Restoration for Power BI**: The `pbip-tools smudge` utility ensures that files
  cleaned by `pbip-tools clean` can be reloaded into Power BI.

- **Command-line utilities**: Both filters can be used directly from the command line
  for seamless file processing.

## Installation

You can install the package [from PyPI](https://pypi.org/project/pbip-tools/) with pip:

```bash
pip install pbip-tools
```

## Usage

### Cleaning a JSON File

To clean a Power BI-generated JSON file for readability, run the following command:

```bash
pbip-tools clean [options] <file-or-glob> [<file-or-glob2> ... ]
```

**Clean Options:**

- `--indent=<n>`

  Use `<n>` spaces to use for indentation instead of the usual `2`.

- `--sort-lists`

  Sort JSON arrays before printing for consistent diffs.

  **Note:** Do NOT use `--sort-lists` if the input order of your lists is important.

Example:

```bash
pbip-tools clean --indent=4 report.json my_folder/*.json
```

### Smudging a JSON File

To restore a "cleaned" JSON file to its original state for Power BI loading, run:

```bash
pbip-tools smudge <file-or-glob> [<file-or-glob2> ...]
```

Example:

```bash
pbip-tools smudge cleaned_report.json cleaned/**/*.json
```

### Global Options

- `-h`, `--help`

  Show help message and exit.

<!-- TODO

- `--version`

  Show version information and exit
-->

## Dependencies

This package depends solely on Python’s standard libraries. `tox` is required for
contributing and testing.

## License

This project is licensed under the MIT License. See the
[LICENSE](https://github.com/moshemoshe137/pbip-tools/blob/main/LICENSE) file for
details.

## Contributing

If you would like to contribute, feel free to open issues or submit pull requests.
