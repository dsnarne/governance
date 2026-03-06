"""Load team TOML files from disk."""

from pathlib import Path
from typing import Any

import tomli

from meta.validator.model import Team, TeamMember, TeamMembership

TEAMS_GLOB = "teams/*.toml"


def _parse_team(data: dict[str, Any], key_order: list[str]) -> Team:
    """Parse one team TOML document."""
    repos = [
        str(repo["name"])
        for repo in (data.get("repos") or [])
    ]
    membership = [
        TeamMembership(
            timeframe=str(record["timeframe"]),
            maintainers=list(record["maintainers"]),
            contributors=[
                TeamMember(
                    github_username=str(member["github-username"]),
                    title=(
                        None if member.get("title") is None else str(member["title"])
                    ),
                )
                for member in record["contributors"]
            ],
        )
        for record in (data.get("membership") or [])
    ]
    website = data.get("website")
    return Team(
        slug=str(data["slug"]),
        name=str(data["name"]),
        description=str(data["description"]),
        website=(None if website is None else str(website)),
        create_oidc_clients=bool(data.get("create-oidc-clients", True)),
        repos=repos,
        membership=membership,
        key_order=key_order,
    )


def load_teams() -> dict[str, Team]:
    """Load all team TOML files."""
    out: dict[str, Team] = {}
    for path in sorted(Path().glob(TEAMS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomli.loads(content)
        key_order = list(data.keys())
        t = _parse_team(data, key_order)
        out[f"teams/{path.name}"] = t
    return out
