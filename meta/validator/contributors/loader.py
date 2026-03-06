"""Load contributor TOML files from disk."""

from pathlib import Path
from typing import Any

import tomli

from meta.validator.model import Contributor

CONTRIBUTORS_GLOB = "contributors/*.toml"


def _parse_contributor(data: dict[str, Any], key_order: list[str]) -> Contributor:
    """Parse one contributor TOML document."""
    return Contributor(
        full_name=str(data["full-name"]),
        andrew_id=(None if data.get("andrew-id") is None else str(data["andrew-id"])),
        key_order=key_order,
    )


def load_contributors() -> dict[str, Contributor]:
    """Load all contributor TOML files."""
    out: dict[str, Contributor] = {}
    for path in sorted(Path().glob(CONTRIBUTORS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomli.loads(content)
        key_order = list(data.keys())
        c = _parse_contributor(data, key_order)
        out[f"contributors/{path.name}"] = c
    return out
