# PBIP Tools

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-312/)
[![License: MIT](https://img.shields.io/github/license/moshemoshe137/pbip-tools)](https://github.com/moshemoshe137/pbip-tools/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

**PBIP-tools** is a Python package designed to process Power BI-generated JSON files for
enhanced human-readability and seamless version control integration. The package
provides two key executables:

1. **`json-clean`**: Converts nested and complex Power BI-generated JSON files into a
   human-readable format.

2. **`json-smudge`**: Reverses the cleaning process, restoring the JSON files to a
   format that Power BI can properly load.

## Features

- **Human-readable JSON**: The `json-clean` utility de-nests JSON objects and JSON
  strings for easier understanding and editing.

- **Restoration for Power BI**: The `json-smudge` utility ensures that files cleaned by
  `json-clean` can be reloaded into Power BI.

- **Command-line utilities**: Both `json-clean` and `json-smudge` can be used directly
  from the command line for seamless file processing.

## Installation

You can install the package using pip:

```bash
pip install pbip-tools
```

## Usage

### Cleaning a JSON File

To clean a Power BI-generated JSON file for readability, run the following command:

```bash
json-clean <file-or-glob> [<file-or-glob2> ... ]
```

Example:

```bash
json-clean report.json my_folder/*.json
```

### Smudging a JSON File

To restore a cleaned JSON file to its original state for Power BI loading, run:

```bash
json-smudge <file-or-glob> [<file-or-glob2> ...]
```

Example:

```bash
json-smudge cleaned_report.json cleaned/**/*.json
```

## Dependencies

This package depends solely on Python’s standard libraries. For contributing and
testing, `pre-commit` and `pytest` may be required.

## License

This project is licensed under the MIT License. See the
[LICENSE](https://github.com/moshemoshe137/pbip-tools/blob/main/LICENSE) file for
details.

## Contributing

If you would like to contribute, feel free to open issues or submit pull requests.
