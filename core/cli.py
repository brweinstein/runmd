import argparse
from pathlib import Path
from .core import process_markdown, clear_outputs
from .languages import write_default_config

def main():
    parser = argparse.ArgumentParser(description="Run code in Markdown files like a notebook")
    parser.add_argument("file", type=str, help="Markdown file to process")
    parser.add_argument("-c", "--clear", action="store_true", help="Clear outputs only")
    parser.add_argument("--init-config", action="store_true", help="Create ~/.config/runmd/languages.yml with sensible defaults")
    args = parser.parse_args()

    if args.init_config:
        cfg_path = Path.home() / ".config" / "runmd" / "languages.config"
        write_default_config(str(cfg_path))
        print(f"Wrote default config to {cfg_path}")
        return

    md_path = Path(args.file)
    if not md_path.exists():
        print(f"File not found: {md_path}")
        return

    md_text = md_path.read_text()

    if args.clear:
        new_text = clear_outputs(md_text)
        md_path.write_text(new_text)
        print(f"Cleared outputs in {md_path}")
        return

    new_text = process_markdown(md_text)
    md_path.write_text(new_text)
    print(f"Processed {md_path}")
