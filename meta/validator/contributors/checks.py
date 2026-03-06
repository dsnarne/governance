"""Validation checks for contributors."""

import asyncio
import logging
import os
from dataclasses import dataclass

import httpx

from meta.validator.model import (
    Contributor,
    EntityKey,
    ValidationError,
    ValidationWarning,
)

logger = logging.getLogger(__name__)

USER_AGENT = "ScottyLabs-Governance-Validator"

HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_FORBIDDEN = 403


class GitHubUserCheckError(Exception):
    """Base exception for GitHub user validation failures."""


class GitHubRateLimitedOrForbiddenError(GitHubUserCheckError):
    """GitHub request was rate-limited or forbidden."""

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return "Rate limit exceeded or access forbidden"


@dataclass(frozen=True, slots=True)
class GitHubUnexpectedStatusError(GitHubUserCheckError):
    """GitHub responded with an unexpected status code."""

    status_code: int

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return f"Unexpected status {self.status_code}"


@dataclass(frozen=True, slots=True)
class GitHubRequestError(GitHubUserCheckError):
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
class SlackInvalidMemberIdError(SlackCheckError):
    """Slack member ID does not match expected format."""

    member_id: str

    def __str__(self) -> str:
        """Return a human-readable error message."""
        return f"Invalid Slack member ID format: {self.member_id}"


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


def validate_contributor_file_names(
    contributors: dict[EntityKey, Contributor],
) -> list[ValidationError]:
    """Validate that contributor file names match GitHub username."""
    logger.info("Validating contributor file names...")
    errors: list[ValidationError] = []
    for key, contributor in contributors.items():
        if key.name != contributor.github_username:
            errors.append(
                ValidationError(
                    file=f"contributors/{key.name}.toml",
                    message=(
                        f"Contributor file name '{key.name}' doesn't match "
                        f"GitHub username '{contributor.github_username}'"
                    ),
                ),
            )
    return errors


async def _check_github_user_exists(
    github_username: str,
    client: httpx.AsyncClient,
) -> bool | None:
    """Return True if user exists, False if not found, None on request error."""
    token = os.environ.get("SYNC_GITHUB_TOKEN", "")
    try:
        headers = {"User-Agent": USER_AGENT}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = await client.get(
            f"https://api.github.com/users/{github_username}",
            headers=headers,
        )
        if r.status_code == HTTP_OK:
            return True
        if r.status_code == HTTP_NOT_FOUND:
            return False
        if r.status_code == HTTP_FORBIDDEN:
            raise GitHubRateLimitedOrForbiddenError
        raise GitHubUnexpectedStatusError(r.status_code)
    except httpx.HTTPError as e:
        raise GitHubRequestError(e) from e


async def validate_github_users(
    contributors: dict[EntityKey, Contributor],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate that all contributor GitHub usernames exist."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    items = list(contributors.items())

    async def check_one(
        key: EntityKey,
        github: str,
    ) -> tuple[str | None, EntityKey | None, str | None]:
        try:
            exists = await _check_github_user_exists(github, client)
        except GitHubUserCheckError as e:
            return ("warning", key, f"Failed to check GitHub user {github}: {e}")
        else:
            if exists is False:
                return ("error", key, f"GitHub user does not exist: {github}")
            if exists is None:
                return ("warning", key, f"Failed to check GitHub user {github}")
            return (None, None, None)

    tasks = [check_one(key, c.github_username) for key, c in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        key = items[i][0]
        file_path = f"contributors/{key.name}.toml"
        if isinstance(res, BaseException):
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check GitHub user: {res}",
                ),
            )
            continue
        kind, _, msg = res
        if kind == "error" and msg:
            errors.append(ValidationError(file=file_path, message=msg))
        elif kind == "warning" and msg:
            warnings.append(ValidationWarning(file=file_path, message=msg))
    return (errors, warnings)


async def _check_slack_id_exists(
    slack_id: str,
    client: httpx.AsyncClient,
) -> bool | None:
    """Return True if exists, False if not found, raise on auth/rate limit."""
    token = os.environ.get("SLACK_TOKEN", "")
    if not token:
        raise SlackTokenMissingError
    if not slack_id.startswith("U"):
        raise SlackInvalidMemberIdError(slack_id)

    r = await client.get(
        "https://slack.com/api/users.info",
        params={"user": slack_id},
        headers={"User-Agent": USER_AGENT, "Authorization": f"Bearer {token}"},
    )
    data = r.json()
    ok = data.get("ok")
    if ok is True:
        return True
    if ok is False:
        err = data.get("error", "")
        if err == "user_not_found":
            return False
        if err == "ratelimited":
            raise SlackRateLimitedError
        if err == "invalid_auth":
            raise SlackInvalidAuthError
        raise SlackApiError(err)
    raise SlackUnexpectedResponseError


async def validate_slack_member_ids(
    contributors: dict[EntityKey, Contributor],
    client: httpx.AsyncClient,
) -> tuple[list[ValidationError], list[ValidationWarning]]:
    """Validate Slack member IDs for contributors."""
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    items = [
        (key, c.slack_member_id)
        for key, c in contributors.items()
        if c.slack_member_id
    ]

    async def check_one(
        key: EntityKey,
        slack_id: str,
    ) -> tuple[EntityKey, str, bool | None, str | None]:
        try:
            exists = await _check_slack_id_exists(slack_id, client)
        except SlackCheckError as e:
            return (key, slack_id, None, str(e))
        else:
            return (key, slack_id, exists, None)

    tasks = [check_one(key, sid) for key, sid in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        key, slack_id = items[i]
        file_path = f"contributors/{key.name}.toml"
        if isinstance(res, BaseException):
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check Slack ID {slack_id}: {res}",
                ),
            )
            continue
        _, sid, exists, err_msg = res
        if err_msg:
            warnings.append(
                ValidationWarning(
                    file=file_path,
                    message=f"Failed to check Slack ID {sid}: {err_msg}",
                ),
            )
            continue
        if exists is False:
            errors.append(
                ValidationError(
                    file=file_path,
                    message=f"Slack member ID does not exist: {sid}",
                ),
            )
    return (errors, warnings)
