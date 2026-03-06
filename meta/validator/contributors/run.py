"""Run all contributor validation and record results into file_messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from meta.validator.common import load_schema_key_ordering, validate_key_orderings
from meta.validator.contributors.checks import (
    validate_contributor_file_names,
    validate_github_users,
    validate_slack_member_ids,
)

if TYPE_CHECKING:
    import httpx

    from meta.validator.model import Contributor, EntityKey
    from meta.validator.reporter import Reporter

CONTRIBUTOR_SCHEMA_PATH = "__meta/schemas/contributor.schema.json"


def run_sync(
    contributors: dict[EntityKey, Contributor],
    reporter: Reporter,
) -> None:
    """Run synchronous contributor checks and record results in reporter."""
    ordering = load_schema_key_ordering(CONTRIBUTOR_SCHEMA_PATH)
    for error in validate_key_orderings(
        contributors,
        ordering,
        kind="contributor",
    ):
        reporter.insert_error(error)
    for error in validate_contributor_file_names(contributors):
        reporter.insert_error(error)


async def run_async(
    contributors: dict[EntityKey, Contributor],
    client: httpx.AsyncClient,
    reporter: Reporter,
) -> None:
    """Run async contributor checks and record results in reporter."""
    gh_errors, gh_warnings = await validate_github_users(contributors, client)
    for error in gh_errors:
        reporter.insert_error(error)
    for warning in gh_warnings:
        reporter.insert_warning(warning)

    slack_errors, slack_warnings = await validate_slack_member_ids(
        contributors,
        client,
    )
    for error in slack_errors:
        reporter.insert_error(error)
    for warning in slack_warnings:
        reporter.insert_warning(warning)
