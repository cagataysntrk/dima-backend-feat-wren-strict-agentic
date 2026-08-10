# Competitor Crawl Coverage

## Completion status

The official competitor inventory in `dima/docs/meetings/20260722/rakip-listesi.md` contains 21 competitors. The crawl combined public sitemap URLs, same-origin internal-link discovery, rendered documentation graphs, and a targeted resolution of the two competitors whose initial sitemap discovery returned zero URLs.

| Measure | Count |
|---|---:|
| Competitors in scope | 21 |
| URL records in final scope | 2,202 |
| Full-page rendered screenshots | 2,198 |
| Explicitly blocked at origin | 4 |
| Unresolved capture failures | 0 |
| Render viewport | 1,440 × 900, full-page screenshot |

## Per-competitor inventory

| Competitor | Inventory | Captured | Screenshots | Blocked |
|---|---:|---:|---:|---:|
| Wren AI | 102 | 102 | 102 | 0 |
| Zenlytic | 149 | 149 | 149 | 0 |
| Upsolve AI | 278 | 278 | 278 | 0 |
| Datost | 1 | 1 | 1 | 0 |
| Numbers Station | 72 | 72 | 72 | 0 |
| Atlas | 23 | 23 | 23 | 0 |
| Vanna AI | 46 | 46 | 46 | 0 |
| Defog | 10 | 10 | 10 | 0 |
| Dot / GetDot | 235 | 235 | 235 | 0 |
| Seek AI | 4 | 0 | 0 | 4 |
| Datyo | 81 | 81 | 81 | 0 |
| Kaelio / ktx | 174 | 174 | 174 | 0 |
| nao Labs | 106 | 106 | 106 | 0 |
| Motley / SLayer | 42 | 42 | 42 | 0 |
| Honeydew | 152 | 152 | 152 | 0 |
| Timbr | 321 | 321 | 321 | 0 |
| MINEO Manufacturing | 127 | 127 | 127 | 0 |
| oee.ai | 241 | 241 | 241 | 0 |
| Premisys | 5 | 5 | 5 | 0 |
| Zentio | 28 | 28 | 28 | 0 |
| Loukamotive / IF | 5 | 5 | 5 | 0 |

## Method

- Started from the official list of 21 competitors.
- Parsed public sitemap indexes and same-origin public links where available.
- Rendered pages in Chromium with a fresh page, a settled DOM, lazy-content wait, and full-page screenshot.
- Re-ran failed records with isolated browser workers and hard per-URL deadlines.
- Captured Datyo's marketing landing page and its public English/Chinese VitePress documentation graph as a separate 81-route inventory.
- Retried Upsolve `/demo` with a custom wait strategy; it rendered successfully.
- Probed Seek's root, robots, sitemap candidates, and sampled public paths. `www.seek.ai` returned a self-referential `301 Location: <same requested URL>`; bare `seek.ai` timed out. Those four indexed/probed URLs are marked blocked, not captured.

## Honest scope boundary

“Public page” means a page reachable without authentication from the public sitemap or rendered same-origin link graph. External consoles, desktop downloads, authenticated application screens, and third-party assets were recorded as outbound links where useful but were not misclassified as public marketing pages of the competitor.

Seek is the only unresolved origin. The agent must not infer its page copy or visual system from search snippets. Re-run the Seek probe when the origin redirect is fixed or an authorized browser session is available.

## Raw evidence locations

- [`coverage-v2.json`](/tmp/dima-competitor-research/coverage-v2.json) — one normalized metadata record per scoped URL.
- [`visual-index-v2.json`](/tmp/dima-competitor-research/visual-index-v2.json) — screenshot paths and page classifications.
- [`rendered/`](/tmp/dima-competitor-research/rendered) — initial full-page pass.
- [`retry-v2/`](/tmp/dima-competitor-research/retry-v2) — isolated retry pass.
- [`datyo-crawl-final/`](/tmp/dima-competitor-research/datyo-crawl-final) — Datyo landing/docs pass.
- [`seek-origin-block.json`](/tmp/dima-competitor-research/seek-origin-block.json) — reproducible block evidence.

