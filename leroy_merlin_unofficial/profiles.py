"""The profiles of Leroy Merlin's own range, STANDERS, as data on furniture-design's kinds (source, clause,
material), read from the titles of its public product sitemap, as the panels are.

A STANDERS title reads "<Shape> <material> <finish> STANDERS, H.<h> x l.<w> x Ep.<t> mm, L.<length> m": the
height of a flange (H), the width across (l), the wall (Ep) and the length sold (L). Only a title that states
all four is read; one cut short or naming no wall is left out, and the test counts those. Each title is a clause
under sources/leroy-merlin-sitemap-profiles, its sizes as printed.

A material is one section in one material and finish, `standers-<shape>-<material>-<finish>-<h>x<w>x<t>` (not
`lm-`, which names a panel whose sheets the cutting sheet lays parts on),
its params the section's sizes (section_height, section_width, wall_thickness), its payload the products sold of
it (their lengths and addresses). It states no density or strength: what a profile weighs or carries is not in
its title, so the checks that read them judge no part of it.

The titles are kept in the private repo xag/furniture (sources/aluminium-profiles and
sources/sliding-doors/owner-profiles, sitemap-entries.json) and tools/build_profiles.py reads profiles.json from
them; tests/test_profiles.py reads every product again from those entries.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from quern.provenance import Quantity
from quern.tree import Node

HERE = Path(__file__).parent
SOURCE = "leroy-merlin-sitemap-profiles"

TITLE = re.compile(r"^(?P<head>.+?) STANDERS, H\.(?P<h>[\d.]+) x l\.(?P<w>[\d.]+) x Ep\.(?P<t>[\d.]+) mm, "
                   r"L\.(?P<length>[\d.]+) (?P<unit>m|cm)$")
SHAPES = [("profilé uu", "uu"), ("profilé u", "u"), ("profilé h", "h"), ("profilé t", "t"),
          ("cornière lisse", "angle-smooth"), ("cornière incurvée", "angle-curved"), ("cornière", "angle"),
          ("profilé", "profile")]
MATERIALS = [("aluminium", "aluminium"), ("alu", "aluminium"), ("pvc", "pvc")]


def read(title: str) -> dict | None:
    """What a STANDERS title says of a profile, or None when it does not state its four sizes."""
    m = TITLE.match(title.strip())
    if not m:
        return None
    head = m["head"].lower()
    shape = next((s for words, s in SHAPES if head.startswith(words)), None)
    rest = head[len(next(w for w, s in SHAPES if s == shape)):].strip() if shape else ""
    material = next((mat for words, mat in MATERIALS if rest.startswith(words)), None)
    if shape is None or material is None:
        return None
    finish = rest[len(next(w for w, mat in MATERIALS if rest.startswith(w))):].strip()
    length = float(m["length"]) * (1000 if m["unit"] == "m" else 10)
    return {"shape": shape, "material": material, "finish": finish, "h": float(m["h"]), "w": float(m["w"]),
            "t": float(m["t"]), "length_mm": length}


@lru_cache(maxsize=1)
def products() -> list[dict]:
    return json.loads((HERE / "profiles.json").read_text(encoding="utf-8"))["products"]


def _mm(x: float) -> str:
    return f"{x:g}".replace(".", "-")


def _slug(words: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", words.translate(str.maketrans("éèêàâîôûç", "eeeaaiouc"))).strip("-")


def material_id(p: dict) -> str:
    return (f"standers-{p['shape']}-{p['material']}-{_slug(p['finish']) or 'plain'}-"
            f"{_mm(p['h'])}x{_mm(p['w'])}x{_mm(p['t'])}")


def source() -> Node:
    """One clause per product read: its title as printed, and its sizes."""
    def mm(v: float, what: str, p: dict) -> Quantity:
        return Quantity(value=v, unit="mm", provenance="published", grounded=True, source=p["url"],
                        note=f"{what}, as the title prints it: {p['title']}")
    return Node(id=SOURCE, kind="source", name="Leroy Merlin France: product sitemap, STANDERS profiles",
                payload={"publisher": "Leroy Merlin France", "url": "https://www.leroymerlin.fr/sitemap-index.xml",
                         "fetched": "2026-11-15", "licence": "copyrighted", "authority": "maker",
                         "capture": "the sitemap entries kept privately, their files identified by sha256"},
                children=[Node(id=f"p-{p['id']}", kind="clause",
                               payload={"locator": p["url"], "rows": {"title": p["title"]}},
                               params={"section_height": mm(p["h"], "H", p), "section_width": mm(p["w"], "l", p),
                                       "wall_thickness": mm(p["t"], "Ep", p), "length": mm(p["length_mm"], "L", p)})
                          for p in products()])


SHAPE_WORDS = {"u": "U profile", "uu": "double U profile", "h": "H profile", "t": "T profile", "angle": "angle",
               "angle-smooth": "smooth angle", "angle-curved": "curved angle", "profile": "profile"}


def materials() -> list[Node]:
    """One material per section, material and finish, with the products sold of it."""
    by: dict[str, list[dict]] = {}
    for p in products():
        by.setdefault(material_id(p), []).append(p)
    out = []
    for mid, ps in sorted(by.items()):
        p = ps[0]
        clause = f"sources/{SOURCE}/p-{p['id']}"
        def derived(name: str, v: float) -> Quantity:
            return Quantity(value=v, unit="mm", provenance="derived", grounded=True, derived_from=[f"{clause}/{name}"],
                            note=f"as the title prints it: {p['title']}")
        out.append(Node(
            id=mid, kind="material",
            name=f"STANDERS {p['material']} {SHAPE_WORDS[p['shape']]} {p['finish']}, {p['h']:g} x {p['w']:g} x "
                 f"{p['t']:g} mm (Leroy Merlin)".replace("  ", " "),
            params={"section_height": derived("section_height", p["h"]),
                    "section_width": derived("section_width", p["w"]),
                    "wall_thickness": derived("wall_thickness", p["t"])},
            payload={"form": f"{p['material']} {SHAPE_WORDS[p['shape']]}", "finish": p["finish"],
                     "label": f"Profilé STANDERS {p['h']:g}x{p['w']:g}x{p['t']:g}",
                     "measured_along": "unstated",
                     "sold_at_leroy_merlin": {"products": [{"ref": q["id"], "length_mm": q["length_mm"], "url": q["url"],
                                                    "title": q["title"]} for q in sorted(ps, key=lambda q: q["length_mm"])]}},
            links={"per": sorted(f"sources/{SOURCE}/p-{q['id']}" for q in ps)}))
    return out
