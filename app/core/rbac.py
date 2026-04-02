from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.VIEWER: {"dashboard:read"},
    Role.ANALYST: {"dashboard:read", "records:read"},
    Role.ADMIN: {
        "dashboard:read",
        "records:read",
        "records:create",
        "records:update",
        "records:delete",
        "users:read",
        "users:create",
        "users:update",
        "audits:read",
        "events:read",
        "events:publish",
    },
}


def has_permission(role: str, permission: str) -> bool:
    try:
        resolved_role = Role(role)
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(resolved_role, set())
