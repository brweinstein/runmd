import os
import shutil
from typing import Dict, Callable

try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except Exception:
    yaml = None
    YAML_AVAILABLE = False


DEFAULT_LANGUAGES: Dict[str, Callable[[str], list]] = {
    "python": lambda f: ["python3", f],
    "py": lambda f: ["python3", f],
    "racket": lambda f: ["racket", f],
    "bash": lambda f: ["bash", f],
    "sh": lambda f: ["sh", f],
    "javascript": lambda f: ["node", f],
    "ruby": lambda f: ["ruby", f],
    "php": lambda f: ["php", f],
    "julia": lambda f: ["julia", f],
    "lua": lambda f: ["lua", f],
    "r": lambda f: ["Rscript", f],
    "rust": lambda f: ["sh", "-c", f"rustc {f} -o /tmp/runmd_rust && /tmp/runmd_rust"],
    "go": lambda f: ["go", "run", f],
    "java": lambda f: ["sh", "-c", f"javac {f} && java {os.path.splitext(os.path.basename(f))[0]}"],
    "cpp": lambda f: ["sh", "-c", f"g++ {f} -o /tmp/runmd_cpp && /tmp/runmd_cpp"],
    "c": lambda f: ["sh", "-c", f"gcc {f} -o /tmp/runmd_c && /tmp/runmd_c"],
}


def check_dependency_exists(cmd):
    if isinstance(cmd, list):
        base_cmd = cmd[0]
    else:
        base_cmd = cmd.split()[0]
    return shutil.which(base_cmd) is not None


def write_default_config(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    serializable = {}
    for k, v in DEFAULT_LANGUAGES.items():
        try:
            cmd_list = v("{file}")
            cmd_str = " ".join(cmd_list)
        except Exception:
            cmd_str = str(v)
        serializable[k] = cmd_str

    with open(path, "w", encoding="utf-8") as f:
        if YAML_AVAILABLE:
            yaml.safe_dump(serializable, f)
        else:
            for k, v in serializable.items():
                f.write(f"{k}: {v}\n")


def load_languages():
    cfg_dir = os.path.expanduser("~/.config/runmd")
    config_path = os.path.join(cfg_dir, "languages.config")
    user_langs = None
    if os.path.exists(config_path) and YAML_AVAILABLE:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_langs = yaml.safe_load(f) or {}
        except Exception:
            user_langs = None

    user_map = {}
    if user_langs:
        for k, v in user_langs.items():
            cmd_template = str(v)

            def make_cmd(template: str):
                return lambda fpath, t=template: (t.format(file=fpath)).split()

            user_map[k] = make_cmd(cmd_template)

    return {**DEFAULT_LANGUAGES, **user_map}
