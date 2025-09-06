# runmd

Run code blocks inside Markdown files and insert their outputs inline, like a lightweight notebook for plain .md files.

runmd finds fenced code blocks (```lang ... ```), executes them using a language-specific runner, and appends a consistent
"**Output**" fenced block containing the captured stdout (or stderr on failure). It supports a user-configurable command map,
can clear outputs, and includes a small CLI for common workflows.

## Features

- Execute fenced code blocks for many languages (Python, Racket, Bash, Node, Ruby, Julia, Go, C/C++, Rust, Java, R, PHP, Lua, ...)
- Insert standardized output blocks after each executed code fence:

  **Output**
  ```
  <captured output>
  ```
- Preserve code block contents when inserting output; `runmd -c` removes outputs and restores the original Markdown
 - User-configurable language command templates at `~/.config/runmd/languages.config`
- CLI helper to generate a default config (`runmd --init-config`)
- Reasonable error handling: runtime/compiler errors are captured and shown in the output fence so you can iterate quickly

## Quick start

Process a Markdown file in-place:

```bash
runmd notes.md
```

Remove outputs (restore the original file):

```bash
runmd -c notes.md
```

Create a default user config (writes `~/.config/runmd/languages.config`):

```bash
runmd --init-config
```

## Installation

From the repository (editable, recommended for development):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

If/when published to PyPI you can also install via pip:

```bash
pip install runmd
```

Make sure your virtualenv/bin is in PATH if you installed locally:

```bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

## Usage

Basic CLI usage:

```text
runmd <file>
runmd -c <file>          # clear outputs only
runmd --init-config      # write a default config file
```

Behavior notes:
- Code blocks are matched by a fenced pattern like ````` ```python\n...\n``` `````
- The tool writes temporary files for each block and runs the configured command for that language.
- If an interpreter/compiler isn't available the output block will contain an error message; `runmd -c` will still remove it.

## Configuring language runners

By default, `runmd` ships with a sensible set of language mappings. To override or add languages create a YAML file at
`~/.config/runmd/languages.config` with entries like:

```yaml
python: python3 {file}
javascript: node {file}
racket: racket {file}
```

The `{file}` placeholder will be replaced with the temporary file path. If `{file}` is omitted the tool will append the
temporary filename at the end of the command.

You can generate a default config with:

```bash
runmd --init-config
```

## Error handling

- Runtime/compiler errors are captured and placed into the output fence so you can see failures inline.
- `runmd -c` will remove error output blocks the same as normal outputs.

## Examples

Process a lecture note and view outputs inline:

```bash
runmd ~/Documents/cs135/notes/sep3.md
```

Process and write to a different file (manual redirection):

```bash
runmd notes.md > notes.with-output.md
```

Clear outputs only (restore original markdown):

```bash
runmd -c notes.with-output.md
```

## Development

- Install development deps and run tests:

```bash
source venv/bin/activate
pip install -r requirements-dev.txt  # or `pip install pytest pyyaml`
pytest -q
```

- Run the CLI locally during development:

```bash
python -m core.cli path/to/file.md
```

## Contributing

Contributions gratefully accepted. Open issues for bugs and feature requests. Small, focused PRs with tests are preferred.

## License

MIT License © 2025 Ben Weinstein
