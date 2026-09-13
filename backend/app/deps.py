from collections.abc import Iterator

from .db import SessionLocal
from .store import SqlStore


def get_store() -> Iterator[SqlStore]:
    with SessionLocal() as session:
        yield SqlStore(session)
