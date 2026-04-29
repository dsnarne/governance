"""Codeowners synchronizer."""

import sys
from http import HTTPStatus
from typing import TYPE_CHECKING, override

from dotenv import load_dotenv
from github import GithubException

from meta.clients.github_client import get_github_client
from meta.logger import log_operation, print_section
from meta.synchronizers.abstract import AbstractSynchronizer

if TYPE_CHECKING:
    from github.Repository import Repository

    from meta.models import Team


class CodeownersSynchronizer(AbstractSynchronizer):
    """Codeowners synchronizer."""

    REPO_NAME = "scottylabs-labrador/Governance"
    CODEOWNERS_FILE_PATH = ".github/CODEOWNERS"
    COMMIT_MESSAGE = "chore: auto-update CODEOWNERS"
    FILE_PATH = "meta/synchronizers/codeowners.py"

    def __init__(
        self,
    ) -> None:
        """Initialize the codeowners synchronizer."""
        super().__init__()
        self.g = get_github_client()

    @override
    def sync(self) -> None:
        print_section("Synchronizing CODEOWNERS file")

        # Generate the new codeowners file
        new_codeowners_file = self.generate_codeowners_file()

        # Get the current codeowners file
        repo = self.g.get_repo(self.REPO_NAME)
        current_codeowners_file, sha = self.get_current_codeowners_file(repo)
        if new_codeowners_file == current_codeowners_file:
            self.logger.debug("No changes to the codeowners file. Skipping...\n")
            return

        # Update or create the codeowners file
        if sha:
            with log_operation("update the codeowners file"):
                repo.update_file(
                    self.CODEOWNERS_FILE_PATH,
                    self.COMMIT_MESSAGE,
                    new_codeowners_file,
                    sha,
                )
        else:
            with log_operation("create the codeowners file"):
                repo.create_file(
                    self.CODEOWNERS_FILE_PATH,
                    self.COMMIT_MESSAGE,
                    new_codeowners_file,
                )

    def generate_codeowners_file(self) -> str:
        """Generate the CODEOWNERS file."""
        lines = [f"# Auto-generated CODEOWNERS file from {self.FILE_PATH}"]
        lines.append("")

        if "governance" not in self.teams:
            msg = "Governance team not found."
            self.logger.critical(msg)
            raise ValueError(msg)

        governance_team = self.teams["governance"]
        lines.append("# Default owners are the Governance team leads")
        lines.append(f"*{self._get_team_leads_pattern(governance_team)}")
        lines.append("")

        if "leadership" not in self.teams:
            msg = "Leadership team not found."
            self.logger.critical(msg)
            raise ValueError(msg)

        leadership_team = self.teams["leadership"]
        lines.append(
            "# Owners of the `teams/` directory are the leadership team leads",
        )
        lines.append(f"teams{self._get_team_leads_pattern(leadership_team)}")
        lines.append("")

        lines.append(
            "# The codeowners of each team file are their corresponding leads",
        )
        lines.append("")
        for team_slug, team in sorted(self.teams.items()):
            codeowners_pattern = f"teams/{team_slug}.toml"
            codeowners_pattern += self._get_team_leads_pattern(team)
            lines.append(codeowners_pattern)
            lines.append("")

        return "\n".join(lines)

    def _get_team_leads_pattern(self, team: Team) -> str:
        """Get the codeowners pattern for the team's leads."""
        codeowners_pattern = ""
        for lead in sorted(team.leads):
            codeowners_pattern += f" @{lead}"
        return codeowners_pattern

    def get_current_codeowners_file(
        self,
        repo: Repository,
    ) -> tuple[str | None, str | None]:
        """Get the current codeowners file from the repository.

        Returns:
            tuple[str | None, str | None]: The current codeowners file content
            and the sha of the file.

        Notes:
            Returns (None, None) if we want to create the CODEOWNERS file.

        """
        try:
            contents = repo.get_contents(".github/CODEOWNERS")
        except GithubException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return None, None

            self.logger.exception("Unexpected GitHub API error")
            sys.exit(1)

        # Error if the contents is a list (i.e. a directory)
        if isinstance(contents, list):
            return None, None

        # Return the sha and content of the codeowners file
        sha = contents.sha
        current_content = contents.decoded_content.decode("utf-8")
        return current_content, sha


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    codeowners_synchronizer = CodeownersSynchronizer()
    codeowners_synchronizer.sync()
