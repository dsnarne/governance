"""Validation checks for contributors."""

from __future__ import annotations

import re

from meta.validator.model import Contributor, EntityKey, ValidationError

_ANDREW_ID_RE = re.compile(r"^[a-z0-9]+$")


def validate_andrew_ids(
    contributors: dict[EntityKey, Contributor],
) -> list[ValidationError]:
    """Validate optional `andrew-id` fields and enforce uniqueness."""
    errors: list[ValidationError] = []

    seen: dict[str, EntityKey] = {}
    for key, contributor in contributors.items():
        if contributor.andrew_id is None:
            continue
        if not _ANDREW_ID_RE.fullmatch(contributor.andrew_id):
            errors.append(
                ValidationError(
                    file=f"contributors/{key.name}.toml",
                    message=f"Invalid andrew-id: {contributor.andrew_id!r}",
                ),
            )
            continue
        prev = seen.get(contributor.andrew_id)
        if prev is not None:
            errors.append(
                ValidationError(
                    file=f"contributors/{key.name}.toml",
                    message=(
                        f"Duplicate andrew-id {contributor.andrew_id!r} "
                        f"(also in contributors/{prev.name}.toml)"
                    ),
                ),
            )
        else:
            seen[contributor.andrew_id] = key

    return errors
