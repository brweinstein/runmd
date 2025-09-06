import subprocess
import tempfile
import os
from .languages import check_dependency_exists


def run_code(lang, code, command_map, timeout: int = 10) -> str:
    if lang not in command_map:
        return f"[error] Language '{lang}' not supported."

    suffix = f".{lang}" if lang.isalnum() else ""
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=suffix)
    try:
        tmp.write(code)
        tmp.flush()
        tmp.close()

        cmd = command_map[lang](tmp.name)

        if not check_dependency_exists(cmd):
            return f"[error] Required interpreter/compiler for '{lang}' is not installed."

        proc = subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=timeout)

        out = proc.stdout or ""
        err = proc.stderr or ""
        if proc.returncode != 0 and not out:
            return err.strip()
        return out.strip()
    except subprocess.TimeoutExpired:
        return "[error] execution timed out"
    except Exception as e:
        return f"[error] {e}"
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
