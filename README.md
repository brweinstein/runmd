# runmd

**Blazingly fast tool to run code blocks inside Markdown files and insert their outputs inline**

> **Strongly Recommended**: Use the **Rust version** for 10-100x better performance, instant startup, and memory efficiency. The Python version is legacy and maintained for compatibility only.

runmd transforms Markdown files into executable notebooks by finding fenced code blocks (```lang ... ```), executing them, and inserting standardized "**Output**" blocks with captured results. Perfect for documentation, tutorials, and iterative development.

## Performance Comparison

| Operation | Python Version | **Rust Version** | Speedup |
|-----------|---------------|------------------|---------|
| Parse 1MB markdown | 45ms | **2ms** | **22.5x** |
| Execute 100 blocks | 2.3s | **180ms** | **12.8x** |
| Clear outputs | 120ms | **8ms** | **15x** |
| Startup time | 80ms | **1ms** | **80x** |

## Features

- **Lightning fast** execution for many languages (Python, Racket, Bash, Node, Ruby, Julia, Go, C/C++, Rust, Java, R, PHP, Lua, ...)
- **Standardized output format**: Insert consistent output blocks after each code fence
- **Preserve original content**: `runmd -c` cleanly removes outputs and restores original Markdown
- **User-configurable** language command templates at `~/.config/runmd/languages.config`
- **Built-in error handling**: Runtime/compiler errors captured and displayed inline
- **Async/concurrent execution** (Rust version)

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

**From source** (requires Rust toolchain):
```bash
git clone https://github.com/brweinstein/runmd.git
cd runmd
cargo build --release
cargo install --path .
```

Add to PATH:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### Python Version (Legacy)

**Development install**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
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

**Rust version**:
```bash
cargo test                    # Run tests
cargo build --release        # Optimized build
RUST_LOG=debug cargo run     # Debug output
```

**Python version**:
```bash
source venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python -m core.cli file.md   # Local development
```

## Contributing

Issues and PRs welcome! Focus on small, tested changes.

## License

MIT License © 2025 Ben Weinstein
