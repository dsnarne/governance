"""Validation checks for teams."""

import asyncio
import logging
import os
from dataclasses import dataclass

import httpx

from meta.validator.model import (
    Contributor,
    EntityKey,
    Team,
    ValidationError,
    ValidationWarning,
)

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


class SlackCheckError(Exception):
    """Base exception for Slack validation failures."""


class SlackTokenMissingError(SlackCheckError):
    """Slack token is missing from the environment."""

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return "SLACK_TOKEN environment variable not set"


@dataclass(frozen=True, slots=True)
class SlackInvalidChannelIdError(SlackCheckError):
    """Slack channel ID does not match expected format."""

    channel_id: str

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return f"Invalid Slack channel ID format: {self.channel_id}"


class SlackRateLimitedError(SlackCheckError):
    """Slack request was rate-limited."""

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return "Rate limit exceeded"


class SlackInvalidAuthError(SlackCheckError):
    """Slack authentication is invalid."""

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return "Invalid authentication"


@dataclass(frozen=True, slots=True)
class SlackApiError(SlackCheckError):
    """Slack API returned an error code."""

    code: str

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return f"Slack API error: {self.code}"


class SlackUnexpectedResponseError(SlackCheckError):
    """Slack API returned an unexpected response shape."""

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return "Unexpected response from Slack API"

def validate_team_file_names(
    teams: dict[EntityKey, Team],
) -> list[ValidationError]:
    """Validate that team file names match slug."""
    logger.info("Validating team file names...")
    errors: list[ValidationError] = []
    for key, team in teams.items():
        if key.name != team.slug:
            errors.append(
                ValidationError(
                    file=f"teams/{key.name}.toml",
                    message=(
                        f"Team file name '{key.name}' doesn't match slug '{team.slug}'"
                    ),
                ),
            )
    return errors


def validate_maintainers_are_contributors(
    teams: dict[EntityKey, Team],
) -> list[ValidationError]:
    """Ensure every maintainer is also listed as a contributor."""
    logger.info("Validating that all maintainers are also contributors...")
    errors: list[ValidationError] = []
    for team_key, team in teams.items():
        contributor_set = set(team.contributors)
        errors.extend(
            ValidationError(
                file=f"teams/{team_key.name}.toml",
                message=f"Maintainer '{maintainer}' is not a contributor",
            )
            for maintainer in team.maintainers
            if maintainer not in contributor_set
        )
    return errors


def validate_cross_references(
    contributors: dict[EntityKey, Contributor],
    teams: dict[EntityKey, Team],
) -> list[ValidationError]:
    """Check that all team participants exist in contributors."""
    logger.info("Validating cross-references...")
    errors: list[ValidationError] = []
    for team_key, team in teams.items():
        participants = list(team.maintainers) + list(team.contributors)
        if team.applicants:
            participants.extend(team.applicants)
        for participant in participants:
            key = EntityKey(kind="contributor", name=participant)
            if key not in contributors:
                errors.append(
                    ValidationError(
                        file=f"teams/{team_key.name}.toml",
                        message=(
                            f"Team '{team_key.name}' references non-existent "
                            f"contributor: {participant}"
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


def _team_repos_to_check(teams: dict[EntityKey, Team]) -> list[tuple[EntityKey, str]]:
    """Flatten team repositories into (team_key, repo) pairs."""
    return [
        (team_key, repo)
        for team_key, team in teams.items()
        for repo in team.repos
    ]


def _repo_validation_error(
    file_path: str,
    repo: str,
    result_type: str,
    org: str | None,
) -> ValidationError | None:
    if result_type == RepoCheckResult.EXISTS_OUTSIDE_ORG and org:
        return ValidationError(
            file=file_path,
            message=(
                f'GitHub repository {repo} is not in the "{SCOTTYLABS_ORG}" '
                f"organization. It is in the {org} organization."
            ),
        )
    if result_type == RepoCheckResult.NOT_FOUND:
        return ValidationError(
            file=file_path,
            message=f"GitHub repository does not exist: {repo}",
        )
    return None


async def validate_github_repositories(
    teams: dict[EntityKey, Team],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate that team repos exist and are in ScottyLabs org."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    async def check_one(repo: str) -> tuple[str, str | None, str | None]:
        try:
            result_type, org = await _check_github_repository_exists(repo, client)
        except GitHubRepoCheckError as e:
            return ("error", None, str(e))
        else:
            return (result_type, org, None)

    keys_repos = _team_repos_to_check(teams)
    results = await asyncio.gather(*(check_one(repo) for _, repo in keys_repos))

    for (team_key, repo), (result_type, org, err_msg) in zip(
        keys_repos,
        results,
        strict=False,
    ):
        file_path = f"teams/{team_key.name}.toml"
        if err_msg:
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check GitHub repository {repo}: {err_msg}",
                ),
            )
            continue
        err = _repo_validation_error(file_path, repo, result_type, org)
        if err is not None:
            errors.append(err)

    return (errors, warnings)


async def _check_slack_channel_exists(
    channel_id: str,
    client: httpx.AsyncClient,
) -> bool | None:
    """Return True if exists, False if not found, raise on auth/rate limit."""
    token = os.environ.get("SLACK_TOKEN", "")
    if not token:
        raise SlackTokenMissingError
    if not channel_id.startswith(("C", "G")):
        raise SlackInvalidChannelIdError(channel_id)

    r = await client.get(
        "https://slack.com/api/conversations.info",
        params={"channel": channel_id},
        headers={"User-Agent": USER_AGENT, "Authorization": f"Bearer {token}"},
    )
    data = r.json()
    ok = data.get("ok")
    if ok is True:
        return True
    if ok is False:
        err = data.get("error", "")
        if err == "channel_not_found":
            return False
        if err == "ratelimited":
            raise SlackRateLimitedError
        if err == "invalid_auth":
            raise SlackInvalidAuthError
        raise SlackApiError(err)
    raise SlackUnexpectedResponseError


async def validate_slack_channel_ids(
    teams: dict[EntityKey, Team],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate Slack channel IDs for teams."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    items = [
        (team_key, channel_id)
        for team_key, team in teams.items()
        for channel_id in team.slack_channel_ids
    ]

    async def check_one(
        team_key: EntityKey,
        channel_id: str,
    ) -> tuple[EntityKey, str, bool | None, str | None]:
        try:
            exists = await _check_slack_channel_exists(channel_id, client)
        except SlackCheckError as e:
            return (team_key, channel_id, None, str(e))
        else:
            return (team_key, channel_id, exists, None)

    tasks = [check_one(team_key, cid) for team_key, cid in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        team_key, channel_id = items[i]
        file_path = f"teams/{team_key.name}.toml"
        if isinstance(res, BaseException):
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check Slack ID {channel_id}: {res}",
                ),
            )
            continue
        _, cid, exists, err_msg = res
        if err_msg:
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check Slack ID {cid}: {err_msg}",
                ),
            )
            continue
        if exists is False:
            errors.append(
                ValidationError(
                    file=file_path,
                    message=f"Slack channel ID does not exist: {cid}",
                ),
            )
    return (errors, warnings)
