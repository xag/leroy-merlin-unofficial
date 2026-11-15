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

from furniture_design.knowledge import with_authority
from furniture_design.knowledge import knowledge as general_knowledge
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
    ("osb-bouleau-swiss-krono", "OSB bouleau Swiss Krono", "OSB/3", ["swiss-krono-osb-3", "osb-3"], False, "osb"),
    ("contreplaque-peuplier", "contreplaqué peuplier", "plywood",
     ["garnica-poplar-plywood", "toro-poplar-plywood", "allin-poplar-plywood"], False, "plywood"),
    ("contreplaque-peuplier-pircher", "contreplaqué peuplier Pircher", "plywood",
     ["garnica-poplar-plywood", "toro-poplar-plywood", "allin-poplar-plywood"], False, "plywood"),
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
    ("contreplaque-ordinaire", "contreplaqué ordinaire", "plywood", ["allin-poplar-plywood"], False, "plywood"),
    ("contreplaque-naturel", "contreplaqué naturel", "plywood", ["allin-poplar-plywood"], False, "plywood"),
    ("contreplaque", "contreplaqué", "plywood", ["allin-poplar-plywood"], False, "plywood"),
    ("contreplaque-decor", "contreplaqué décor", "plywood", [], False, "plywood"),
    ("lamelle-colle-chene", "chêne lamellé-collé", "glued solid wood", "oak-european", True, None),
    ("lamelle-colle-hetre", "hêtre lamellé-collé", "glued solid wood", "beech-european", True, None),
    ("massif-hetre-vaporise", "hêtre massif vaporisé", "solid wood", "beech-european", False, None),
    ("massif-hetre-thermo", "hêtre thermo massif", "solid wood", "beech-thermally-modified", False, None),
    ("lamelle-colle-frene", "frêne lamellé-collé", "glued solid wood", "ash-european", True, None),
    ("lamelle-colle-sapin", "sapin lamellé-collé", "glued solid wood", "spruce-norway", False, None),
    ("lamelle-colle-epicea", "épicéa lamellé-collé", "glued solid wood", "spruce-norway", True, None),
    ("lamelle-colle-acacia", "acacia lamellé-collé", "glued solid wood", "acacia-mangium", False, None),
    ("lamelle-colle-aulne", "aulne lamellé-collé", "glued solid wood", "alder-black", True, None),
    ("lamelle-colle-teck", "teck lamellé-collé", "glued solid wood", "teak", True, None),
    ("massif-pin", "pin massif", "solid wood", "pine-maritime", False, None),
    ("massif-eucalyptus", "eucalyptus massif", "solid wood", "eucalyptus-grandis", False, None),
]
# Why a line's values are borrowed, when they are: what the listing says and what was taken
BORROWED = {
    "lamelle-colle-sapin": "'sapin' is sold for silver fir and for spruce alike; spruce is the weaker",
    "lamelle-colle-acacia": "'acacia' is sold for robinia and for Acacia mangium; mangium is the weaker",
    "massif-pin": "the title names no pine; maritime pine is the weaker of the two sold in France",
    "massif-hetre-vaporise": "steamed beech, read as beech",
    "massif-eucalyptus": "the title names no species; Eucalyptus grandis, the plantation eucalyptus Europe mostly "
                         "imports according to CIRAD's Tropix, is read, and E. globulus is the other candidate",
    "massif-hetre-thermo": "thermally modified beech, read as beech treated at 190 °C for 3.5 h (Schmidtová et al. "
                           "2026); the treatment of the board on sale is unknown, and strength falls as its "
                           "temperature rises",
}
# Why a panel line's board is a stand-in, when its listing names no species or the board is not certain
STAND_IN = {
    "osb-bouleau-swiss-krono": "Swiss Krono declares one OSB, its OSB/3 (DoP CPR-164), and names no birch OSB; "
                               "'bouleau' is read as birch among that board's hardwood strands. The label states "
                               "the board and its class.",
    **{line: "the title names no species; ALLIN's all-poplar plywood is read, the less stiff of the two French "
             "boards (poplar, okoumé) that cover these thicknesses. The label says what the board is."
       for line in ("contreplaque", "contreplaque-naturel", "contreplaque-ordinaire")},
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


def _label(words: str) -> str:
    """What the documents call the board: the line's words and the shop (furniture-design reads a
    material's payload label)."""
    return f"{words[:1].upper()}{words[1:]} Leroy Merlin"


def _panel(line: str, words: str, form: str, boards: list[str], named: bool, key: str, t: float) -> list[Node]:
    sold = _sold(line, t)
    base = f"lm-{line}-{_mm(t)}"
    shop = {"line": line, "thickness_mm": t, **sold, "named": named}
    found = _board(boards, t)
    if not found:
        return [Node(id=base, kind="material", name=f"Leroy Merlin, {words}, {t:g} mm",
                     payload={"form": form, "measured_along": "unstated", "connector_key": key,
                              "label": _label(words),
                              "leroy_merlin": {**shop, "values_from": None,
                                               "missing": "no published values for this line and thickness"}},
                     links={"per": sold["products"]})]
    board, band = found
    first = TAGS.get(band[0].payload["measured_along"], "")
    out = []
    for m in band:
        tag = TAGS.get(m.payload["measured_along"], "")
        payload = {**m.payload, "form": form, "label": _label(words),
                   "leroy_merlin": {**shop, "values_from": f"materials/{m.id}"}}
        if "same_panel_as" in payload:
            payload["same_panel_as"] = f"{base}-{first}"
        if not named:
            payload["leroy_merlin"]["unverified"] = STAND_IN.get(line) or _unverified(board)
        params = {k: v if named else v.model_copy(update={"grounded": False}) for k, v in m.params.items()}
        out.append(Node(id=f"{base}-{tag}" if tag else base, kind="material",
                        name=f"Leroy Merlin, {words}, {t:g} mm" + (f", bent {m.payload['measured_along']}" if tag else ""),
                        payload=payload, params=params, links={"per": list(m.links["per"])}))
    return out


@lru_cache(maxsize=1)
def _general_materials() -> dict[str, Node]:
    """furniture-design's materials by id: the species and the treated woods a solid-wood line reads."""
    return {m.id: m for b in general_knowledge() if b.id == "materials" for m in b.children}


def _solid(line: str, words: str, form: str, species: str | None, named: bool, t: float) -> Node:
    sold = _sold(line, t)
    shop = {"line": line, "thickness_mm": t, **sold, "named": named}
    mid = f"lm-{line}-{_mm(t)}"
    if species is None:
        return Node(id=mid, kind="material", name=f"Leroy Merlin, {words}, {t:g} mm",
                    payload={"form": form, "measured_along": "unstated", "connector_key": None,
                             "label": _label(words),
                             "leroy_merlin": {**shop, "values_from": None,
                                              "missing": "no published values for this wood"}},
                    links={"per": sold["products"]})
    src = _general_materials()[species]
    payload = {**src.payload, "form": form, "label": _label(words),
               "leroy_merlin": {**shop, "values_from": f"materials/{species}"}}
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
                                             "label": _label(words),
                                             "leroy_merlin": {"line": line, **_sold(line, None), "named": False,
                                                              "values_from": None,
                                                              "missing": "the title states no thickness"}},
                                    links={"per": _sold(line, None)["products"]}))
                else:
                    out.extend(_panel(line, words, form, source, named, key, t))
            else:
                out.append(_solid(line, words, form, source, named, t))
    return Node(id="materials", kind="", children=out)


VISIT = "sources/leroy-merlin-store-visit-2026-11-14"


def store_visit() -> Node:
    """What a store's cutting service said it does not do, as reported after a visit: no source Leroy
    Merlin publishes says it (its pages are behind a captcha), so every value is ungrounded."""
    return Node(id="leroy-merlin-store-visit-2026-11-14", kind="source",
                name="Leroy Merlin France, a store's cutting service, as reported after a visit on 14 November 2026",
                payload={"publisher": "reported by a customer of a Leroy Merlin France store", "year": 2026,
                         "licence": "unstated",
                         "in_our_words": "one store, by word of mouth; Leroy Merlin publishes no rule of its "
                                         "cutting service that could be read"},
                children=[
                    Node(id="narrowest-cut", kind="clause",
                         payload={"locator": "said in the store's cutting service",
                                  "quote": "j'ai appris sur place qu'ils ne pouvaient pas faire une découpe de "
                                           "moins de 10 cm de large"},
                         params={"min_part_width": Quantity(value=100, unit="mm", provenance="reported",
                                                            grounded=False, note="10 cm")}),
                    Node(id="no-glulam", kind="clause",
                         payload={"locator": "noted on the day of the visit",
                                  "quote": "Le magasin ne découpe pas le lamellé-collé"}),
                ])


def cutting_service() -> Node:
    """Leroy Merlin's cutting service as a tool a part links sawn_with: the narrowest part it cuts and
    the boards it does not cut (every lamellé-collé line), as reported; it states no cut and no depth,
    which no source gives."""
    refuses = [f"materials/{m.id}" for m in materials().children
               if (m.payload or {}).get("leroy_merlin", {}).get("line", "").startswith("lamelle-colle")]
    return Node(id="leroy-merlin-cutting-service", kind="tool", name="Leroy Merlin's cutting service",
                payload={"maker": "Leroy Merlin France", "saw_kind": "panel saw",
                         "does": "cuts the panels the store sells to the customer's sizes, in straight cuts",
                         "unverified": "reported from one store's cutting service, not published by Leroy Merlin"},
                params={"min_part_width": Quantity(value=100, unit="mm", provenance="reported", grounded=False,
                                                   derived_from=[f"{VISIT}/narrowest-cut/min_part_width"],
                                                   note="as reported after a visit")},
                links={"per": [f"{VISIT}/narrowest-cut", f"{VISIT}/no-glulam"], "refuses": refuses})


# Who stands behind each source (furniture-design's AUTHORITIES).
AUTHORITY = {
    "leroy-merlin-sitemap": "maker",
    "leroy-merlin-store-visit-2026-11-14": "maker",
}


def knowledge() -> list[Node]:
    """The branches to merge beside furniture-design's and wood-panels's: the sitemap and what a
    store's cutting service said, the materials (the panels, then the STANDERS profiles), and the cutting
    service as a tool."""
    from leroy_merlin_unofficial import profiles
    panels = materials()
    panels.children += profiles.materials()
    return [Node(id="sources", kind="", children=with_authority([sitemap(), store_visit()], AUTHORITY) + [profiles.source()]),
            panels, Node(id="tools", kind="", children=[cutting_service()])]
