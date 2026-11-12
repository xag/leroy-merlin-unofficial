"""Every value against the copy it was read from, and the data against furniture-design's rules.

The copies are copyrighted and live in the private repo xag/furniture, checked out beside this
one (or at $FURNITURE_REPO): sources/leroy-merlin/sitemap-entries.json, the sitemap entries as
fetched, and sources/leroy-merlin/makers/, each maker document beside its text (pdftotext, or a
transcription of a scanned page that says it is one). Without them these tests fail, saying
where they looked, and never skip.
"""

import hashlib
import json
import os
import re
from functools import lru_cache
from pathlib import Path

from quern import Quern, run_rules

from furniture_design.knowledge import knowledge as general, merge
from furniture_design.package import PACKAGE
from leroy_merlin_unofficial import LINES, _documents, _range, knowledge

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources" / "leroy-merlin"


def _here(path: Path) -> Path:
    assert path.exists(), (f"the private copy {path} is missing: clone xag/furniture beside this repo or "
                           "set FURNITURE_REPO")
    return path


@lru_cache(maxsize=1)
def _entries() -> dict:
    return json.loads(_here(CAPTURES / "sitemap-entries.json").read_text(encoding="utf-8"))


def _numbers(printed: str) -> list[float]:
    """'13 300' is 13300, '18,0' is 18, '≥ 10,5' is 10.5, '450 ± 40' is 450 and 40."""
    return [float(n.replace(" ", "").replace(",", ".")) for n in re.findall(r"\d+(?: \d{3})*(?:[.,]\d+)?", printed)]


def test_every_maker_value_is_printed_in_the_document_fetched():
    for doc in _documents().values():
        pdf = _here(CAPTURES / "makers" / Path(doc["file"]).name)
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == doc["sha256"], doc["id"]
        text = re.sub(r"\s+", " ", _here(pdf.with_suffix(".txt")).read_text(encoding="utf-8"))
        if doc["capture"] == "transcribed":
            assert text.startswith("Transcribed by reading the scanned pages") and doc["sha256"] in text
        for clause in doc["clauses"]:
            for name, v in clause["params"].items():
                assert v["printed"] in text, (doc["id"], clause["id"], name, v["printed"])
                assert any(abs(n - v["value"]) < 1e-9 for n in _numbers(v["printed"])), (doc["id"], name)


def test_every_product_is_its_sitemap_entry_and_its_sizes_are_its_titles():
    entries = {e["url"]: e for e in _entries()["entries"]}
    for r in _range():
        e = entries[r["url"]]
        assert e["sitemap"] == r["sitemap"] and f"<loc>{r['url']}</loc>" in e["element"]
        said = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", e["title"].replace(",", "."))]
        for k in ("thickness_mm", "length_mm", "width_mm"):
            if r[k]:  # in mm or in cm, as the title gives it
                assert any(abs(n - r[k]) < 1e-9 or abs(10 * n - r[k]) < 1e-9 for n in said), (r["id"], k, e["title"])
    assert len(_entries()["sitemaps"]) and all(len(s) == 64 for s in _entries()["sitemaps"].values())


def test_every_line_the_range_names_is_described():
    assert {r["line"] for r in _range()} == {line for line, *_ in LINES}


def _tree() -> Quern:
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(general(), knowledge())
    return tree


def test_the_data_passes_furniture_designs_rules():
    assert [(r.rule, r.node, r.verdict) for r in run_rules(_tree()) if not r.ok] == []


def test_no_copyrighted_clause_carries_a_quote():
    sources = knowledge()[0].children
    assert all(s.payload["licence"] == "copyrighted" for s in sources)
    assert all("quote" not in c.payload for s in sources for c in s.children)


def test_a_line_whose_listing_names_no_maker_says_so_on_every_value():
    for m in knowledge()[1].children:
        lm = m.payload["leroy_merlin"]
        if not m.params:
            assert lm["values_from"] is None and lm["missing"]
            continue
        own = f"sources/{lm['values_from']}/"
        for name, q in m.params.items():
            if not lm["values_from"].startswith("materials/") and not q.derived_from[0].startswith(own):
                assert not q.grounded, (m.id, name)  # borrowed from another document: never grounded
            else:
                assert q.grounded == lm["maker_named"], (m.id, name)
        assert lm["maker_named"] or lm["unverified"], m.id
        assert lm["products"] and all(p.startswith("sources/leroy-merlin-sitemap/p-") for p in lm["products"])


def test_a_plywood_board_is_two_materials_one_per_way_it_bends():
    ms = {m.id: m for m in knowledge()[1].children}
    along, across = ms["lm-contreplaque-bouleau-18-along"], ms["lm-contreplaque-bouleau-18-across"]
    assert along.payload["measured_along"] == "face grain, flat"
    assert across.payload["measured_along"] == "across face grain, flat"
    assert across.payload["same_panel_as"] == along.id
    # Riga Wood's 18 mm, Table 3.17: EN 310 lower 5% strength 61.7 along, read as characteristic
    assert abs(along.params["design_bending_stress"].value - 61.7 / 2.1) < 1e-9
