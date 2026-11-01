"""Upload Lumbre to a Hugging Face Space. The token is read from .env."""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"hf_[A-Za-z0-9]{25,}")
HEADER = """---
title: Lumbre
emoji: 🕯️
colorFrom: red
colorTo: yellow
sdk: streamlit
sdk_version: 1.66.1
app_file: app.py
pinned: false
license: mit
python_version: "3.11"
---

"""
IGNORE = (
    ".env",
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    "sub.md",
    "scripts",
    "tests",
)


def main() -> int:
    load_dotenv(ROOT / ".env")
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        print("Set HF_TOKEN in .env before publishing.")
        return 1
    leaked = _leaked_files()
    if leaked:
        print("Refusing to upload because a token-like string is in: " + ", ".join(leaked))
        return 1
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    try:
        owner = api.whoami()["name"]
        repo_id = f"{owner}/lumbre"
        api.create_repo(
            repo_id,
            repo_type="space",
            space_sdk="streamlit",
            exist_ok=True,
            private=False,
        )
        api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=str(ROOT),
            ignore_patterns=[
                ".env",
                ".env.*",
                ".venv/**",
                ".git/**",
                "**/__pycache__/**",
                ".pytest_cache/**",
                "tests/**",
                "scripts/**",
                "sub.md",
                "README.md",
            ],
            commit_message="Publish the altar page",
        )
        readme = HEADER + (ROOT / "README.md").read_text(encoding="utf-8")
        api.upload_file(
            path_or_fileobj=readme.encode("utf-8"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="space",
            commit_message="Add the Space page settings",
        )
    except Exception as exc:
        print(_redact(str(exc), token))
        return 1
    print(f"Published https://huggingface.co/spaces/{repo_id}")
    return 0


def _leaked_files() -> list[str]:
    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or _ignored(path):
            continue
        if path.suffix not in {".py", ".md", ".toml", ".txt"} and path.name != ".env.example":
            continue
        if TOKEN.search(path.read_text(encoding="utf-8")):
            found.append(str(path.relative_to(ROOT)))
    return found


def _ignored(path: Path) -> bool:
    return path.name == ".env" or any(part in IGNORE for part in path.parts)


def _redact(text: str, token: str) -> str:
    return text.replace(token, "[token]")


if __name__ == "__main__":
    sys.exit(main())
