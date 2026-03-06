"""Data models for governance validation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Contributor:
    """A contributor record loaded from `contributors/*.toml`."""

    full_name: str
    andrew_id: str | None = None
    key_order: list[str] = field(default_factory=list)

    def get_key_order(self) -> list[str]:
        """Return the TOML key ordering as loaded from disk."""
        return self.key_order

    def set_key_order(self, order: list[str]) -> None:
        """Set the TOML key ordering captured during parsing."""
        self.key_order = order


@dataclass(frozen=True, slots=True)
class TeamMember:
    """A contributor entry within a team's membership record."""

    github_username: str
    title: str | None = None


@dataclass(frozen=True, slots=True)
class TeamMembership:
    """Membership record for a given timeframe."""

    timeframe: str
    maintainers: list[str]
    contributors: list[TeamMember]


@dataclass
class Team:
    """A team record loaded from `teams/*.toml`."""

    slug: str
    name: str
    description: str
    website: str | None = None
    create_oidc_clients: bool = True
    repos: list[str] = field(default_factory=list)
    membership: list[TeamMembership] = field(default_factory=list)
    key_order: list[str] = field(default_factory=list)

    def get_key_order(self) -> list[str]:
        """Return the TOML key ordering as loaded from disk."""
        return self.key_order

    def set_key_order(self, order: list[str]) -> None:
        """Set the TOML key ordering captured during parsing."""
        self.key_order = order


@dataclass(frozen=True)
class EntityKey:
    """Key for looking up an entity (contributor or team) by kind and name."""

    kind: str  # "team" | "contributor"
    name: str  # file_stem

    def __hash__(self) -> int:
        """Hash by name for use as a dict key."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Compare by name when comparing keys."""
        if not isinstance(other, EntityKey):
            return NotImplemented
        return self.name == other.name

    def __str__(self) -> str:
        """Return the unscoped identifier (file stem)."""
        return self.name

    def scoped_id(self) -> str:
        """Return a stable scoped identifier of the form `<kind>:<name>`."""
        return f"{self.kind}:{self.name}"


@dataclass
class ValidationError:
    """A validation error associated with a file."""

    file: str
    message: str


@dataclass
class ValidationWarning:
    """A validation warning associated with a file."""

    file: str
    message: str


@dataclass
class FileValidationMessages:
    """Collected errors and warnings for a single file."""

    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)


@dataclass
class ValidationStatistics:
    """Aggregate statistics for a validation run."""

    contributors_count: int
    teams_count: int
    valid_files_count: int
    invalid_files_count: int
    total_errors: int
    total_warnings: int


@dataclass
class ValidationReport:
    """Full validation result including per-file messages."""

    valid: bool
    stats: ValidationStatistics
    files: dict[str, FileValidationMessages]
