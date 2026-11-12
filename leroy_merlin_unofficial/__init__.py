"""The wood panels Leroy Merlin France sells, as data on furniture-design's kinds (source,
clause, material). Unofficial: Leroy Merlin and the panel makers neither wrote nor endorsed it.

Two kinds of source:

- Leroy Merlin's public product sitemap (range.json): every panel product it lists, with the
  thickness, the sheet size or cut-to-size and the address its title gives. Each is a clause
  under sources/leroy-merlin-sitemap. The product pages themselves are behind a captcha and
  are not read (ledger: the-range-is-read-from-the-public-sitemap).
- The makers' Declarations of Performance and data sheets (sources.json): one source per
  document, one clause per thickness or thickness band, its values as printed. They are
  copyrighted, so a clause carries its locator and values and no quote; the copies are kept
  private and tests/test_values.py checks every value against them.

A material is one product line in one thickness, under materials/: `lm-<line>-<thickness>`,
and for plywood and OSB one per way it bends (`-along`/`-across`, `-major`/`-minor`). Its
payload says what Leroy Merlin sells of it (the products, their sheet sizes, whether it is cut
to size) and where its values come from. When Leroy Merlin's listing names no maker, the
values are those of the same type by a maker that publishes them, and every one is ungrounded
until the label on the panel in the store says who made it (ledger:
a-line-whose-maker-is-unnamed-borrows-a-makers-values-ungrounded). A line no source describes
(contreplaqué ordinaire, naturel, décor; OSB bouleau; hêtre thermo; eucalyptus) has a material
with what is sold and no values, so it judges nothing.

    from furniture_design.knowledge import knowledge as general, merge
    from leroy_merlin_unofficial import knowledge as leroy_merlin
    tree.root.children = merge(general(), leroy_merlin()) + [pieces]
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from furniture_design.knowledge import DESIGN_STRESS_CLAUSES, design_stress, european_species
from quern.provenance import Quantity
from quern.tree import Node

HERE = Path(__file__).parent
SITEMAP = "sources/leroy-merlin-sitemap"
TROPIX = "sources/tropix-{}/properties"

# Every product line the sitemap's titles name: its words as Leroy Merlin's titles give them,
# the form of board, where its values come from (maker documents, in the order they are
# tried, or a species material of furniture-design), whether Leroy Merlin's listing names the
# maker those values belong to, and the key a connector's strengths are stored under.
# (line, words, form, values from, maker named, connector_key)
LINES = [
    ("agglomere", "aggloméré naturel", "particleboard", ["finsa-fimapan-ez-dop-00067"], False, "particleboard"),
    ("agglomere-finsa", "aggloméré Finsa", "particleboard", ["finsa-fimapan-ez-dop-00067"], True, "particleboard"),
    ("agglomere-hydrofuge", "aggloméré hydrofuge", "particleboard", ["finsa-fimapan-h-ez-dop-00094"], False,
     "particleboard"),
    ("agglomere-hydrofuge-finsa", "aggloméré hydrofuge Finsa", "particleboard", ["finsa-fimapan-h-ez-dop-00094"],
     True, "particleboard"),
    ("agglomere-blanc", "aggloméré blanc (mélaminé)", "melamine-faced particleboard",
     ["finsa-fimaplast-ez-dop-00267"], False, "particleboard"),
    ("agglomere-melamine", "tablette aggloméré mélaminé", "melamine-faced particleboard",
     ["finsa-fimaplast-ez-dop-00267"], False, "particleboard"),
    ("mdf", "médium (MDF) naturel", "MDF", ["finsa-fibrapan-ez-dop-00090", "finsa-fibrapan-ez-datasheet"], False,
     "mdf"),
    ("mdf-teinte", "médium (MDF) blanc, gris, noir ou chêne", "MDF",
     ["finsa-fibrapan-ez-dop-00090", "finsa-fibrapan-ez-datasheet"], False, "mdf"),
    ("mdf-valchromat", "médium teinté dans la masse Valchromat", "MDF", ["valchromat-e05-dop-04-02"], True, "mdf"),
    ("panneau-fibres-dures", "panneau de fibres dures (isorel)", "hardboard",
     ["betanzos-htp-premium-dop", "betanzos-hardboard-epd"], False, "hardboard"),
    ("osb-3", "OSB 3", "OSB/3", ["kronospan-osb3-dop-18112013"], False, "osb"),
    ("osb-3-kronospan", "OSB 3 Kronospan", "OSB/3", ["kronospan-osb3-dop-18112013"], True, "osb"),
    ("osb-3-swiss-krono", "OSB 3 Swiss Krono", "OSB/3", ["swiss-krono-osb3-dop-cpr-164"], True, "osb"),
    ("osb-bouleau-swiss-krono", "OSB bouleau Swiss Krono", "OSB/3", [], False, "osb"),
    ("contreplaque-peuplier", "contreplaqué peuplier", "plywood",
     ["garnica-poplar-dop-gar-30", "toro-poplar-datasheet"], False, "plywood"),
    ("contreplaque-peuplier-pircher", "contreplaqué peuplier Pircher", "plywood",
     ["garnica-poplar-dop-gar-30", "toro-poplar-datasheet"], False, "plywood"),
    ("contreplaque-okoume-exterieur", "contreplaqué okoumé extérieur", "plywood",
     ["thebault-dop-01-teboply-okoume"], False, "plywood"),
    ("contreplaque-okoume-nautique", "contreplaqué okoumé nautique", "plywood",
     ["thebault-dop-01-teboply-okoume"], False, "plywood"),
    ("contreplaque-okoume-twin", "contreplaqué okoumé twin", "plywood", ["thebault-dop-03-tebotwin"], False,
     "plywood"),
    ("contreplaque-bouleau", "contreplaqué bouleau", "plywood", ["riga-wood-plywood-handbook"], False, "plywood"),
    ("contreplaque-bouleau-filme", "contreplaqué bouleau filmé (BB/CP phénolique)", "plywood",
     ["riga-wood-plywood-handbook"], False, "plywood"),
    ("contreplaque-antiderapant", "contreplaqué antidérapant", "plywood", ["riga-wood-plywood-handbook"], False,
     "plywood"),
    ("contreplaque-powerplex", "contreplaqué Powerplex", "plywood", ["houtwerf-powerplex-bio-dop"], True,
     "plywood"),
    ("contreplaque-pin", "contreplaqué pin", "plywood", ["thebault-dop-12-tebopin"], False, "plywood"),
    ("contreplaque-marin-pin", "contreplaqué marin pin", "plywood", ["thebault-dop-12-tebopin"], False, "plywood"),
    ("panneau-3-plis-epicea", "panneau 3 plis épicéa", "solid wood panel", ["binderholz-swp-dop"], False, "plywood"),
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
NOMINAL = {("riga-wood-plywood-handbook", 6.0): 6.5}
# The two ways a plywood or OSB board bends, and what its part's span_along must say
WAYS = {"plywood": [("parallel", "along", "face grain, flat"), ("perpendicular", "across", "across face grain, flat")],
        "solid wood panel": [("parallel", "along", "face grain, flat"),
                             ("perpendicular", "across", "across face grain, flat")],
        "OSB/3": [("major", "major", "major axis, flat"), ("minor", "minor", "minor axis, flat")]}
# The density a document without one borrows: (document, from, why)
DENSITY_FROM = {
    "kronospan-osb3-dop-18112013": ("sources/swiss-krono-osb3-dop-cpr-164/10-18/density_low",
                                    "Kronospan's declaration states no density; Swiss Krono's OSB/3 mean"),
    "binderholz-swp-dop": (TROPIX.format("spruce-norway") + "/relative_density",
                           "binderholz states no density; Norway spruce's, the species of its layers"),
}


@lru_cache(maxsize=1)
def _range() -> list[dict]:
    return json.loads((HERE / "range.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _documents() -> dict[str, dict]:
    return {d["id"]: d for d in json.loads((HERE / "sources.json").read_text(encoding="utf-8"))["documents"]}


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


def makers() -> list[Node]:
    """One source per maker document, one clause per thickness or band, its values as printed."""
    out = []
    for d in _documents().values():
        clauses = [Node(id=c["id"], kind="clause",
                        payload={"locator": c["locator"], "thickness_mm": c["thickness"],
                                 "rows": {k: v["printed"] for k, v in c["params"].items()}},
                        params={k: _published(v["value"], v["unit"], c["locator"],
                                              f"{v['statistic']}{', ' + v['test'] if v.get('test') else ''}")
                                for k, v in c["params"].items()})
                   for c in d["clauses"]]
        out.append(Node(id=d["id"], kind="source", name=f"{d['publisher']}: {d['title']}",
                        payload={"publisher": d["publisher"], "year": 2026, "url": d["url"], "fetched": d["fetched"],
                                 "sha256": d["sha256"], "licence": "copyrighted",
                                 "capture": "private copy, identified by its sha256"
                                            + (", values transcribed from its scanned pages"
                                               if d["capture"] == "transcribed" else ""),
                                 "statistic": d["statistic_note"]},
                        children=clauses))
    return out


def _clause(doc: str, t: float) -> dict | None:
    t = NOMINAL.get((doc, t), t)
    return next((c for c in _documents()[doc]["clauses"] if c["thickness"][0] <= t <= c["thickness"][1]), None)


def _q(value: float, unit: str, refs: list[str], note: str, grounded: bool) -> Quantity:
    return Quantity(value=float(value), unit=unit, provenance="derived", grounded=grounded, derived_from=refs,
                    note=note)


def _sold(line: str, t: float | None) -> dict:
    rows = [r for r in _range() if r["line"] == line and r["thickness_mm"] == t]
    return {"products": [f"{SITEMAP}/p-{r['id']}" for r in rows],
            "sheets_mm": sorted({(r["length_mm"], r["width_mm"]) for r in rows if r["length_mm"]}),
            "cut_to_size": any(r["cut_to_size"] for r in rows)}


def _panel(line: str, words: str, form: str, docs: list[str], named: bool, key: str, t: float) -> list[Node]:
    sold = _sold(line, t)
    base = f"lm-{line}-{_mm(t)}"
    found = next(((d, c) for d in docs if (c := _clause(d, t))), None)
    shop = {"line": line, "thickness_mm": t, **sold, "maker_named": named}
    if not found:
        return [Node(id=base, kind="material", name=f"Leroy Merlin, {words}, {t:g} mm",
                     payload={"form": form, "measured_along": "unstated", "connector_key": key,
                              "leroy_merlin": {**shop, "values_from": None,
                                               "missing": "no published values for this line and thickness"}},
                     links={"per": sold["products"]})]
    doc, c = found
    ref = f"sources/{doc}/{c['id']}"
    pr = c["params"]
    unverified = "" if named else " (the listing names no maker: this maker's values, until the label says)"
    density = None
    if "density_low" in pr:
        lo, hi = pr["density_low"]["value"], pr["density_high"]["value"]
        density = _q((lo + hi) / 2, "kg/m3", [f"{ref}/density_low", f"{ref}/density_high"],
                     "the middle of the stated density" + unverified, named)
    elif doc in DENSITY_FROM:
        src, why = DENSITY_FROM[doc]
        density = _q(_value(src), "kg/m3", [src], why, False)
    elif len(docs) > 1:
        other = next((d, oc) for d in docs[1:] if (oc := _clause(d, t)) and "density_low" in oc["params"])
        oref = f"sources/{other[0]}/{other[1]['id']}"
        density = _q(other[1]["params"]["density_low"]["value"], "kg/m3", [f"{oref}/density_low"],
                     "the maker's other document" + unverified, named)
    ways = WAYS.get(form, [("", "", "flat")])
    out = []
    for suffix, tag, along in ways:
        s_key, e_key = (f"bending_strength_{suffix}", f"bending_modulus_{suffix}") if suffix else (
            "bending_strength", "bending_modulus")
        params = {}
        if density:
            params["density"] = density
        if s_key in pr:
            s = pr[s_key]
            characteristic = s["statistic"] == "characteristic"
            ds = design_stress(s["value"], f"{ref}/{s_key}", characteristic=characteristic)
            params["design_bending_stress"] = ds.model_copy(update={"grounded": named,
                                                                    "note": ds.note + unverified})
            if not characteristic:
                params["modulus_of_rupture"] = _q(s["value"], "MPa", [f"{ref}/{s_key}"],
                                                  f"{s['statistic']}" + unverified, named)
        modulus = "unstated"
        if e_key in pr:
            e = pr[e_key]
            params["modulus_of_elasticity"] = _q(e["value"], "MPa", [f"{ref}/{e_key}"],
                                                 f"{e['statistic']}, {e.get('test', 'test not printed')}" + unverified,
                                                 named)
            modulus = "apparent" if e.get("test") == "EN 310" else "true"
            if modulus == "true" and "shear_modulus_rolling" in pr:
                params["shear_modulus_rolling"] = _q(pr["shear_modulus_rolling"]["value"], "MPa",
                                                     [f"{ref}/shear_modulus_rolling"],
                                                     "rolling shear: the shear of a board bent flat" + unverified, named)
        mid = f"{base}-{tag}" if tag else base
        payload = {"form": form, "measured_along": along, "modulus": modulus, "connector_key": key,
                   "leroy_merlin": {**shop, "values_from": doc}}
        if tag:
            payload["same_panel_as"] = f"{base}-{ways[0][1]}"
        if not named:
            payload["leroy_merlin"]["unverified"] = ("Leroy Merlin's listing names no maker; these are "
                                                     f"{_documents()[doc]['publisher']}'s values for the same type. "
                                                     "The label on the panel says who made it.")
        out.append(Node(id=mid, kind="material",
                        name=f"Leroy Merlin, {words}, {t:g} mm" + (f", bent {along}" if tag else ""),
                        payload=payload, params=params,
                        links={"per": [ref, *DESIGN_STRESS_CLAUSES,
                                       *([DENSITY_FROM[doc][0].rsplit("/", 1)[0]] if doc in DENSITY_FROM else [])]}))
    return out


def _value(ref: str) -> float:
    """The value at a clause param path: a maker document's, or a Tropix sheet's relative
    density as kg/m3."""
    _, src, clause, param = ref.split("/")
    if src.startswith("tropix-"):
        from furniture_design.knowledge import TROPIX_SHEETS
        sheet = next(s for s in TROPIX_SHEETS if f"tropix-{s[0]}" == src)
        return 1000.0 * sheet[7]
    return next(c for c in _documents()[src]["clauses"] if c["id"] == clause)["params"][param]["value"]


def _solid(line: str, words: str, form: str, species: str | None, named: bool, t: float) -> Node:
    sold = _sold(line, t)
    shop = {"line": line, "thickness_mm": t, **sold, "maker_named": named}
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
                                             "leroy_merlin": {"line": line, **_sold(line, None), "maker_named": False,
                                                              "values_from": None,
                                                              "missing": "the title states no thickness"}},
                                    links={"per": _sold(line, None)["products"]}))
                else:
                    out.extend(_panel(line, words, form, source, named, key, t))
            else:
                out.append(_solid(line, words, form, source, named, t))
    return Node(id="materials", kind="", children=out)


def knowledge() -> list[Node]:
    """The branches to merge beside furniture-design's: the sources and the materials."""
    return [Node(id="sources", kind="", children=[sitemap(), *makers()]), materials()]
