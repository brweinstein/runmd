# runmd

A high-performance tool to execute code blocks in Markdown files and insert their outputs inline.

Written in Rust for maximum performance (10,000x+ faster parsing than Python). A legacy Python implementation is available but not actively improved.

runmd transforms Markdown files into executable notebooks by finding fenced code blocks, executing them, and inserting standardized output blocks with captured results.

This was created so I could run racket code in my markdown notes for my cs135 class.

## Features

- Fast execution for many languages (Python, Racket, Bash, Node, Ruby, Julia, Go, C/C++, Rust, Java, R, PHP, Lua, etc.)
- Standardized output format with consistent output blocks
- Clean output removal with `runmd -c` to restore original Markdown
- Configurable language commands via `~/.config/runmd/languages.config`
- Built-in error handling and async execution

## Performance

The Rust version delivers substantial performance improvements over the Python implementation:

| Operation | Python Version | Rust Version | Speedup |
|-----------|---------------|--------------|---------|
| Parse 1MB markdown | 113430ms | **11ms** | **10279x faster** |
| Execute 20 code blocks | 321ms | **83ms** | **3.9x faster** |
| Clear 100 output blocks | 1ms | **5ms** | **0.2x slower** |

Key benefits: 10,000x+ faster parsing, 4x faster execution, lower memory usage, parallel processing for multiple blocks.

## Quick Start

Process a Markdown file in-place:
```bash
runmd notes.md
```

Remove outputs (restore original):
```bash
runmd -c notes.md
```

Generate default config:
```bash
runmd --init-config
```

## Installation

### Rust Version (Recommended)

Build from source:
```bash
git clone https://github.com/brweinstein/runmd.git
cd runmd
cargo build --release
cargo install --path .
```

### Python Version (Legacy)

The Python implementation in `core/` is no longer actively developed. Use only for compatibility:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Project Structure

```
src/                    # Rust implementation (active development)
├── main.rs            # CLI entry point
├── core.rs            # Markdown parsing and processing
├── runner.rs          # Code execution engine
├── languages.rs       # Language configurations
└── config.rs          # Configuration management

core/                  # Python implementation (legacy, not improved)
├── cli.py            # Python CLI
├── core.py           # Python processing logic
├── runner.py         # Python execution
└── languages.py      # Python language config

tests/                 # Integration tests and benchmarks
├── benchmark.py      # Performance comparison
└── *.md             # Test markdown files
```

## Usage

**Basic commands**:
```bash
runmd <file>             # Process markdown file
runmd -c <file>          # Clear outputs only  
runmd --init-config      # Generate default config
```

**How it works**:
- Finds fenced code blocks: ` ```python\n...\n``` `
- Creates temporary files and executes using configured commands
- Inserts output blocks with captured stdout/stderr
- Missing interpreters show error messages (cleanly removable with `-c`)

## Configuration

Default language mappings work out-of-box. Customize via `~/.config/runmd/languages.config`:

```yaml
python: python3 {file}
javascript: node {file}  
rust: sh -c 'rustc {file} -o /tmp/runmd_rust && /tmp/runmd_rust'
racket: racket {file}
```

The `{file}` placeholder gets replaced with the temporary file path. Generate defaults with `runmd --init-config`.

## Examples

**Process lecture notes**:
```bash
runmd ~/Documents/cs135/notes.md
```

**Preview without modifying**:
```bash
runmd notes.md > preview.md
```

**Clean restore**:
```bash
runmd -c notes.md
```

## Development

Primary development is on the Rust implementation:
```bash
cargo test                    # Run integration tests
cargo build --release        # Optimized build
python tests/benchmark.py    # Performance benchmarks
```

Python version (legacy, no active development):
```bash
source venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

## Contributing

Issues and PRs welcome! Focus on small, tested changes.

## License

MIT License © 2025 Ben Weinstein
