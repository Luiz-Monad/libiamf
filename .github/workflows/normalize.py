#!/usr/bin/env python3
from util import run

def should_use_crlf(path):
    name = path.name
    if name == "CMakeLists.txt":
        return True
    crlf_extensions = [".sln", ".vcxproj", ".vcxproj.filters", ".props"]
    return any(str(path).endswith(ext) for ext in crlf_extensions)

def normalize_line_endings(data, use_crlf):
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data.replace(b"\n", b"\r\n") if use_crlf else data

def is_binary_file(path):
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        return b"\x00" in chunk
    except Exception:
        return True

def normalize_tree(workdir, remove):
    """Normalize files and remove unwanted paths in-place."""
    # Remove unwanted paths
    for rel in remove:
        target = workdir / rel
        if target.exists():
            print(f"Removing {target}")
            run(["rm", "-rf", str(target)])

    # Normalize text files
    for p in workdir.rglob("*"):
        # Skip non-files and files inside .git
        if not p.is_file() or ".git" in p.parts:
            continue

        # Skip binaries
        if is_binary_file(p):
            continue

        use_crlf = should_use_crlf(p)
        try:
            with open(p, "rb") as f:
                data = f.read()
            norm = normalize_line_endings(data, use_crlf)
            if data != norm:
                with open(p, "wb") as f:
                    f.write(norm)
        except Exception as e:
            print(f"Skipping {p}: {e}")
