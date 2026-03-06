"""Load contributor TOML files from disk."""

from pathlib import Path

import tomli

from meta.validator.common import _toml_key_order
from meta.validator.model import Contributor, EntityKey

CONTRIBUTORS_GLOB = "contributors/*.toml"


def _parse_contributor(content: str, key_order: list[str]) -> Contributor:
    """Parse one contributor TOML document."""
    data = tomli.loads(content)
    return Contributor(
        full_name=data["full-name"],
        github_username=data["github-username"],
        slack_member_id=data.get("slack-member-id"),
        key_order=key_order,
    )


def load_contributors() -> dict[EntityKey, Contributor]:
    """Load all contributor TOML files."""
    out: dict[EntityKey, Contributor] = {}
    for path in sorted(Path().glob(CONTRIBUTORS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        key_order = _toml_key_order(content)
        c = _parse_contributor(content, key_order)
        key = EntityKey(kind="contributor", name=path.stem)
        out[key] = c
    return out
