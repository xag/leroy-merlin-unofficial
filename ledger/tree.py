"""The decisions leroy-merlin-unofficial is bound by, as a ledger. Read it with
`uv run quern brief .`, never whole.

Vocabulary: ledger@0.8.0 and grounding@1.2.0, pinned in quern.lock.
"""

from __future__ import annotations

import os
from pathlib import Path

import quern.grounding  # noqa: F401
from quern import Node, Quern
from quern.library import consume

OWNER = ("we're going to choose the wood at leroy merlin. Make sure we have all the knowledge in the quern "
         "tree about every type of wood panels that can be found there")
OWNER_SPLIT = "We need to keep the makers too but not necessarily as specific packages."
OWNER_CLASS = "is the strength of a finsa particle board really linked to finsa or to the particle board?"


def _alt(id_: str, name: str, why: str) -> Node:
    return Node(id=id_, kind="alternative", name=name, payload={"why": why})


def entries() -> list[Node]:
    return [
        Node(
            id="the-panels-are-data-on-furniture-designs-kinds", kind="decision",
            name="Leroy Merlin's panels and their makers' values are knowledge nodes on furniture-design's kinds "
                 "(source, clause, material), shipped as Python and two data files (`knowledge()`, range.json, "
                 "sources.json); this repo defines no kind or rule. furniture-design names no shop and no maker, "
                 "so they are here",
            payload={"decided_on": "2026-11-12", "the_owner": OWNER,
                     "why": "A part made of a panel bought there reads its density, stiffness and design stress "
                            "as furniture-design's rules already do; what the shop adds is which boards exist, in "
                            "which thicknesses and sheets, and whose values they carry. furniture-design keeps "
                            "the species and the method (its ledger: the-method-is-public-and-names-no-home, "
                            "a-makers-products-are-their-own-package)."},
            children=[
                _alt("in-furniture-design", "Add the shop's range to furniture-design",
                     "furniture-design names no maker and no shop."),
                _alt("in-the-app", "Keep the range in the furniture app's repo",
                     "Another app, or a person with the packages alone, could not choose at the shop."),
            ],
        ),
        Node(
            id="the-range-is-read-from-the-public-sitemap", kind="decision",
            name="What Leroy Merlin sells is read from its public product sitemap: each panel product's address and "
                 "image title, read into its line, thickness, sheet size and whether it is cut to size. The product "
                 "pages, behind a captcha, are not read, and the captcha is not got round",
            payload={"decided_on": "2026-11-12", "the_owner": OWNER,
                     "why": "The sitemap is published for robots to read and names every product with its "
                            "dimensions. The pages would say more (maker, glue class, stock per store), but they "
                            "answer an automated browser with a captcha, which is the shop saying no."},
            links={"rests_on": ["the-range-is-data-on-wood-panels-boards"]},
            children=[
                _alt("solve-the-captcha", "Drive a browser through the captcha",
                     "Gets round a control the shop put there on purpose."),
                _alt("search-snippets", "Read the pages through a search engine's summaries",
                     "Not a copy anyone can check a value against."),
            ],
        ),
        Node(
            id="a-material-is-one-line-in-one-thickness", kind="decision",
            name="A material is one product line in one thickness (`lm-<line>-<thickness>`), and a plywood, 3-ply or "
                 "OSB board is two, one per way it bends (`-along`/`-across`, `-major`/`-minor`, same_panel_as); "
                 "its payload says what the shop sells of it, products, sheets and cut to size, and where its "
                 "values come from",
            payload={"decided_on": "2026-11-12",
                     "why": "The makers' values change with thickness (a band per EN 312 or EN 300, a row per "
                            "plywood thickness), a part has one thickness, and a plywood board bent with its face "
                            "grain across the span is a different material for the checks (furniture-design: "
                            "a-material-says-which-way-its-values-were-measured)."},
            links={"rests_on": ["the-range-is-data-on-wood-panels-boards"]},
            children=[
                _alt("one-material-per-line", "One material per line with a value per thickness",
                     "Every rule would have to pick the value by the part's thickness."),
            ],
        ),
        Node(
            id="a-line-whose-maker-is-unnamed-borrows-a-makers-values-ungrounded", kind="decision",
            name="A line whose listing names its maker (Finsa, Kronospan, Swiss Krono, Valchromat, Powerplex) takes "
                 "that maker's published values, grounded; a line that names none takes the values a maker "
                 "publishes for the same type (Finsa for particleboard and MDF, Garnica and Toro for poplar, "
                 "Thebault for okoumé and pine, Riga Wood for birch, binderholz for 3-ply spruce, Kronospan for "
                 "OSB, Betanzos for hardboard), every one ungrounded and the material saying so; a solid-wood line "
                 "takes its species' values, and the weaker species where its name covers two",
            payload={"decided_on": "2026-11-12", "the_owner": OWNER,
                     "why": "Without the product pages the maker of an unbranded board is unknown, but its type "
                            "is not, and a board of a type is not far from another maker's of that type. Grounded "
                            "values would claim what nobody checked; no values would leave the choice with nothing "
                            "to judge by. Ungrounded values are judged and flagged: the label on the panel in the "
                            "store (its CE marking and declaration number) settles which maker it is."},
            links={"rests_on": ["the-range-is-read-from-the-public-sitemap", "a-material-is-one-line-in-one-thickness"]},
            children=[
                _alt("no-values-for-unbranded", "Give an unbranded line no values",
                     "Most of the range would judge nothing."),
                _alt("grounded-proxies", "Take the type's values as grounded",
                     "Would claim a maker's declaration for a board nobody knows it made."),
            ],
        ),
        Node(
            id="the-values-are-checked-against-a-private-copy", kind="decision",
            name="Every value is checked by a test against the document as fetched, identified by its sha256 and "
                 "kept with its text in the private repo xag/furniture (sources/leroy-merlin); a scanned page is "
                 "transcribed there, and says so; the test fails, never skips, when the copy is not beside this repo",
            payload={"decided_on": "2026-11-12",
                     "why": "The documents are copyrighted (furniture-design: a-copyrighted-source-is-cited-by-"
                            "locator-and-values); a value with no copy to check it against is a number someone "
                            "typed. Kronospan's and binderholz's declarations are images with no text, read by eye."},
            links={"rests_on": ["the-range-is-data-on-wood-panels-boards"]},
            children=[
                _alt("skip-without-the-copy", "Skip the check when the copy is absent",
                     "A skipped check reads as green on every machine that cannot run it."),
            ],
        ),
        Node(
            id="the-knowledge-is-shared-unchanged-and-improved-only-here", kind="decision",
            name="The knowledge base, the database knowledge() returns, is licensed CC BY-NC-ND 4.0 with one added "
                 "permission (designing, building and selling furniture with it); the code is AGPL-3.0-or-later, "
                 "as for furniture-design and lamello-unofficial",
            payload={"decided_on": "2026-11-12",
                     "why": "The same terms as the packages it extends (their ledgers: the-knowledge-is-shared-"
                            "unchanged-and-improved-only-here), so a copy cannot grow elsewhere and an improvement "
                            "is published here."},
            children=[
                _alt("another-licence", "Another licence for this package",
                     "One base under two sets of terms would make the whole unusable under either."),
            ],
        ),
        Node(
            id="the-range-is-data-on-wood-panels-boards", kind="decision", meta={"amended": "b0df928cd0ea wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
            name="This package holds what Leroy Merlin lists (range.json, read into one clause per product) and "
                 "which board each line is; the boards' values, a class's or a maker's, are wood-panels's "
                 "materials, which each line's material copies. This repo defines no kind or rule and holds no maker "
                 "document",
            payload={"decided_on": "2026-11-13", "the_owner": OWNER_SPLIT,
                     "why": "A maker's declaration and a class's figures hold wherever the board is sold; what the "
                            "shop adds is which boards it lists, in which thicknesses and sheets "
                            "(wood-panels: the-classes-and-the-makers-are-one-package)."},
            links={"supersedes": ["the-panels-are-data-on-furniture-designs-kinds"]},
            children=[
                _alt("makers-here", "Keep the makers' documents in this package",
                     "A second shop would copy them or depend on this one."),
            ],
        ),
        Node(
            id="a-line-takes-its-classs-values-or-a-makers", kind="decision", meta={"amended": "b67e56213391 wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
            name="A line of particleboard, MDF or OSB takes its class's values (P2 for plain and melamine-faced "
                 "particleboard, P3 for moisture-resistant, MDF for médium, OSB/3), and a line of plywood or 3-ply "
                 "a maker's board of the same type; a line whose listing names the class or the maker (OSB 3, "
                 "Finsa, Kronospan, Swiss Krono, Valchromat, Powerplex) is grounded, and every other value is "
                 "ungrounded, the material saying what the label on the panel settles; a solid-wood line takes "
                 "its species' values, and the weaker species where its name covers two",
            payload={"decided_on": "2026-11-13", "the_owner": OWNER_CLASS,
                     "why": "A particleboard's strength is its class's, not its maker's (wood-panels: "
                            "a-boards-strength-is-its-classs), so an unbranded board of a known type needs only "
                            "its class confirmed; the class a type is sold under is the usual one, not a certainty "
                            "('hydrofuge' may be P3 or P5), so it stays ungrounded until the label says. Plywood's "
                            "strength is its maker's and species', so the maker is what the label must settle."},
            links={"supersedes": ["a-line-whose-maker-is-unnamed-borrows-a-makers-values-ungrounded"],
                   "rests_on": ["the-range-is-data-on-wood-panels-boards", "a-material-is-one-line-in-one-thickness"]},
            children=[
                _alt("maker-values-for-classed-boards", "Keep borrowing a maker's values for unbranded particleboard and MDF",
                     "Calls a class's figures a maker's."),
            ],
        ),
        Node(
            id="the-range-is-checked-against-the-sitemap-as-fetched", kind="decision", meta={"amended": "e8f18c1fd99b wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
            name="Every product's line, thickness and sheet size is checked by a test against the sitemap entry as "
                 "fetched, kept in the private repo xag/furniture (sources/leroy-merlin/sitemap-entries.json) with "
                 "the sha256 of each sitemap file; the test fails, never skips, when the copy is not beside this "
                 "repo. The boards' values are checked by wood-panels's tests",
            payload={"decided_on": "2026-11-13",
                     "why": "A size with no copy to check it against is a number someone typed; a skipped check "
                            "reads as green on every machine that cannot run it."},
            links={"supersedes": ["the-values-are-checked-against-a-private-copy"]},
            children=[
                _alt("skip-without-the-copy", "Skip the check when the copy is absent",
                     "A skipped check reads as green on every machine that cannot run it."),
            ],
        ),
        Node(
            id="what-the-unbranded-lines-are", kind="debt",
            name="The class of Leroy Merlin's unbranded particleboard and MDF lines and the maker of its unbranded "
                 "plywood, 3-ply and hardboard lines are read from their type, not from the board",
            payload={"decided_on": "2026-11-13",
                     "what": "Aggloméré naturel, blanc and the mélaminé shelves are read as P2, aggloméré hydrofuge "
                             "as P3, médium as MDF; poplar, okoumé, birch and pine plywood, 3-ply spruce and "
                             "hardboard take a maker's board of the same type. The CE label on the panel states the "
                             "class and the maker's declaration number."},
            links={"rests_on": ["a-line-takes-its-classs-values-or-a-makers"]},
            children=[
                Node(id="read-the-label-in-the-store", kind="discharge", meta={"amended": "6a22888abb56 wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
                     name="Read the class, the maker and the declaration number on the panel",
                     payload={"who": "whoever is at the shop, and the assistant once the label is photographed",
                              "how": "Name the line's class or maker in LINES (adding the maker's declaration to "
                                     "wood-panels when it is new), and the line's values become grounded"}),
                Node(id="tombstone-the-makers-of-the-unbranded-lines", kind="tombstone",
                     name="'the-makers-of-the-unbranded-lines' - replaced",
                     payload={"was": "the-makers-of-the-unbranded-lines",
                              "why": "for particleboard and MDF it is the class the label must settle, not the maker; "
                                     "this debt says so"}),
            ],
        ),
        Node(
            id="a-line-naming-no-species-takes-the-weaker-stand-in", kind="decision",
            name="A line whose title names no species or whose board is uncertain takes a stand-in's values, every "
                 "one ungrounded, the material saying what was read and what the label settles: plain, natural and "
                 "ordinary plywood read as ALLIN's all-poplar plywood (the less stiff of the two French boards that "
                 "cover those thicknesses), OSB bouleau Swiss Krono as Swiss Krono's OSB/3 (its one declared OSB), "
                 "eucalyptus as Eucalyptus grandis, thermo beech as beech treated at 190 °C",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "Now source lots of data from authoritative sources to answer any relevant "
                                  "question about the bench for any choice of wood panel",
                     "why": "A line without values judges nothing, so a question about the bench in that board had "
                            "no answer; an ungrounded stand-in answers it and says it is not the board's own. The "
                            "weaker of two candidates keeps the answer on the side that holds when the label shows "
                            "the other, as the solid-wood lines already do."},
            links={"rests_on": ["a-line-takes-its-classs-values-or-a-makers"]},
            children=[
                _alt("leave-them-without-values", "Leave these lines without values until the label is read",
                     "Every question about the bench in these boards stays unanswered, though the type is known."),
                _alt("okoume-for-plain-plywood", "Read plain plywood as ALLIN's okoumé",
                     "Okoumé is the stiffer of the two; a poplar board on sale would then sag more than predicted."),
            ],
        ),
        Node(
            id="lines-still-without-values", kind="debt",
            name="Contreplaqué décor, 3 mm poplar, 5 and 10 mm Powerplex, 5 mm pine plywood, and plain plywood at "
                 "3, 9, 19 and 27 mm have no published values here, and judge nothing",
            payload={"decided_on": "2026-11-13",
                     "what": "Décor plywood states no thickness, maker or core; ALLIN's poplar starts at 5 mm and "
                             "states no 9, 19 or 27 mm; Houtwerf declares Powerplex only at 15 and 18 mm; pine "
                             "plywood declarations start at 7 to 12 mm."},
            links={"rests_on": ["a-material-is-one-line-in-one-thickness"],
                   "supersedes": ["lines-without-values"]},
            children=[
                Node(id="find-these-boards", kind="discharge",
                     name="Find what each of these boards is and a published value for it",
                     payload={"who": "whoever is at the shop, or a maker's reply",
                              "how": "Read the species and the maker on the label, find their declaration, and add "
                                     "it to wood-panels"}),
            ],
        ),
        Node(
            id="lines-without-values", kind="debt",
            name="Contreplaqué ordinaire, contreplaqué naturel, contreplaqué, contreplaqué décor, OSB bouleau Swiss "
                 "Krono, hêtre thermo and eucalyptus have no published values here, nor do 3 mm poplar, 5 mm "
                 "Pircher poplar, 5 and 10 mm Powerplex and 5 mm pine plywood, and judge nothing",
            payload={"decided_on": "2026-11-13",
                     "what": "The plain plywood lines name no species, Swiss Krono publishes nothing for a birch "
                             "OSB, no source gives numbers for thermo-treated beech or this eucalyptus, and the "
                             "makers' tables stop short of those thicknesses."},
            links={"rests_on": ["a-material-is-one-line-in-one-thickness"]},
            children=[
                Node(id="find-what-each-line-is", kind="discharge", meta={"amended": "48f8b4e6a0a3 wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
                     name="Find what each of these boards is and a published value for it",
                     payload={"who": "whoever is at the shop, or a maker's reply",
                              "how": "Read the species and the maker on the label, find their declaration, and add it "
                                     "to wood-panels"}),
                Node(id="tombstone-lines-with-no-values", kind="tombstone",
                     name="'lines-with-no-values' - replaced",
                     payload={"was": "lines-with-no-values",
                              "why": "28 mm particleboard now takes P2's values; this debt lists what is still missing"}),
                Node(id="tombstone-thebaults-sheets", kind="tombstone", meta={"amended": "8cb68a7607ef wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
                     name="'thebaults-sheets-disagree-with-its-declaration' - moved",
                     payload={"was": "thebaults-sheets-disagree-with-its-declaration",
                              "why": "Thebault's documents are wood-panels's now, and so is the debt"}),
                Node(id="tombstone-a-true-modulus-without-its-shear", kind="tombstone", meta={"amended": "20bf022daf26 wood-panels-unofficial was renamed wood-panels; the claim is unchanged"},
                     name="'a-true-modulus-without-its-shear' - moved",
                     payload={"was": "a-true-modulus-without-its-shear",
                              "why": "Thebault's documents are wood-panels's now, and so is the debt"}),
            ],
        ),
        Node(
            id="the-cutting-service-is-a-tool-with-what-a-store-said", kind="decision",
            name="Leroy Merlin's cutting service is tools/leroy-merlin-cutting-service, a tool a part links sawn_with: it "
                 "cuts nothing narrower than 100 mm and refuses every lamellé-collé line, as one store said, both "
                 "ungrounded (provenance reported) under sources/leroy-merlin-store-visit-2026-11-14. It states no "
                 "cut and no depth, which nothing read gives, so furniture-design's rule refuses a part sent to it "
                 "until the width of its cut is stated",
            payload={"decided_on": "2026-11-14",
                     "the_owner": "Ça peut valoir le coup aussi de modéliser les règles de découpe dans le pack Leroy "
                                  "Merlin unofficial. Par exemple j'ai appris sur place qu'ils ne pouvaient pas faire "
                                  "une découpe de moins de 10 cm de large.",
                     "why": "The service's rules decide whether a part can be cut there at all, and Leroy Merlin's "
                            "pages, where it may publish them, are behind a captcha. What a store says is the only "
                            "source, so it is recorded as said, by whom and when, and marked unverified.",
                     "falsified_by": "Leroy Merlin's published conditions of its cutting service, or another store "
                                     "cutting a strip under 100 mm or a lamellé-collé board"},
            links={"rests_on": ["the-range-is-read-from-the-public-sitemap"]},
            children=[
                _alt("leave-it-out-until-published", "Model nothing until Leroy Merlin publishes its rules",
                     "The cutting sheet would send a 75 mm rail to a service that turns it away."),
                _alt("in-the-piece", "Write the store's rules in the piece that is cut there",
                     "Every piece cut at Leroy Merlin would repeat them; they are the shop's, not the piece's."),
            ],
        ),
        Node(
            id="a-standers-profile-is-a-material-of-its-section", kind="decision",
            name="Leroy Merlin's own STANDERS profiles (aluminium and PVC U, double U, T, H, angles) are read from the "
                 "sitemap titles as the panels are: a title that states H, l, Ep and L is a product, one clause each; "
                 "a material is one section in one material and finish, standers-<shape>-<material>-<finish>-<h>x<w>x<t>, "
                 "its params the section's sizes and its payload sold_at_leroy_merlin the lengths and addresses sold. "
                 "It states no density or strength, which no title gives; a title cut short or naming no wall is left out",
            links={"rests_on": ["the-range-is-read-from-the-public-sitemap"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Je les sertirai de tiges plastique trouvées à Leroy Merlin. Les tiges elles mêmes iront "
                                  "se loger dans des rails construits à partir d'éléments longs en alu [...] / Ok go",
                     "why": "The owner's sliding doors are made of STANDERS profiles: the clear PVC U 87477510 by its "
                            "label, a white aluminium angle 20 x 20 x 1 by its label. Their product pages are behind a "
                            "captcha, so the titles are what is known, as for the panels. A profile is not a panel: "
                            "lm- names a panel whose sheets the cutting sheet lays parts on, so a profile is named "
                            "standers-."},
            children=[
                _alt("the-owners-profiles-only", "Add only the profiles the owner bought",
                     "The next design uses others; the titles give every one the same way."),
                _alt("lm-prefix", "Name them lm-standers-..., as the panels",
                     "The cutting sheet reads an lm- material's sheet sizes, which a profile has not."),
                _alt("a-density-for-aluminium-and-pvc", "Give aluminium and PVC a density so a part of them weighs",
                     "No title or source read here prints one; a value with no source is not stated."),
            ],
        ),
    ]


def build() -> Quern:
    root = Path(__file__).resolve().parents[1]
    lib, refs = consume(root, os.environ.get("QUERN_REGISTRY", root.parent / "quern-registry"))
    quern = Quern(packages=list(refs))
    quern = lib.effective(quern)
    quern.root.children = entries()
    return quern
