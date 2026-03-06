"""Contributor validation runner."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx

from meta.validator.common import load_schema_key_ordering, validate_key_orderings
from meta.validator.contributors.checks import (
    validate_contributor_file_names,
    validate_github_users,
    validate_slack_member_ids,
)

if TYPE_CHECKING:
    from meta.validator.model import Contributor, EntityKey
    from meta.validator.reporter import Reporter


@dataclass(frozen=True, slots=True)
class ContributorValidator:
    """Run contributor validation (sync + async) and record results."""

    contributors: dict[EntityKey, Contributor]
    reporter: Reporter
    schema_path: str = "__meta/schemas/contributor.schema.json"

    def validate(self) -> None:
        """Run all contributor validations and record into the reporter."""
        self.validate_sync()
        asyncio.run(self.validate_async())

    def validate_sync(self) -> None:
        """Run synchronous contributor checks."""
        ordering = load_schema_key_ordering(self.schema_path)
        for error in validate_key_orderings(
            self.contributors,
            ordering,
            kind="contributor",
        ):
            self.reporter.insert_error(error)
        for error in validate_contributor_file_names(self.contributors):
            self.reporter.insert_error(error)

    async def validate_async(self) -> None:
        """Run async contributor checks using a fresh HTTP client."""
        async with httpx.AsyncClient() as client:
            await self.validate_async_with_client(client)

    async def validate_async_with_client(self, client: httpx.AsyncClient) -> None:
        """Run async contributor checks using a provided HTTP client."""
        gh_errors, gh_warnings = await validate_github_users(self.contributors, client)
        for error in gh_errors:
            self.reporter.insert_error(error)
        for warning in gh_warnings:
            self.reporter.insert_warning(warning)

        slack_errors, slack_warnings = await validate_slack_member_ids(
            self.contributors,
            client,
        )
        for error in slack_errors:
            self.reporter.insert_error(error)
        for warning in slack_warnings:
            self.reporter.insert_warning(warning)

