"""Team validation runner."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx

from meta.validator.key_ordering import load_schema_key_ordering, validate_key_orderings
from meta.validator.teams.checks import (
    validate_cross_references,
    validate_github_repositories,
    validate_maintainers_are_contributors,
    validate_team_file_names,
)

if TYPE_CHECKING:
    from meta.validator.model import Contributor, EntityKey, Team
    from meta.validator.reporter import Reporter


@dataclass(frozen=True, slots=True)
class TeamValidator:
    """Run team validation (sync + async) and record results."""

    teams: dict[EntityKey, Team]
    contributors: dict[EntityKey, Contributor]
    reporter: Reporter
    schema_path: str = "__meta/schemas/team.schema.json"

    def validate(self) -> None:
        """Run all team validations and record into the reporter."""
        self.validate_sync()
        asyncio.run(self.validate_async())

    def validate_sync(self) -> None:
        """Run synchronous team checks."""
        ordering = load_schema_key_ordering(self.schema_path)
        self.reporter.insert_errors(
            validate_key_orderings(self.teams, ordering, kind="team"),
        )
        self.reporter.insert_errors(validate_team_file_names(self.teams))
        self.reporter.insert_errors(validate_maintainers_are_contributors(self.teams))
        self.reporter.insert_errors(
            validate_cross_references(self.contributors, self.teams),
        )

    async def validate_async(self) -> None:
        """Run async team checks using a fresh HTTP client."""
        async with httpx.AsyncClient() as client:
            await self.validate_async_with_client(client)

    async def validate_async_with_client(self, client: httpx.AsyncClient) -> None:
        """Run async team checks using a provided HTTP client."""
        gh_errors, gh_warnings = await validate_github_repositories(self.teams, client)
        self.reporter.insert_errors(gh_errors)
        self.reporter.insert_warnings(gh_warnings)

