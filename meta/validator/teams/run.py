"""Run all team validation and record results into file_messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from meta.validator.key_ordering import load_schema_key_ordering, validate_key_orderings
from meta.validator.teams.checks import (
    validate_cross_references,
    validate_github_repositories,
    validate_maintainers_are_contributors,
    validate_team_file_names,
)

if TYPE_CHECKING:
    import httpx

    from meta.validator.model import Contributor, Team
    from meta.validator.reporter import Reporter

TEAM_SCHEMA_PATH = "__meta/schemas/team.schema.json"


def run_sync(
    teams: dict[str, Team],
    contributors: dict[str, Contributor],
    reporter: Reporter,
) -> None:
    """Run synchronous team checks and record results in reporter."""
    ordering = load_schema_key_ordering(TEAM_SCHEMA_PATH)
    reporter.insert_errors(validate_key_orderings(teams, ordering))
    reporter.insert_errors(validate_team_file_names(teams))
    reporter.insert_errors(validate_maintainers_are_contributors(teams))
    reporter.insert_errors(validate_cross_references(contributors, teams))


async def run_async(
    teams: dict[str, Team],
    client: httpx.AsyncClient,
    reporter: Reporter,
) -> None:
    """Run async team checks and record results in reporter."""
    gh_errors, gh_warnings = await validate_github_repositories(teams, client)
    reporter.insert_errors(gh_errors)
    reporter.insert_warnings(gh_warnings)
