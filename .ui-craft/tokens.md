# dima token contract

The implementation source of truth is `src/app/globals.css`. This document records
usage intent; it does not duplicate raw values.

## Color

- `background`, `card`, `muted`: the neutral editorial surface stack.
- `foreground`, `muted-foreground`: primary and supporting text.
- `brand`: one accent for brand, provenance, focus, and the primary data series.
- `chart-*`: categorical data only. Never use a rainbow sequence for magnitude.
- `destructive`: errors and destructive states only.

Above the fold, the accent budget is three to five placements. Generated editorial
assets may contain copper warmth, but UI controls always use semantic tokens.

## Typography

- Marketing display: Playfair Display through `font-display`.
- UI and body: Plus Jakarta Sans through `font-sans`.
- Data, code, identifiers: JetBrains Mono through `font-mono`.
- Large headings use tight tracking and balanced wrapping.
- Data uses tabular numerals.

## Shape and elevation

- Controls use the small/medium radius steps.
- Cards use `rounded-lg` or `rounded-xl`.
- Editorial image frames may use a slightly larger radius.
- Use layered token shadows; no glow as an affordance.

## Spacing

Major marketing sections use 4.5–6rem mobile and 6rem desktop spacing.
Within-section spacing remains smaller than between-section spacing.

## Motion

- interaction: 100–150ms
- small reveal: 180–220ms
- panel entrance: 240–300ms
- hero choreography: no more than 400ms
- default easing: cubic-bezier(0.22, 1, 0.36, 1)
- animate transform and opacity only
- reduced motion resolves immediately to the final state
