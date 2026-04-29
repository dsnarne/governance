"""Team validation runner."""

from __future__ import annotations

import asyncio
from http import HTTPStatus
from typing import TYPE_CHECKING

import httpx
from github import GithubException

from meta.clients.github_client import get_github_client
from meta.validator.src.reporter import ErrorCode

if TYPE_CHECKING:
    from meta.models import Member, Team
    from meta.validator.src.reporter import Reporter


class TeamValidator:
    """Run team validation (sync + async) and record results."""

    def __init__(
        self,
        teams: dict[str, Team],
        members: dict[str, Member],
        reporter: Reporter,
    ) -> None:
        """Create a team validator."""
        self.teams = teams
        self.members = members
        self.reporter = reporter

    def validate(self) -> None:
        """Run all team validations and record into the reporter."""
        asyncio.run(self.validate_async())
        self.validate_sync()

    async def validate_async(self) -> None:
        """Run async team checks using a fresh HTTP client."""
        async with httpx.AsyncClient() as _:
            pass

    def validate_sync(self) -> None:
        """Run synchronous team checks."""
        self.validate_leads_are_members()
        self.validate_cross_references()
        self.validate_github_repos_exist()

    def validate_leads_are_members(self) -> None:
        """Ensure every lead is also listed as a member."""
        for team in self.teams.values():
            member_set = set(team.members)
            for lead in team.leads:
                if lead not in member_set:
                    self.reporter.insert_error(
                        team.file_path,
                        ErrorCode.LEAD_CROSS_REFERENCE,
                        f"Lead {lead!r} missing from members",
                    )

    def validate_cross_references(self) -> None:
        """Check that all team contributors exist in contributors."""
        for team in self.teams.values():
            for member in team.members:
                if member not in self.members:
                    self.reporter.insert_error(
                        team.file_path,
                        ErrorCode.MEMBER_CROSS_REFERENCE,
                        f"Unknown member: {member}",
                    )

    def validate_github_repos_exist(self) -> None:
        """Ensure that all GitHub repositories exist."""
        github_client = get_github_client()
        for team in self.teams.values():
            for repo in team.repos:
                try:
                    repo_name = "scottylabs-labrador/" + repo
                    github_client.get_repo(repo_name)
                except GithubException as e:
                    if e.status == HTTPStatus.NOT_FOUND:
                        self.reporter.insert_error(
                            team.file_path,
                            ErrorCode.GITHUB_REPO_NOT_FOUND,
                            f"GitHub repository {repo_name} not found",
                        )
