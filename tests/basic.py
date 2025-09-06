from core.core import process_markdown

def test_python_code_block():
    md = "```python\nprint(1+1)\n```"
    result = process_markdown(md)
    assert "2" in result
