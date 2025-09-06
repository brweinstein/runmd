from core.core import process_markdown, clear_outputs


def test_format_and_clear():
    md = """# Sample

```python
print(1+1)
```
"""
    processed = process_markdown(md)
    assert "**Output**" in processed
    assert "2" in processed

    cleared = clear_outputs(processed)
    assert cleared.strip() == md.strip()
