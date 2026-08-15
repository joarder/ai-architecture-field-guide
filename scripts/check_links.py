#!/usr/bin/env python3
"""Check the raw-HTML links in docs/index.md that MkDocs' strict mode can't see.

MkDocs validates markdown links but ignores href attributes inside raw HTML
blocks — which is exactly what the landing-page stack diagram is made of. This
script closes that gap. Run it after any chapter rename, merge, or deletion.

Usage:  python3 scripts/check_links.py
Exit:   0 if all links resolve, 1 otherwise.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
INDEX = DOCS / "index.md"


def main() -> int:
    if not INDEX.exists():
        print(f"ERROR: {INDEX} not found")
        return 1

    html = INDEX.read_text(encoding="utf-8")
    hrefs = re.findall(r'href="([^"]+)"', html)

    problems = []
    checked = 0

    for href in hrefs:
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue

        checked += 1
        path_part, _, anchor = href.partition("#")
        path_part = path_part.rstrip("/")

        if not path_part:
            continue

        # A link like "02-orchestration/" maps to docs/02-orchestration.md,
        # and "tool/" maps to docs/tool/index.md.
        candidates = [
            DOCS / f"{path_part}.md",
            DOCS / path_part / "index.md",
        ]
        target = next((c for c in candidates if c.exists()), None)

        if target is None:
            problems.append(f"  BROKEN PATH  href=\"{href}\" -> no matching file")
            continue

        if anchor:
            body = target.read_text(encoding="utf-8")
            slugs = {
                re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")
                for h in re.findall(r"^#{1,6}\s+(.*)$", body, re.MULTILINE)
            }
            if anchor not in slugs:
                problems.append(
                    f"  BROKEN ANCHOR href=\"{href}\" -> #{anchor} not a heading in {target.name}"
                )

    if problems:
        print(f"Checked {checked} internal links in index.md — {len(problems)} problem(s):\n")
        print("\n".join(problems))
        return 1

    print(f"OK: all {checked} internal links in index.md resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
