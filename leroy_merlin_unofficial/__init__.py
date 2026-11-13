"""The wood panels Leroy Merlin France sells, as data on furniture-design's kinds (source,
clause, material), each line read as a board of wood-panels. Unofficial: Leroy Merlin
neither wrote nor endorsed it.

What the shop lists comes from its public product sitemap (range.json): every panel product, with
the thickness, the sheet size or cut-to-size and the address its title gives. Each is a clause
under sources/leroy-merlin-sitemap. The product pages are behind a captcha and are not read
(ledger: the-range-is-read-from-the-public-sitemap).

A material is one product line in one thickness, under materials/: `lm-<line>-<thickness>`, and
for plywood and OSB one per way it bends (`-along`/`-across`, `-major`/`-minor`). Its values are
those of a wood-panels material: a class's (particleboard P2 or P3, MDF, OSB/3) for a
board whose strength is its class's, or a maker's board's. Its payload `leroy_merlin` says what
the shop sells of it (the products, their sheet sizes, whether it is cut to size) and which
material its values are. When the listing does not name the class or the maker those values
belong to, every value is ungrounded until the label on the panel in the store says (ledger:
a-line-takes-its-classs-values-or-a-makers). A line nothing describes (contreplaqué ordinaire,
naturel, décor; OSB bouleau; hêtre thermo; eucalyptus) has a material with what is sold and no
values, so it judges nothing.

    from furniture_design.knowledge import knowledge as general, merge
    from wood_panels import knowledge as wood_panels
    from leroy_merlin_unofficial import knowledge as leroy_merlin
    tree.root.children = merge(general(), wood_panels(), leroy_merlin()) + [pieces]
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from furniture_design.knowledge import european_species
from quern.provenance import Quantity
from quern.tree import Node
from wood_panels import CLASSES, PRODUCTS
from wood_panels import materials as panel_materials

HERE = Path(__file__).parent
SITEMAP = "sources/leroy-merlin-sitemap"

# Every product line the sitemap's titles name: its words as Leroy Merlin's titles give them, the
# form of board, where its values come from (wood-panels classes or products, in the
# order they are tried, or a species material of furniture-design), whether the listing names the
# class or maker those values belong to, and the key a connector's strengths are stored under.
# (line, words, form, values from, named, connector_key)
LINES = [
    ("agglomere", "aggloméré naturel", "particleboard", ["particleboard-p2"], False, "particleboard"),
    ("agglomere-finsa", "aggloméré Finsa", "particleboard", ["finsa-fimapan-ez", "particleboard-p2"], True,
     "particleboard"),
    ("agglomere-hydrofuge", "aggloméré hydrofuge", "particleboard", ["particleboard-p3"], False, "particleboard"),
    ("agglomere-hydrofuge-finsa", "aggloméré hydrofuge Finsa", "particleboard",
     ["finsa-fimapan-h-ez", "particleboard-p3"], True, "particleboard"),
    ("agglomere-blanc", "aggloméré blanc (mélaminé)", "melamine-faced particleboard", ["particleboard-p2"], False,
     "particleboard"),
    ("agglomere-melamine", "tablette aggloméré mélaminé", "melamine-faced particleboard", ["particleboard-p2"],
     False, "particleboard"),
    ("mdf", "médium (MDF) naturel", "MDF", ["mdf", "finsa-fibrapan-ez"], False, "mdf"),
    ("mdf-teinte", "médium (MDF) blanc, gris, noir ou chêne", "MDF", ["mdf", "finsa-fibrapan-ez"], False, "mdf"),
    ("mdf-valchromat", "médium teinté dans la masse Valchromat", "MDF", ["valchromat"], True, "mdf"),
    ("panneau-fibres-dures", "panneau de fibres dures (isorel)", "hardboard", ["betanzos-htp-premium"], False,
     "hardboard"),
    ("osb-3", "OSB 3", "OSB/3", ["osb-3"], True, "osb"),
    ("osb-3-kronospan", "OSB 3 Kronospan", "OSB/3", ["kronospan-osb-3"], True, "osb"),
    ("osb-3-swiss-krono", "OSB 3 Swiss Krono", "OSB/3", ["swiss-krono-osb-3"], True, "osb"),
    ("osb-bouleau-swiss-krono", "OSB bouleau Swiss Krono", "OSB/3", [], False, "osb"),
    ("contreplaque-peuplier", "contreplaqué peuplier", "plywood", ["garnica-poplar-plywood", "toro-poplar-plywood"],
     False, "plywood"),
    ("contreplaque-peuplier-pircher", "contreplaqué peuplier Pircher", "plywood",
     ["garnica-poplar-plywood", "toro-poplar-plywood"], False, "plywood"),
    ("contreplaque-okoume-exterieur", "contreplaqué okoumé extérieur", "plywood", ["thebault-teboply-okoume"], False,
     "plywood"),
    ("contreplaque-okoume-nautique", "contreplaqué okoumé nautique", "plywood", ["thebault-teboply-okoume"], False,
     "plywood"),
    ("contreplaque-okoume-twin", "contreplaqué okoumé twin", "plywood", ["thebault-tebotwin"], False, "plywood"),
    ("contreplaque-bouleau", "contreplaqué bouleau", "plywood", ["riga-wood-birch-plywood"], False, "plywood"),
    ("contreplaque-bouleau-filme", "contreplaqué bouleau filmé (BB/CP phénolique)", "plywood",
     ["riga-wood-birch-plywood"], False, "plywood"),
    ("contreplaque-antiderapant", "contreplaqué antidérapant", "plywood", ["riga-wood-birch-plywood"], False,
     "plywood"),
    ("contreplaque-powerplex", "contreplaqué Powerplex", "plywood", ["houtwerf-powerplex"], True, "plywood"),
    ("contreplaque-pin", "contreplaqué pin", "plywood", ["thebault-tebopin"], False, "plywood"),
    ("contreplaque-marin-pin", "contreplaqué marin pin", "plywood", ["thebault-tebopin"], False, "plywood"),
    ("panneau-3-plis-epicea", "panneau 3 plis épicéa", "solid wood panel", ["binderholz-3-ply-spruce"], False,
     "plywood"),
    ("contreplaque-ordinaire", "contreplaqué ordinaire", "plywood", [], False, "plywood"),
    ("contreplaque-naturel", "contreplaqué naturel", "plywood", [], False, "plywood"),
    ("contreplaque", "contreplaqué", "plywood", [], False, "plywood"),
    ("contreplaque-decor", "contreplaqué décor", "plywood", [], False, "plywood"),
    ("lamelle-colle-chene", "chêne lamellé-collé", "glued solid wood", "oak-european", True, None),
    ("lamelle-colle-hetre", "hêtre lamellé-collé", "glued solid wood", "beech-european", True, None),
    ("massif-hetre-vaporise", "hêtre massif vaporisé", "solid wood", "beech-european", False, None),
    ("massif-hetre-thermo", "hêtre thermo massif", "solid wood", None, False, "beech"),
    ("lamelle-colle-frene", "frêne lamellé-collé", "glued solid wood", "ash-european", True, None),
    ("lamelle-colle-sapin", "sapin lamellé-collé", "glued solid wood", "spruce-norway", False, None),
    ("lamelle-colle-epicea", "épicéa lamellé-collé", "glued solid wood", "spruce-norway", True, None),
    ("lamelle-colle-acacia", "acacia lamellé-collé", "glued solid wood", "acacia-mangium", False, None),
    ("lamelle-colle-aulne", "aulne lamellé-collé", "glued solid wood", "alder-black", True, None),
    ("lamelle-colle-teck", "teck lamellé-collé", "glued solid wood", "teak", True, None),
    ("massif-pin", "pin massif", "solid wood", "pine-maritime", False, None),
    ("massif-eucalyptus", "eucalyptus massif", "solid wood", None, False, None),
]
# Why a line's values are borrowed, when they are: what the listing says and what was taken
BORROWED = {
    "lamelle-colle-sapin": "'sapin' is sold for silver fir and for spruce alike; spruce is the weaker",
    "lamelle-colle-acacia": "'acacia' is sold for robinia and for Acacia mangium; mangium is the weaker",
    "massif-pin": "the title names no pine; maritime pine is the weaker of the two sold in France",
    "massif-hetre-vaporise": "steamed beech, read as beech",
}
# A thickness a maker's table states under another nominal: Leroy Merlin's 6 mm birch is the
# 6.5 mm of the birch plywood tables
NOMINAL = {("riga-wood-birch-plywood", 6.0): 6.5}
# The tag a way of bending gives a material's id
TAGS = {"face grain, flat": "along", "across face grain, flat": "across", "major axis, flat": "major",
        "minor axis, flat": "minor"}
CLASS_NAMES = {c[0]: c[1] for c in CLASSES}
PRODUCT_NAMES = {p[0]: p[1] for p in PRODUCTS}


@lru_cache(maxsize=1)
def _range() -> list[dict]:
    return json.loads((HERE / "range.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _boards() -> dict[str, list[Node]]:
    """wood-panels's materials by the class or product they are."""
    out: dict[str, list[Node]] = {}
    for m in panel_materials():
        out.setdefault(m.payload.get("product") or m.payload["class"], []).append(m)
    return out


def _mm(t: float) -> str:
    return f"{t:g}".replace(".", "-")


def _published(value: float, unit: str, where: str, note: str) -> Quantity:
    return Quantity(value=float(value), unit=unit, provenance="published", grounded=True, source=where, note=note)


def sitemap() -> Node:
    """Leroy Merlin's product sitemap: one clause per panel product it lists."""
    clauses = []
    for r in _range():
        params = {"thickness": _published(r["thickness_mm"], "mm", "title", "Ep.")} if r["thickness_mm"] else {}
        if r["length_mm"]:
            params["length"] = _published(r["length_mm"], "mm", "title", "L.")
            params["width"] = _published(r["width_mm"], "mm", "title", "l.")
        clauses.append(Node(id=f"p-{r['id']}", kind="clause",
                            payload={"locator": f"{r['sitemap']}, the <url> entry of {r['url']} and its "
                                                "image:title",
                                     "url": r["url"], "line": r["line"], "cut_to_size": r["cut_to_size"]},
                            params=params))
    return Node(id="leroy-merlin-sitemap", kind="source",
                name="Leroy Merlin France, product sitemap (www.leroymerlin.fr/sitemap-index.xml)",
                payload={"publisher": "Leroy Merlin France", "year": 2026,
                         "url": "https://www.leroymerlin.fr/sitemap-index.xml", "fetched": "2026-11-12",
                         "licence": "copyrighted",
                         "capture": "private copy of every entry read, with the sha256 of each sitemap file",
                         "in_our_words": "what the shop lists; not what a given store has in stock"},
                children=clauses)


def _sold(line: str, t: float | None) -> dict:
    rows = [r for r in _range() if r["line"] == line and r["thickness_mm"] == t]
    return {"products": [f"{SITEMAP}/p-{r['id']}" for r in rows],
            "sheets_mm": sorted({(r["length_mm"], r["width_mm"]) for r in rows if r["length_mm"]}),
            "cut_to_size": any(r["cut_to_size"] for r in rows)}


def _board(boards: list[str], t: float) -> tuple[str, list[Node]] | None:
    """The first class or product whose band holds the thickness, and its materials in that band."""
    for b in boards:
        at = NOMINAL.get((b, t), t)
        band = [m for m in _boards()[b] if m.payload["thickness_mm"][0] <= at <= m.payload["thickness_mm"][1]]
        if band:
            return b, band
    return None


def _unverified(board: str) -> str:
    if board in CLASS_NAMES:
        return (f"Leroy Merlin's listing states no class; these are the figures of {CLASS_NAMES[board]}, the class "
                "a board of this type is sold under. The label on the panel (its CE marking) states the class.")
    return (f"Leroy Merlin's listing names no maker; these are the values of {PRODUCT_NAMES[board]}, a board of "
            "the same type. The label on the panel says who made it.")


def _panel(line: str, words: str, form: str, boards: list[str], named: bool, key: str, t: float) -> list[Node]:
    sold = _sold(line, t)
    base = f"lm-{line}-{_mm(t)}"
    shop = {"line": line, "thickness_mm": t, **sold, "named": named}
    found = _board(boards, t)
    if not found:
        return [Node(id=base, kind="material", name=f"Leroy Merlin, {words}, {t:g} mm",
                     payload={"form": form, "measured_along": "unstated", "connector_key": key,
                              "leroy_merlin": {**shop, "values_from": None,
                                               "missing": "no published values for this line and thickness"}},
                     links={"per": sold["products"]})]
    board, band = found
    first = TAGS.get(band[0].payload["measured_along"], "")
    out = []
    for m in band:
        tag = TAGS.get(m.payload["measured_along"], "")
        payload = {**m.payload, "form": form, "leroy_merlin": {**shop, "values_from": f"materials/{m.id}"}}
        if "same_panel_as" in payload:
            payload["same_panel_as"] = f"{base}-{first}"
        if not named:
            payload["leroy_merlin"]["unverified"] = _unverified(board)
        params = {k: v if named else v.model_copy(update={"grounded": False}) for k, v in m.params.items()}
        out.append(Node(id=f"{base}-{tag}" if tag else base, kind="material",
                        name=f"Leroy Merlin, {words}, {t:g} mm" + (f", bent {m.payload['measured_along']}" if tag else ""),
                        payload=payload, params=params, links={"per": list(m.links["per"])}))
    return out


def _solid(line: str, words: str, form: str, species: str | None, named: bool, t: float) -> Node:
    sold = _sold(line, t)
    shop = {"line": line, "thickness_mm": t, **sold, "named": named}
    mid = f"lm-{line}-{_mm(t)}"
    if species is None:
        return Node(id=mid, kind="material", name=f"Leroy Merlin, {words}, {t:g} mm",
                    payload={"form": form, "measured_along": "unstated", "connector_key": None,
                             "leroy_merlin": {**shop, "values_from": None,
                                              "missing": "no published values for this wood"}},
                    links={"per": sold["products"]})
    src = next(m for m in european_species() if m.id == species)
    payload = {**src.payload, "form": form, "leroy_merlin": {**shop, "values_from": f"materials/{species}"}}
    params = {k: v.model_copy(update={"grounded": named}) for k, v in src.params.items()}
    if not named:
        payload["leroy_merlin"]["unverified"] = BORROWED[line]
    return Node(id=mid, kind="material", name=f"Leroy Merlin, {words}, {t:g} mm, read as {src.name}",
                payload=payload, params=params, links={"per": list(src.links["per"])})


def materials() -> Node:
    out = []
    for line, words, form, source, named, key in LINES:
        thicknesses = sorted({r["thickness_mm"] for r in _range() if r["line"] == line and r["thickness_mm"]})
        if not thicknesses and any(r["line"] == line for r in _range()):
            thicknesses = [None]
        for t in thicknesses:
            if isinstance(source, list):
                if t is None:
                    out.append(Node(id=f"lm-{line}", kind="material", name=f"Leroy Merlin, {words}",
                                    payload={"form": form, "measured_along": "unstated", "connector_key": key,
                                             "leroy_merlin": {"line": line, **_sold(line, None), "named": False,
                                                              "values_from": None,
                                                              "missing": "the title states no thickness"}},
                                    links={"per": _sold(line, None)["products"]}))
                else:
                    out.extend(_panel(line, words, form, source, named, key, t))
            else:
                out.append(_solid(line, words, form, source, named, t))
    return Node(id="materials", kind="", children=out)


def knowledge() -> list[Node]:
    """The branches to merge beside furniture-design's and wood-panels's: the sitemap
    and the materials."""
    return [Node(id="sources", kind="", children=[sitemap()]), materials()]
