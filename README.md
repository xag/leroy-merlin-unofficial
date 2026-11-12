# leroy-merlin-unofficial

The wood panels Leroy Merlin France sells, and their makers' published values, as data for [furniture-design](https://github.com/xag/furniture-design). **Unofficial**: Leroy Merlin and the panel makers did not write or endorse it, and nothing here speaks for them.

## What is here

- **The range**: 727 panel products read from Leroy Merlin's public product sitemap, each with its thickness, its sheet size or whether it is cut to size, and its address. They fall into 42 lines: particleboard (raw, white, moisture-resistant, Finsa), melamine-faced shelves, MDF (raw, coloured, Valchromat), hardboard, OSB 3 (Kronospan, Swiss Krono), plywood (poplar, okoumé exterior, marine and twin, birch, film-faced and anti-slip birch, Powerplex, pine, 3-ply spruce, plain), and glued or solid boards of oak, beech, ash, fir, spruce, acacia, alder, teak and pine. What a given store has in stock is not in the sitemap.
- **The makers' values**: nineteen documents, mostly Declarations of Performance: Finsa (FimaPan E-Z, FimaPan H E-Z, FimaPlast E-Z, FibraPan E-Z), Unilin (Belspan), Valchromat, Betanzos (hardboard), Kronospan and Swiss Krono (OSB/3), Riga Wood (birch plywood), Garnica and Toro (poplar), Thebault (okoumé, twin, pine), binderholz (3-ply spruce) and Houtwerf (Powerplex). Each value carries its document, thickness band, locator and printed form.
- **The materials**: one per line and thickness (`materials/lm-<line>-<thickness>`), two for a board that bends differently along and across (`-along`/`-across` for plywood, `-major`/`-minor` for OSB). Each says what is sold (products, sheets, cut to size) and carries the density, design bending stress and modulus furniture-design's rules read. A solid-wood line takes its species' values from furniture-design (CIRAD's Tropix sheets).
- **Lines whose listing names no maker** borrow the values a maker publishes for the same type, and every borrowed value is ungrounded: the label on the panel (its CE marking and declaration number) says whose values it really has. Lines nothing describes (plain plywood, décor plywood, birch OSB, thermo beech, eucalyptus) have a material with what is sold and no values.

No kinds and no rules of its own: a part that `uses` one of these materials is judged by furniture-design's rules.

## Sources

The product pages are behind a captcha, which is not got round; the range comes from the sitemap the shop publishes for robots. The makers' documents are copyrighted, so they are cited by locator and values and never quoted. The copies as fetched are kept in a private repo, and `tests/test_values.py` checks every value against them: clone that repo beside this one, or set `FURNITURE_REPO`, or that test fails and says why. Kronospan's and binderholz's declarations are scanned images; their values were read by eye and transcribed there, and the transcriptions say so.

## Using it

```python
from furniture_design.knowledge import knowledge as general, merge
from leroy_merlin_unofficial import knowledge as leroy_merlin

tree.root.children = merge(general(), leroy_merlin()) + [pieces]
```

A part then links `uses: ["materials/lm-contreplaque-bouleau-18-along"]` and states `span_along: "face grain, flat"`.

## Design ledger

```sh
uv sync
uv run quern brief .
uv run quern check
```

The open debts: the makers of the unbranded lines, the lines with no values, Thebault's data sheets disagreeing with its declaration, and Thebault's moduli lacking a shear modulus. There is no flight-recorder boundary: nothing here touches storage, the network, the clock or randomness at run time.

## Licence

- **The code** (`leroy_merlin_unofficial/*.py`, `tests/`, `ledger/`) is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE), copyright 2026 Xavier Grehant.
- **The knowledge base**, the database `leroy_merlin_unofficial.knowledge()` returns (range.json, sources.json and every value on its nodes), is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0](LICENSE-DATA), database rights included, with one added permission: designing, building and selling furniture with it is allowed. An improvement is published here, through [CONTRIBUTING.md](CONTRIBUTING.md).
- Leroy Merlin's product names and the makers' values are cited from their pages and documents, not licensed.

## Tests

`uv run pytest --testmon`, then `uv run pytest`. Both stop at the first failure.
