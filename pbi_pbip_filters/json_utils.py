import json
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
                json_from_file = json.loads(f.read())

            processed_json = process_func(json_from_file)

            with Path(file).open("w", encoding="UTF-8") as f:
                f.write(processed_json)
        except Exception as e:
            msg = f"Error processing {file}: {e}"
            raise ValueError(msg) from e
    return 0
