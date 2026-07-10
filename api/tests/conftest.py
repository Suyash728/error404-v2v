import pytest

from core.crypto import _fernet


@pytest.fixture(autouse=True)
def _reset_fernet_cache():
    # core.crypto._fernet() is @lru_cache'd for the process lifetime, which
    # is right for the running app (the key never changes mid-process) but
    # wrong across tests that monkeypatch GCAL_TOKEN_ENCRYPTION_KEY to
    # different values — without this, whichever test runs first would
    # "win" the cache for every test after it.
    _fernet.cache_clear()
    yield
    _fernet.cache_clear()
