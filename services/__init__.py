"""Service layer: all business logic and SQL live here, never in the UI."""


class ServiceError(Exception):
    """Raised by services for expected, user-facing problems.

    The ``message`` is safe to show directly to the librarian.
    """
