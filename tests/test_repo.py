import re
import unittest
from pathlib import Path

TOKEN = re.compile(r"hf_[A-Za-z0-9]{25,}")
ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".venv", ".git", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".txt", ".example"}


class RepoTests(unittest.TestCase):
    def test_tracked_sources_have_no_access_token(self) -> None:
        offenders = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.name == ".env" or SKIP_PARTS.intersection(path.parts):
                continue
            if path.suffix not in TEXT_SUFFIXES and path.name != ".env.example":
                continue
            if TOKEN.search(path.read_text(encoding="utf-8")):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
