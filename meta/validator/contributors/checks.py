"""Validation checks for contributors."""

from __future__ import annotations

import re

from meta.validator.model import Contributor, ValidationError

_ANDREW_ID_RE = re.compile(r"^[a-z0-9]+$")


def validate_andrew_ids(
    contributors: dict[str, Contributor],
) -> list[ValidationError]:
    """Validate optional `andrew-id` fields and enforce uniqueness."""
    errors: list[ValidationError] = []

    seen: dict[str, str] = {}
    for file_path, contributor in contributors.items():
        if contributor.andrew_id is None:
            continue
        if not _ANDREW_ID_RE.fullmatch(contributor.andrew_id):
            errors.append(
                ValidationError(
                    file=file_path,
                    message=f"Invalid andrew-id: {contributor.andrew_id!r}",
                ),
            )
            continue
        prev = seen.get(contributor.andrew_id)
        if prev is not None:
            errors.append(
                ValidationError(
                    file=file_path,
                    message=(
                        f"Duplicate andrew-id {contributor.andrew_id!r} "
                        f"(also in {prev})"
                    ),
                ),
            )
        else:
            seen[contributor.andrew_id] = file_path

    return errors
