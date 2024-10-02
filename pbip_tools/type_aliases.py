"""
Type aliases for easy type hinting throughout the project.

Attributes
----------
JSONPrimitive : TypeAlias
    Represents JSON primitive types: string, numeric, boolean, or None.
JSONType : TypeAlias
    Represents the recursive structure of a JSON object.
PathLike : TypeAlias
    Represents file system paths, but behaves a little nicer than `os.PathLike`.
"""

# (Attempt to) define type aliases for JSON data...
import os
from pathlib import Path
from typing import Any, TypeAlias

JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONType: TypeAlias = dict[str | int, "JSONType"] | list["JSONType"] | JSONPrimitive

# A custom "PathLike" type alias (that works as expected...)
PathLike: TypeAlias = str | Path | os.PathLike[Any]
