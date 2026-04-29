"""Mock Keycloak clients for validator tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class MockKeycloakClientValid:
    """Mock Keycloak client that maps every username to a synthetic user id."""

    def get_user_id_by_username(self, username: str) -> str:
        """Pretend the user exists in Keycloak."""
        return f"kc-user-{username}"


class MockKeycloakClientUserNotFound:
    """Mock Keycloak client that reports no matching user."""

    def get_user_id_by_username(self, _username: str) -> str | None:
        """Return no user to emulate an unknown Andrew ID."""
        return None


class MockKeycloakClientUnexpectedError:
    """Mock Keycloak client that always raises when resolving the user id."""

    def get_user_id_by_username(self, _username: str) -> str | None:
        """Raise a non-Keycloak-specific exception for the generic failure path."""
        msg = "unexpected keycloak client failure"
        raise RuntimeError(msg)


type MockKeycloakClient = (
    MockKeycloakClientValid
    | MockKeycloakClientUserNotFound
    | MockKeycloakClientUnexpectedError
)


def make_get_keycloak_client(
    client: MockKeycloakClient,
) -> Callable[[], MockKeycloakClient]:
    """Return a ``get_keycloak_client``-compatible callable for monkeypatching."""

    def mock_get_keycloak_client() -> MockKeycloakClient:
        """Return the provided mock client."""
        return client

    return mock_get_keycloak_client
