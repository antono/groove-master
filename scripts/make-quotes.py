#!/usr/bin/env python3
"""Generate static/quotes/quotes.json from docs/groove_academy_quotes.csv.

The CSV (columns: citation, author, reference) is the editorial source; this
driver converts it to the shipped JSON the Quote of the Day component fetches.

Each quote gets a *stable* id — `<author-slug>-<8-hex citation hash>` — so it
survives quotes being added or reordered and only changes if the quote's own
text changes (which is effectively a different quote). Ids are asserted unique.

Re-run after editing the CSV:

    python3 scripts/make-quotes.py
"""

import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "docs", "groove_academy_quotes.csv")
OUT_DIR = os.path.join(ROOT, "static", "quotes")
OUT_PATH = os.path.join(OUT_DIR, "quotes.json")


def slug(author: str) -> str:
    """Kebab-case an author name for the readable half of the id."""
    s = author.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def quote_id(author: str, citation: str) -> str:
    """Stable id: independent of row order, tied only to the quote's text."""
    digest = hashlib.sha1(citation.strip().encode("utf-8")).hexdigest()[:8]
    return f"{slug(author)}-{digest}"


def main() -> int:
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    quotes = []
    seen_ids = set()
    for row in rows:
        citation = (row.get("citation") or "").strip()
        author = (row.get("author") or "").strip()
        testimonial = (row.get("reference") or "").strip()
        if not citation or not author:
            continue  # skip the trailing blank line / malformed rows
        qid = quote_id(author, citation)
        if qid in seen_ids:
            print(f"error: duplicate quote id {qid!r} for {author}", file=sys.stderr)
            return 1
        seen_ids.add(qid)
        quotes.append(
            {
                "id": qid,
                "citation": citation,
                "author": author,
                "testimonial": testimonial,
            }
        )

    if not quotes:
        print("error: no quotes parsed from CSV", file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"wrote {len(quotes)} quotes to {os.path.relpath(OUT_PATH, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
