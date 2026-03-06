"""Load team TOML files from disk."""

from pathlib import Path

import tomli

from meta.validator.common import _toml_key_order
from meta.validator.model import EntityKey, Team

TEAMS_GLOB = "teams/*.toml"


def _parse_team(content: str, key_order: list[str]) -> Team:
    """Parse one team TOML document."""
    data = tomli.loads(content)
    return Team(
        name=data["name"],
        slug=data["slug"],
        maintainers=data["maintainers"],
        contributors=data["contributors"],
        applicants=data.get("applicants"),
        repos=data.get("repos", []),
        slack_channel_ids=data.get("slack-channel-ids", []),
        key_order=key_order,
    )


def load_teams() -> dict[EntityKey, Team]:
    """Load all team TOML files."""
    out: dict[EntityKey, Team] = {}
    for path in sorted(Path().glob(TEAMS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        key_order = _toml_key_order(content)
        t = _parse_team(content, key_order)
        key = EntityKey(kind="team", name=path.stem)
        out[key] = t
    return out
