#!/usr/bin/env python3
"""Build the Mawaqeet Lovelace prayer card bundle."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FRONTEND_DIR = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "mawaqeet"
    / "frontend"
)


def main() -> int:
    """Run npm install and vite build."""
    if not (FRONTEND_DIR / "package.json").is_file():
        print(f"Missing package.json in {FRONTEND_DIR}", file=sys.stderr)
        return 1

    lock = FRONTEND_DIR / "package-lock.json"
    install_cmd = ["npm", "ci"] if lock.is_file() else ["npm", "install"]
    subprocess.run(install_cmd, cwd=FRONTEND_DIR, check=True)
    subprocess.run(["npm", "run", "test"], cwd=FRONTEND_DIR, check=True)
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True)
    out = FRONTEND_DIR.parent / "www" / "mawaqeet-prayer-card.js"
    print(f"Built {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
