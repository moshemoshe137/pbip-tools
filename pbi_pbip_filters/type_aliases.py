# (Attempt to) define type aliases for JSON data...
import os
from pathlib import Path
from typing import Any, TypeAlias

JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONType: TypeAlias = dict[str | int, "JSONType"] | list["JSONType"] | JSONPrimitive

# A custom "PathLike" type alias (that works as expected...)
PathLike: TypeAlias = str | Path | os.PathLike[Any]
