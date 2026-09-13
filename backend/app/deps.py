from .store import InMemoryStore

_store = InMemoryStore()


def get_store() -> InMemoryStore:
    return _store
