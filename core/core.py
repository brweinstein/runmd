import re
from .runner import run_code
from .languages import load_languages

def clear_outputs(md_text: str) -> str:
    pattern = r"(```\w+\n[\s\S]*?```)(?:\n)?\*\*Output:?\*\*\n```[\s\S]*?```(?:\n)?"
    cleaned = re.sub(pattern, r"\1", md_text, flags=re.DOTALL)

    def _trim_code_trailing(match: re.Match) -> str:
        lang = match.group(1)
        code = match.group(2)
        new_code = code.rstrip('\n')
        return f"```{lang}\n{new_code}\n```"

    cleaned = re.sub(r"```(\w+)\n([\s\S]*?)```", _trim_code_trailing, cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'```(?=```)', '```\n\n', cleaned)
    cleaned = re.sub(r'```\n(?=```)', '```\n\n', cleaned)

    return cleaned

def process_markdown(md_text: str) -> str:
    command_map = load_languages()
    md_text = clear_outputs(md_text)

    def repl(match: re.Match) -> str:
        lang = match.group(1)
        code = match.group(2)

        if lang.lower() == "racket":
            lines = code.splitlines()
            if not lines or not lines[0].startswith("#lang"):
                lines.insert(0, "#lang racket")
            code_to_run = "\n".join(lines)
        else:
            code_to_run = code

        output = run_code(lang, code_to_run, command_map).strip()

        if code.endswith("\n"):
            code_fence = f"```{lang}\n{code}```"
        else:
            code_fence = f"```{lang}\n{code}\n```"

        output_text = output.rstrip("\n") if output is not None else ""

        output_block = f"**Output**\n```\n{output_text}\n```"

        return code_fence + "\n" + output_block

    fence_pattern = r"```(\w+)\n([\s\S]*?)```(?!\n\*\*Output:?\*\*)"
    return re.sub(fence_pattern, repl, md_text, flags=re.DOTALL)
