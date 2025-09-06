import warnings
from sgpt.config import Config, DEFAULT_CONFIG, CACHE_PATH


def test_prefixed_env(monkeypatch, tmp_path):
    monkeypatch.setenv("BLUS_OPENAI_API_KEY", "test")
    monkeypatch.setenv("BLUS_CACHE_PATH", "/tmp/new_cache")
    cfg = Config(tmp_path / ".sgptrc", **DEFAULT_CONFIG)
    assert cfg.get("CACHE_PATH") == "/tmp/new_cache"


def test_legacy_env_warn(monkeypatch, tmp_path):
    monkeypatch.setenv("BLUS_OPENAI_API_KEY", "test")
    monkeypatch.setenv("CACHE_PATH", "/tmp/old_cache")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = Config(tmp_path / ".sgptrc", **DEFAULT_CONFIG)
        assert cfg.get("CACHE_PATH") == str(CACHE_PATH)
        assert any("CACHE_PATH" in str(warn.message) for warn in w)


def test_legacy_env_ignored_when_new_set(monkeypatch, tmp_path):
    monkeypatch.setenv("BLUS_OPENAI_API_KEY", "test")
    monkeypatch.setenv("CACHE_PATH", "/tmp/old_cache")
    monkeypatch.setenv("BLUS_CACHE_PATH", "/tmp/new_cache")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = Config(tmp_path / ".sgptrc", **DEFAULT_CONFIG)
        assert cfg.get("CACHE_PATH") == "/tmp/new_cache"
        assert any("CACHE_PATH" in str(warn.message) for warn in w)
