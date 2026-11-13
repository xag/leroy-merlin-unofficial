"""The range against the sitemap it was read from, and the data against furniture-design's rules.

The sitemap entries are kept in the private repo xag/furniture, checked out beside this one (or at
$FURNITURE_REPO): sources/leroy-merlin/sitemap-entries.json, as fetched. Without it these tests
fail, saying where they looked, and never skip. The values of the boards are wood-panels-
unofficial's, and its tests check them against their documents.
"""

import json
import os
import re
from functools import lru_cache
from pathlib import Path

from quern import Quern, run_rules

from furniture_design.knowledge import knowledge as general, merge
from furniture_design.package import PACKAGE
from leroy_merlin_unofficial import LINES, _range, knowledge
from wood_panels_unofficial import knowledge as wood_panels

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources" / "leroy-merlin"


def _here(path: Path) -> Path:
    assert path.exists(), (f"the private copy {path} is missing: clone xag/furniture beside this repo or "
                           "set FURNITURE_REPO")
    return path


@lru_cache(maxsize=1)
def _entries() -> dict:
    return json.loads(_here(CAPTURES / "sitemap-entries.json").read_text(encoding="utf-8"))


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


def test_no_two_materials_share_an_id():
    ids = [m.id for m in knowledge()[1].children]
    assert len(ids) == len(set(ids))


def _tree() -> Quern:
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(general(), wood_panels(), knowledge())
    return tree


def test_the_data_passes_furniture_designs_rules():
    assert [(r.rule, r.node, r.verdict) for r in run_rules(_tree()) if not r.ok] == []


def test_a_line_whose_listing_names_neither_class_nor_maker_grounds_nothing():
    panels = {m.id: m for m in wood_panels()[1].children}
    for m in knowledge()[1].children:
        lm = m.payload["leroy_merlin"]
        if not m.params:
            assert lm["values_from"] is None and lm["missing"]
            continue
        assert lm["products"] and all(p.startswith("sources/leroy-merlin-sitemap/p-") for p in lm["products"])
        if lm["values_from"].startswith("materials/") and lm["values_from"][10:] in panels:
            board = panels[lm["values_from"][10:]]
            assert {k: q.value for k, q in m.params.items()} == {k: q.value for k, q in board.params.items()}, m.id
            if lm["named"]:
                assert all(q.grounded == board.params[k].grounded for k, q in m.params.items()), m.id
        if not lm["named"]:
            assert lm["unverified"] and not any(q.grounded for q in m.params.values()), m.id


def test_an_unbranded_board_takes_its_classs_figures_and_osb_3_names_its_class():
    ms = {m.id: m for m in knowledge()[1].children}
    agglo = ms["lm-agglomere-18"]
    assert agglo.payload["leroy_merlin"]["values_from"] == "materials/particleboard-p2-13-20"
    assert agglo.params["modulus_of_rupture"].value == 11.0 and agglo.params["modulus_of_elasticity"].value == 1600.0
    assert "class" in agglo.payload["leroy_merlin"]["unverified"]
    osb = ms["lm-osb-3-18-major"]
    assert osb.payload["leroy_merlin"]["values_from"] == "materials/osb-3-10-18-major"
    assert osb.params["design_bending_stress"].grounded and ms["lm-osb-3-18-minor"].payload["same_panel_as"] == osb.id


def test_a_plywood_board_is_two_materials_one_per_way_it_bends():
    ms = {m.id: m for m in knowledge()[1].children}
    along, across = ms["lm-contreplaque-bouleau-18-along"], ms["lm-contreplaque-bouleau-18-across"]
    assert along.payload["measured_along"] == "face grain, flat"
    assert across.payload["measured_along"] == "across face grain, flat"
    assert across.payload["same_panel_as"] == along.id and "same_panel_as" not in along.payload
    # Riga Wood's 18 mm, Table 3.17: EN 310 lower 5% strength 61.7 along, read as characteristic
    assert abs(along.params["design_bending_stress"].value - 61.7 / 2.1) < 1e-9
    # Leroy Merlin's 6 mm birch is the tables' 6.5 mm
    assert ms["lm-contreplaque-bouleau-6-along"].payload["leroy_merlin"]["values_from"] == \
        "materials/riga-wood-birch-plywood-6.5-along"
