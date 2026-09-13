import pytest

from app.main import DEFAULT_CORS_ORIGINS, allowed_origins


def test_defaults_cover_the_vite_dev_and_preview_ports():
    origins = allowed_origins()
    assert "http://localhost:5173" in origins
    assert "http://localhost:4173" in origins


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://league.example", ["https://league.example"]),
        (" https://a.example , https://b.example ", ["https://a.example", "https://b.example"]),
        ("https://a.example,,", ["https://a.example"]),
    ],
)
def test_environment_overrides_the_defaults(monkeypatch, raw, expected):
    monkeypatch.setenv("CORS_ORIGINS", raw)
    assert allowed_origins() == expected


def test_default_constant_is_a_comma_separated_list():
    assert allowed_origins() == [
        origin.strip() for origin in DEFAULT_CORS_ORIGINS.split(",")
    ]
