"""Governance validator entry point."""

from __future__ import annotations

from dotenv import load_dotenv

from meta.logger import print_section

from .members import MemberValidator, load_members
from .reporter import Reporter
from .teams import TeamValidator, load_teams


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    reporter = Reporter()

    print_section("Validating members")
    members = load_members(reporter)
    MemberValidator(members, reporter).validate()

    print_section("Validating teams")
    teams = load_teams(reporter)
    TeamValidator(teams, members, reporter).validate()

    reporter.emit()
