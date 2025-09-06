import os
from core.languages import load_languages, write_default_config


def test_load_default_has_python():
    langs = load_languages()
    assert "python" in langs


def test_write_default_config(tmp_path, monkeypatch):
    cfg = tmp_path / "runmd" / "languages.yml"
    write_default_config(str(cfg))
    assert cfg.exists()
    monkeypatch.setenv("HOME", str(tmp_path))
    langs = load_languages()
    assert "python" in langs
