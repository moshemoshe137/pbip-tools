"""Main package namespace."""

from .clean.clean_JSON import clean_json
from .smudge.smudge_JSON import smudge_json

__all__ = [
    "clean_json",
    "smudge_json",
]
