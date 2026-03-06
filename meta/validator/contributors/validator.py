"""Contributor validation runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from meta.validator.contributors.checks import validate_andrew_ids
from meta.validator.key_ordering import load_schema_key_ordering, validate_key_orderings

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

    def validate_sync(self) -> None:
        """Run synchronous contributor checks."""
        ordering = load_schema_key_ordering(self.schema_path)
        self.reporter.insert_errors(
            validate_key_orderings(
                self.contributors,
                ordering,
                kind="contributor",
            ),
        )
        self.reporter.insert_errors(validate_andrew_ids(self.contributors))
