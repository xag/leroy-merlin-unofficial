"""The STANDERS profiles against the sitemap entries they were read from, and against furniture-design's rules.

The entries are kept in the private repo xag/furniture, checked out beside this one (or at $FURNITURE_REPO):
sources/aluminium-profiles/ and sources/sliding-doors/owner-profiles/, sitemap-entries.json. Without them these
tests fail, saying where they looked, and never skip.
"""

import json
import os
import re
from pathlib import Path

from quern import Quern, run_rules

from furniture_design.knowledge import knowledge as general, merge
from furniture_design.package import PACKAGE
from leroy_merlin_unofficial import knowledge
from leroy_merlin_unofficial.profiles import material_id, products, read
from wood_panels import knowledge as wood_panels

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources"
FILES = ["aluminium-profiles/sitemap-entries.json", "sliding-doors/owner-profiles/sitemap-entries.json"]


def _standers() -> dict[str, dict]:
    out = {}
    for f in FILES:
        path = CAPTURES / f
        assert path.exists(), f"the private copy {path} is missing: clone xag/furniture beside this repo or set FURNITURE_REPO"
        for e in json.loads(path.read_text(encoding="utf-8"))["entries"]:
            if "STANDERS" in (e.get("title") or ""):
                out.setdefault(e["url"], e)
    return out


def test_every_profile_is_its_sitemap_entry_and_its_sizes_are_its_title():
    entries = _standers()
    for p in products():
        e = entries[p["url"]]
        assert e["title"] == p["title"], p["id"]
        assert p["url"].endswith(f"-{p['id']}.html")
        stated = read(e["title"])
        assert stated and all(stated[k] == p[k] for k in ("shape", "material", "finish", "h", "w", "t", "length_mm")), p["id"]


def test_every_standers_entry_that_states_its_four_sizes_is_a_product_and_no_other():
    entries = _standers()
    readable = {u for u, e in entries.items() if read(e["title"])}
    assert readable == {p["url"] for p in products()}
    left = [e["title"] for u, e in entries.items() if u not in readable]
    assert len(left) == len(entries) - len(products()) and len(left) < len(entries) / 3
    assert any("STANDERS, H.15 x l.15 mm, L.2.5 m" in t for t in left)  # a title naming no wall is left out


def test_the_owners_profiles_are_in_the_range():
    by = {p["id"]: p for p in products()}
    clear = by["87477510"]  # the label on the owner's clear U
    assert (clear["shape"], clear["material"], clear["finish"], clear["h"], clear["w"], clear["t"]) == \
        ("u", "pvc", "transparent", 12, 12, 1)
    angle = by["87477763"]  # STANDERS 20 x 20 x 1, white aluminium, on the owner's angle
    assert (angle["material"], angle["finish"], angle["h"], angle["w"], angle["t"]) == \
        ("aluminium", "anodisé blanc satiné", 20, 20, 1)
    assert material_id(by["87477958"]) == "standers-u-aluminium-brut-12x12x1"


def test_a_profile_material_reads_its_section_and_names_what_is_sold():
    mats = {m.id: m for b in knowledge() if b.id == "materials" for m in b.children}
    m = mats["standers-u-pvc-transparent-12x12x1"]
    assert (m.params["section_height"].value, m.params["section_width"].value, m.params["wall_thickness"].value) == (12, 12, 1)
    assert [q["ref"] for q in m.payload["sold_at_leroy_merlin"]["products"]] == ["87477510"]
    alu = mats["standers-u-aluminium-brut-12x12x1"]
    assert [q["length_mm"] for q in alu.payload["sold_at_leroy_merlin"]["products"]] == [1000, 2500]


def test_the_profiles_break_none_of_furniture_designs_rules():
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(general(), wood_panels(), knowledge())
    ours = {f"materials/{material_id(p)}" for p in products()} | {"sources/leroy-merlin-sitemap-profiles"}
    broken = [r for r in run_rules(tree, "") if not r.ok and any(r.node == p or r.node.startswith(p + "/") for p in ours)]
    assert not broken, broken[:3]
