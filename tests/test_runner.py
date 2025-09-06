from core.runner import run_code
from core.languages import load_languages


def test_run_python_simple():
    langs = load_languages()
    out = run_code("python", "print(2+3)", langs)
    assert "5" in out


def test_run_unknown_language():
    langs = load_languages()
    out = run_code("nope", "1+1", langs)
    assert "not supported" in out.lower()
