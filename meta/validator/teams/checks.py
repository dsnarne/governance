"""Validation checks for teams."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from meta.validator.model import (
    Team,
    ValidationError,
    ValidationWarning,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger(__name__)

USER_AGENT = "ScottyLabs-Governance-Validator"
SCOTTYLABS_ORG = "ScottyLabs"

HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_FORBIDDEN = 403


class GitHubRepoCheckError(Exception):
    """Base exception for GitHub repository validation failures."""


class GitHubRateLimitedOrForbiddenError(GitHubRepoCheckError):
    """GitHub request was rate-limited or forbidden."""

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return "Rate limit exceeded or access forbidden"


@dataclass(frozen=True, slots=True)
class GitHubUnexpectedStatusError(GitHubRepoCheckError):
    """GitHub responded with an unexpected status code."""

    status_code: int

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return f"Unexpected status {self.status_code}"


@dataclass(frozen=True, slots=True)
class GitHubRequestError(GitHubRepoCheckError):
    """GitHub request failed at the transport layer."""

    cause: BaseException

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return str(self.cause)

def validate_team_file_names(
    teams: dict[str, Team],
) -> list[ValidationError]:
    """Validate that team file names match slug."""
    logger.info("Validating team file names...")
    errors: list[ValidationError] = []
    for file_path, team in teams.items():
        file_stem = Path(file_path).stem
        if file_stem != team.slug:
            errors.append(
                ValidationError(
                    file=file_path,
                    message=(
                        f"Team file name '{file_stem}' doesn't match slug '{team.slug}'"
                    ),
                ),
            )
    return errors


def validate_maintainers_are_contributors(
    teams: dict[str, Team],
) -> list[ValidationError]:
    """Ensure every maintainer is also listed as a contributor in each timeframe."""
    logger.info("Validating that all maintainers are also contributors...")
    errors: list[ValidationError] = []
    for team_file, team in teams.items():
        for record in team.membership:
            contributor_set = {m.github_username for m in record.contributors}
            errors.extend(
                ValidationError(
                    file=team_file,
                    message=(
                        f"[{record.timeframe}] Maintainer {maintainer!r} "
                        f"missing from contributors"
                    ),
                )
                for maintainer in record.maintainers
                if maintainer not in contributor_set
            )
    return errors


def validate_cross_references(
    contributors: Mapping[str, object],
    teams: dict[str, Team],
) -> list[ValidationError]:
    """Check that all team participants exist in contributors."""
    logger.info("Validating cross-references...")
    errors: list[ValidationError] = []
    for team_file, team in teams.items():
        for record in team.membership:
            participants = list(record.maintainers) + [
                m.github_username for m in record.contributors
            ]
            for participant in participants:
                contributor_file = f"contributors/{participant}.toml"
                if contributor_file not in contributors:
                    errors.append(
                        ValidationError(
                            file=team_file,
                            message=(
                                f"[{record.timeframe}] Unknown contributor: "
                                f"{participant}"
                            ),
                        ),
                    )
    return errors


class RepoCheckResult:
    """Result types for GitHub repository existence checks."""

    EXISTS_IN_ORG = "exists_in_org"
    EXISTS_OUTSIDE_ORG = "exists_outside_org"
    NOT_FOUND = "not_found"


async def _check_github_repository_exists(
    repository: str,
    client: httpx.AsyncClient,
) -> tuple[str, str | None]:
    r"""Return \(`result_type`, `org_or_none`\).

    `result_type` is one of: `exists_in_org`, `exists_outside_org`, `not_found`.
    """
    token = os.environ.get("SYNC_GITHUB_TOKEN", "")
    try:
        headers = {"User-Agent": USER_AGENT}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = await client.get(
            f"https://api.github.com/repos/{repository}",
            headers=headers,
        )
        if r.status_code == HTTP_OK:
            data = r.json()
            org_login = (data.get("organization") or {}).get("login")
            if org_login == SCOTTYLABS_ORG:
                return (RepoCheckResult.EXISTS_IN_ORG, None)
            return (RepoCheckResult.EXISTS_OUTSIDE_ORG, org_login or "<no org>")
        if r.status_code == HTTP_NOT_FOUND:
            return (RepoCheckResult.NOT_FOUND, None)
        if r.status_code == HTTP_FORBIDDEN:
            raise GitHubRateLimitedOrForbiddenError
        raise GitHubUnexpectedStatusError(r.status_code)
    except httpx.HTTPError as e:
        raise GitHubRequestError(e) from e


def _team_repos_to_check(
    teams: dict[str, Team],
) -> list[tuple[str, str, str]]:
    """Flatten team repositories into (team_key, repo) pairs."""
    return [
        (team_file, repo_name, f"{SCOTTYLABS_ORG}/{repo_name}")
        for team_file, team in teams.items()
        for repo_name in team.repos
    ]


def _repo_validation_error(
    file_path: str,
    repo_name: str,
    result_type: str,
    org: str | None,
) -> ValidationError | None:
    if result_type == RepoCheckResult.EXISTS_OUTSIDE_ORG and org:
        return ValidationError(
            file=file_path,
            message=(
                f'GitHub repository {repo_name} is not in the "{SCOTTYLABS_ORG}" '
                f"organization. It is in the {org} organization."
            ),
        )
    if result_type == RepoCheckResult.NOT_FOUND:
        return ValidationError(
            file=file_path,
            message=f"GitHub repository does not exist: {repo_name}",
        )
    return None


async def validate_github_repositories(
    teams: dict[str, Team],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate that team repos exist and are in ScottyLabs org."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    async def check_one(repository: str) -> tuple[str, str | None, str | None]:
        try:
            result_type, org = await _check_github_repository_exists(repository, client)
        except GitHubRepoCheckError as e:
            return ("error", None, str(e))
        else:
            return (result_type, org, None)

    keys_repos = _team_repos_to_check(teams)
    results = await asyncio.gather(
        *(check_one(repository) for _, _, repository in keys_repos),
    )

    for (team_file, repo_name, _), (result_type, org, err_msg) in zip(
        keys_repos,
        results,
        strict=False,
    ):
        if err_msg:
            warnings.append(
                ValidationWarning(
                    file=team_file,
                    message=f"Failed to check GitHub repository {repo_name}: {err_msg}",
                ),
            )
            continue
        err = _repo_validation_error(team_file, repo_name, result_type, org)
        if err is not None:
            errors.append(err)

    return (errors, warnings)
