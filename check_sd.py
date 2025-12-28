import os
from pathlib import Path

# -------- CONFIG -------- #

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "node_modules",
    ".langgraph_api",
}

EXCLUDE_FILES = {
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    "*.log",
}

MAX_DEPTH = 10  # increase if needed

# ------------------------ #


def should_exclude(path: Path) -> bool:
    if path.name in EXCLUDE_DIRS:
        return True
    for pattern in EXCLUDE_FILES:
        if path.match(pattern):
            return True
    return False


def print_tree(
    root: Path,
    prefix: str = "",
    depth: int = 0,
):
    if depth > MAX_DEPTH:
        return

    entries = sorted(
        [p for p in root.iterdir() if not should_exclude(p)],
        key=lambda p: (p.is_file(), p.name.lower()),
    )

    for i, path in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + path.name)

        if path.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(
                path,
                prefix + extension,
                depth + 1,
            )


if __name__ == "__main__":
    project_root = Path(__file__).parent
    print(project_root.name)
    print_tree(project_root)
