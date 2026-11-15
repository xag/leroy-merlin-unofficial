"""Write leroy_merlin_unofficial/profiles.json from the STANDERS entries of Leroy Merlin France's product sitemap,
kept in the private repo xag/furniture beside this one (or at $FURNITURE_REPO):

    uv run python tools/build_profiles.py

Every STANDERS entry whose title states its four sizes is a product; tests/test_profiles.py reads each again."""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from leroy_merlin_unofficial.profiles import read  # noqa: E402

CAPTURES = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources"
FILES = ["aluminium-profiles/sitemap-entries.json", "sliding-doors/owner-profiles/sitemap-entries.json"]


def entries() -> dict[str, dict]:
    """Every STANDERS entry, by address, from the kept sitemap entries."""
    out = {}
    for f in FILES:
        for e in json.loads((CAPTURES / f).read_text(encoding="utf-8"))["entries"]:
            if "STANDERS" in (e.get("title") or ""):
                out.setdefault(e["url"], {**e, "file": f})
    return out


def main() -> None:
    products = []
    for url, e in sorted(entries().items()):
        p = read(e["title"])
        if p:
            ref = re.search(r"-(\d+)\.html$", url)[1]
            products.append({"id": ref, "title": e["title"], "url": url, "entries": e["file"], **p})
    (ROOT / "leroy_merlin_unofficial" / "profiles.json").write_text(
        json.dumps({"products": products}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(products), "products of", len(entries()), "STANDERS entries")


if __name__ == "__main__":
    main()
