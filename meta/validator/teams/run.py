"""Run all team validation and record results into file_messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from meta.validator.common import load_schema_key_ordering, validate_key_orderings
from meta.validator.teams.checks import (
    validate_cross_references,
    validate_github_repositories,
    validate_maintainers_are_contributors,
    validate_slack_channel_ids,
    validate_team_file_names,
)

if TYPE_CHECKING:
    import httpx

    from meta.validator.model import Contributor, EntityKey, Team
    from meta.validator.reporter import Reporter

TEAM_SCHEMA_PATH = "__meta/schemas/team.schema.json"


def run_sync(
    teams: dict[EntityKey, Team],
    contributors: dict[EntityKey, Contributor],
    reporter: Reporter,
) -> None:
    """Run synchronous team checks and record results in reporter."""
    ordering = load_schema_key_ordering(TEAM_SCHEMA_PATH)
    for error in validate_key_orderings(teams, ordering, kind="team"):
        reporter.insert_error(error)
    for error in validate_team_file_names(teams):
        reporter.insert_error(error)
    for error in validate_maintainers_are_contributors(teams):
        reporter.insert_error(error)
    for error in validate_cross_references(contributors, teams):
        reporter.insert_error(error)


async def run_async(
    teams: dict[EntityKey, Team],
    client: httpx.AsyncClient,
    reporter: Reporter,
) -> None:
    """Run async team checks and record results in reporter."""
    gh_errors, gh_warnings = await validate_github_repositories(teams, client)
    for error in gh_errors:
        reporter.insert_error(error)
    for warning in gh_warnings:
        reporter.insert_warning(warning)

    slack_errors, slack_warnings = await validate_slack_channel_ids(
        teams,
        client,
    )
    for error in slack_errors:
        reporter.insert_error(error)
    for warning in slack_warnings:
        reporter.insert_warning(warning)
