from pydantic import BaseModel


class Team(BaseModel):
    """Team record loaded from `teams/*.toml`."""

    file_path: str
    name: str
    website: str | None = None
    server: str | None = None
    create_oidc_clients: bool = True
    repos: list[str]
    leads: list[str]
    members: list[str]
