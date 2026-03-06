"""Helpers for schema-based TOML key ordering validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Mapping

from .model import ValidationError


def load_schema_key_ordering(schema_path: str) -> list[str]:
    """Load JSON schema and return the order of keys in the properties object."""
    text = Path(schema_path).read_text(encoding="utf-8")
    data = json.loads(text)
    properties = data.get("properties", {})
    return list(properties.keys())


class _HasKeyOrder(Protocol):
    """Protocol for models that preserve TOML key ordering."""

    def get_key_order(self) -> list[str]: ...

    def set_key_order(self, order: list[str]) -> None: ...


def _is_subsequence_in_order(
    actual_order: list[str],
    expected_order: list[str],
) -> bool:
    """Check that actual_order is a subsequence of expected_order in the right order."""
    i = 0
    for a in actual_order:
        while i < len(expected_order) and expected_order[i] != a:
            i += 1
        if i == len(expected_order):
            return False
        i += 1
    return True


def validate_key_orderings(
    data: Mapping[str, _HasKeyOrder],
    expected_order: list[str],
) -> list[ValidationError]:
    """Validate key order in TOML files against the expected schema order."""
    if not data:
        return [
            ValidationError(file="N/A", message="No data found"),
        ]
    errors: list[ValidationError] = []
    for file_path, item in data.items():
        actual_order = item.get_key_order()
        if not _is_subsequence_in_order(actual_order, expected_order):
            errors.append(
                ValidationError(
                    file=file_path,
                    message=(
                        f"Invalid key order for {file_path}.\n"
                        f"    - expected (schema): {expected_order}\n"
                        f"    - found (file): {actual_order}"
                    ),
                ),
            )
    return errors
