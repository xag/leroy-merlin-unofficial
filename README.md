# leroy-merlin-unofficial

The wood panels Leroy Merlin France sells, each line read as a board of [wood-panels](https://github.com/xag/wood-panels), as data for [furniture-design](https://github.com/xag/furniture-design). **Unofficial**: Leroy Merlin did not write or endorse it, and nothing here speaks for it.

## What is here

- **The range**: 727 panel products read from Leroy Merlin's public product sitemap, each with its thickness, its sheet size or whether it is cut to size, and its address. They fall into 42 lines: particleboard (raw, white, moisture-resistant, Finsa), melamine-faced shelves, MDF (raw, coloured, Valchromat), hardboard, OSB 3 (Kronospan, Swiss Krono), plywood (poplar, okoumé exterior, marine and twin, birch, film-faced and anti-slip birch, Powerplex, pine, 3-ply spruce, plain), and glued or solid boards of oak, beech, ash, fir, spruce, acacia, alder, teak and pine. What a given store has in stock is not in the sitemap.
- **Which board each line is**: a particleboard, MDF or OSB line takes its class's values from wood-panels (P2 for plain and melamine-faced particleboard, P3 for moisture-resistant, MDF for médium, OSB/3), since a board's strength is its class's and not its maker's. A plywood or 3-ply line takes a maker's board of the same type, since plywood has no class with figures. A solid-wood line takes its species from furniture-design (CIRAD's Tropix sheets). A line whose title names no species, or whose board is uncertain, takes a stand-in, every value marked unverified: plain, natural and ordinary plywood read as ALLIN's all-poplar plywood, OSB bouleau Swiss Krono as Swiss Krono's OSB/3, eucalyptus as Eucalyptus grandis, thermo beech as beech treated at 190 °C. Each line's material also carries what its board carries: creep (`initial_share_of_longtime`), screw withdrawal from the face and the edge, 24 h swelling and movement with moisture, where wood-panels has them.
- **The materials**: one per line and thickness (`materials/lm-<line>-<thickness>`), two for a board that bends differently along and across (`-along`/`-across` for plywood, `-major`/`-minor` for OSB). Each copies its board's values and says what is sold (products, sheets, cut to size) and which wood-panels material its values are (`leroy_merlin.values_from`).
- **What the listing does not say**: when a line's listing names neither the class nor the maker (aggloméré naturel is read as P2, médium as MDF, birch plywood as Riga Wood's), every value is ungrounded and the material says what the label on the panel settles: its CE marking states the class and the maker's declaration. Lines nothing describes (plain plywood, décor plywood, birch OSB, thermo beech, eucalyptus) have a material with what is sold and no values.

- **The cutting service**: `tools/leroy-merlin-cutting-service`, a tool a part links `sawn_with`. Leroy Merlin publishes nothing on what it cuts, so it states no figure. A material's `sold_cut_to_size_online` says whether the sitemap lists that line sold cut to size on the website, and nothing about what a store's service cuts.

No kinds and no rules of its own: a part that `uses` one of these materials, or is cut by the service, is judged by furniture-design's rules.

Leroy Merlin's own STANDERS profiles are read the same way (`leroy_merlin_unofficial/profiles.py`, `profiles.json`, written by `tools/build_profiles.py`): every STANDERS entry whose title states the flange height, the width, the wall and the length sold (H × l × Ep, L), 223 of 296, is a product. A material is one section in one material and finish, `standers-<shape>-<material>-<finish>-<h>x<w>x<t>` (aluminium or PVC; U, double U, T, H, angle), its params `section_height`, `section_width` and `wall_thickness`, its payload `sold_at_leroy_merlin` the lengths and addresses. For example `standers-u-pvc-transparent-12x12x1` (87477510, 1 m) and `standers-u-aluminium-brut-12x12x1` (87477958, 1 m; 87477962, 2.5 m). No title gives a density or a strength, so none is stated.

## Sources

The product pages are behind a captcha, which is not got round; the range comes from the sitemap the shop publishes for robots. The entries as fetched are kept in a private repo, and `tests/test_values.py` checks every product's sizes against them: clone that repo beside this one, or set `FURNITURE_REPO`, or that test fails and says why. The boards' values, and their checks against the makers' documents, are wood-panels's.

## Using it

```python
from furniture_design.knowledge import knowledge as general, merge
from wood_panels import knowledge as wood_panels
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

`uv run pytest` runs the tests whose code, data or packages changed since they passed, last failures first then the fastest, under a time budget (testplan); `uv run pytest --all` runs them all, once a day. Both stop at the first failure.
