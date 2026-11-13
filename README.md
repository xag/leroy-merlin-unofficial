# leroy-merlin-unofficial

The wood panels Leroy Merlin France sells, each line read as a board of [wood-panels-unofficial](https://github.com/xag/wood-panels-unofficial), as data for [furniture-design](https://github.com/xag/furniture-design). **Unofficial**: Leroy Merlin did not write or endorse it, and nothing here speaks for it.

## What is here

- **The range**: 727 panel products read from Leroy Merlin's public product sitemap, each with its thickness, its sheet size or whether it is cut to size, and its address. They fall into 42 lines: particleboard (raw, white, moisture-resistant, Finsa), melamine-faced shelves, MDF (raw, coloured, Valchromat), hardboard, OSB 3 (Kronospan, Swiss Krono), plywood (poplar, okoumé exterior, marine and twin, birch, film-faced and anti-slip birch, Powerplex, pine, 3-ply spruce, plain), and glued or solid boards of oak, beech, ash, fir, spruce, acacia, alder, teak and pine. What a given store has in stock is not in the sitemap.
- **Which board each line is**: a particleboard, MDF or OSB line takes its class's values from wood-panels-unofficial (P2 for plain and melamine-faced particleboard, P3 for moisture-resistant, MDF for médium, OSB/3), since a board's strength is its class's and not its maker's. A plywood or 3-ply line takes a maker's board of the same type, since plywood has no class with figures. A solid-wood line takes its species from furniture-design (CIRAD's Tropix sheets).
- **The materials**: one per line and thickness (`materials/lm-<line>-<thickness>`), two for a board that bends differently along and across (`-along`/`-across` for plywood, `-major`/`-minor` for OSB). Each copies its board's values and says what is sold (products, sheets, cut to size) and which wood-panels-unofficial material its values are (`leroy_merlin.values_from`).
- **What the listing does not say**: when a line's listing names neither the class nor the maker (aggloméré naturel is read as P2, médium as MDF, birch plywood as Riga Wood's), every value is ungrounded and the material says what the label on the panel settles: its CE marking states the class and the maker's declaration. Lines nothing describes (plain plywood, décor plywood, birch OSB, thermo beech, eucalyptus) have a material with what is sold and no values.

No kinds and no rules of its own: a part that `uses` one of these materials is judged by furniture-design's rules.

## Sources

The product pages are behind a captcha, which is not got round; the range comes from the sitemap the shop publishes for robots. The entries as fetched are kept in a private repo, and `tests/test_values.py` checks every product's sizes against them: clone that repo beside this one, or set `FURNITURE_REPO`, or that test fails and says why. The boards' values, and their checks against the makers' documents, are wood-panels-unofficial's.

## Using it

```python
from furniture_design.knowledge import knowledge as general, merge
from wood_panels_unofficial import knowledge as wood_panels
from leroy_merlin_unofficial import knowledge as leroy_merlin

tree.root.children = merge(general(), wood_panels(), leroy_merlin()) + [pieces]
```

A part then links `uses: ["materials/lm-contreplaque-bouleau-18-along"]` and states `span_along: "face grain, flat"`, or `uses: ["materials/lm-agglomere-18"]` and `span_along: "flat"`.

## Design ledger

```sh
uv sync
uv run quern brief .
uv run quern check
```

The open debts: what the unbranded lines are (their class or maker, read from their type), and the lines and thicknesses with no values. There is no flight-recorder boundary: nothing here touches storage, the network, the clock or randomness at run time.

## Licence

- **The code** (`leroy_merlin_unofficial/*.py`, `tests/`, `ledger/`) is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE), copyright 2026 Xavier Grehant.
- **The knowledge base**, the database `leroy_merlin_unofficial.knowledge()` returns (range.json and every value on its nodes), is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0](LICENSE-DATA), database rights included, with one added permission: designing, building and selling furniture with it is allowed. An improvement is published here, through [CONTRIBUTING.md](CONTRIBUTING.md).
- Leroy Merlin's product names are cited from its pages, not licensed.

## Tests

`uv run pytest --testmon`, then `uv run pytest`. Both stop at the first failure.
