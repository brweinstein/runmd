import os
from core.core import process_markdown, clear_outputs

SAMPLE = """# Sample

```python
print(1+1)
```
"""


def test_process_python_block():
    res = process_markdown(SAMPLE)
    assert "**Output**" in res
    assert "2" in res


def test_clear_outputs_roundtrip(tmp_path):
    p = tmp_path / "t.md"
    p.write_text(SAMPLE)
    processed = process_markdown(p.read_text())
    cleared = clear_outputs(processed)
    # after clearing, we should get back the original sample (ignoring minor whitespace)
    assert p.read_text().strip() == cleared.strip()
