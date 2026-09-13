class NotFoundError(Exception):
    """The requested resource does not exist."""


class ConflictError(Exception):
    """The request clashes with the current state of the league."""
