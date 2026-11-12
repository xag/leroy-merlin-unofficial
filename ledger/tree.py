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
            links={"rests_on": ["the-panels-are-data-on-furniture-designs-kinds"]},
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
            links={"rests_on": ["the-panels-are-data-on-furniture-designs-kinds"]},
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
            links={"rests_on": ["the-panels-are-data-on-furniture-designs-kinds"]},
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
            id="the-makers-of-the-unbranded-lines", kind="debt",
            name="The makers of Leroy Merlin's unbranded lines are unknown, so their values are another maker's for "
                 "the same type; the label on the panel says whose they are",
            payload={"decided_on": "2026-11-12",
                     "what": "Aggloméré naturel, blanc, hydrofuge and the mélaminé shelves; MDF naturel and "
                             "coloured; OSB 3; poplar, okoumé, birch, pine and 3-ply spruce plywood; hardboard. "
                             "Recording the maker and declaration number on the label, then that declaration's "
                             "values, discharges a line."},
            links={"rests_on": ["a-line-whose-maker-is-unnamed-borrows-a-makers-values-ungrounded"]},
            children=[Node(id="read-the-label-in-the-store", kind="discharge", name="Read the maker and the declaration number on the panel, then that declaration",
                           payload={"who": "whoever is at the shop, and the assistant once the label is photographed",
                                    "how": "Add the maker's declaration to sources.json, name the line's maker in LINES, and the line's values become grounded"})],
        ),
        Node(
            id="lines-with-no-values", kind="debt",
            name="Contreplaqué ordinaire, contreplaqué naturel, contreplaqué décor, OSB bouleau Swiss Krono, hêtre "
                 "thermo and eucalyptus have no published values here, and judge nothing",
            payload={"decided_on": "2026-11-12",
                     "what": "The plain plywood lines name no species, Swiss Krono publishes nothing for a birch "
                             "OSB, and no source gives numbers for thermo-treated beech or this eucalyptus; some "
                             "thicknesses of described lines are outside every table too (3 mm poplar, 5 and 10 "
                             "mm Powerplex, 5 mm pine plywood, 28 mm particleboard)."},
            links={"rests_on": ["a-material-is-one-line-in-one-thickness"]},
            children=[Node(id="find-what-each-line-is", kind="discharge", name="Find what each of these boards is and a published value for it",
                           payload={"who": "whoever is at the shop, or a maker's reply",
                                    "how": "Read the species and the maker on the label, find their declaration, and add it as a source"})],
        ),
        Node(
            id="thebaults-sheets-disagree-with-its-declaration", kind="debt",
            name="Thebault's data sheets for TeboPly okoumé and TeboMarine give lower bending values than its "
                 "declaration of performance DOP 01 at 8 to 30 mm; the declaration's are used",
            payload={"decided_on": "2026-11-12",
                     "what": "At 15 mm the data sheet gives 18.7 MPa and 3464 MPa along the face grain where the "
                             "declaration gives 30.4 and 5456. A declaration is what the maker is bound by; "
                             "Thebault has not been asked which is right."},
            children=[Node(id="ask-thebault", kind="discharge", name="Ask Thebault which of its two tables is right",
                           payload={"who": "the owner, by mail to Thebault",
                                    "how": "Use the table Thebault confirms and record its answer as a source"})],
        ),
        Node(
            id="a-true-modulus-without-its-shear", kind="debt",
            name="Thebault declares its okoumé, twin and pine plywood moduli to NF EN 789 with no rolling-shear "
                 "modulus, so their sag is not judged; their strength is",
            payload={"decided_on": "2026-11-12",
                     "what": "A modulus measured in pure bending needs a shear term for a board's deflection "
                             "(furniture-design: a-panels-tested-modulus-takes-no-shear-term), and no Thebault "
                             "document gives the shear modulus; Kronospan and binderholz do, so theirs are judged."},
            children=[Node(id="find-a-rolling-shear-modulus", kind="discharge", name="Find the rolling-shear modulus Thebault's boards are designed with",
                           payload={"who": "anyone, from Thebault or a published table for okoumé and pine plywood",
                                    "how": "Add it to the clauses and the materials take a shear term, as Kronospan's and binderholz's do"})],
        ),
    ]


def build() -> Quern:
    root = Path(__file__).resolve().parents[1]
    lib, refs = consume(root, os.environ.get("QUERN_REGISTRY", root.parent / "quern-registry"))
    quern = Quern(packages=list(refs))
    quern = lib.effective(quern)
    quern.root.children = entries()
    return quern
