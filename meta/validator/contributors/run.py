"""Run all contributor validation and record results into file_messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from meta.validator.contributors.checks import validate_andrew_ids
from meta.validator.key_ordering import load_schema_key_ordering, validate_key_orderings

if TYPE_CHECKING:
    from meta.validator.model import Contributor
    from meta.validator.reporter import Reporter

CONTRIBUTOR_SCHEMA_PATH = "__meta/schemas/contributor.schema.json"


def run_sync(
    contributors: dict[str, Contributor],
    reporter: Reporter,
) -> None:
    """Run synchronous contributor checks and record results in reporter."""
    ordering = load_schema_key_ordering(CONTRIBUTOR_SCHEMA_PATH)
    reporter.insert_errors(
        validate_key_orderings(
            contributors,
            ordering,
        ),
    )
    reporter.insert_errors(validate_andrew_ids(contributors))


