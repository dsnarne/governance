"""Governance validator entry point."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

from meta.logger import get_app_logger
from meta.validator.contributors import ContributorValidator, load_contributors
from meta.validator.reporter import Reporter
from meta.validator.teams import load_teams
from meta.validator.teams.run import run_async as teams_run_async
from meta.validator.teams.run import run_sync as teams_run_sync


def run() -> None:
    """Run the validator and exit non-zero if invalid."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    contributors = load_contributors()
    teams = load_teams()
    reporter = Reporter(contributors, teams)

    ContributorValidator(contributors=contributors, reporter=reporter).validate()
    teams_run_sync(teams, contributors, reporter)

    async def run_team_checks() -> None:
        async with httpx.AsyncClient() as client:
            await teams_run_async(teams, client, reporter)

    asyncio.run(run_team_checks())

    report = reporter.emit()
    if not report.valid:
        raise SystemExit(1)


def main() -> None:
    """CLI entry point."""
    logger = get_app_logger()
    if not Path("contributors").exists():
        logger.critical("Please run this binary from the workspace root.")
        sys.exit(1)
    run()


if __name__ == "__main__":
    main()
