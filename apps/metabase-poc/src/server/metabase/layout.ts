// Dashboard grid layout (engine grid: 24 columns). Pure, unit-tested.
//
// Our UI edits order and width only; positions are recomputed by flowing the
// widgets left-to-right into rows, so the engine's grid stays valid.

export const GRID_COLS = 24;
export type Width = "kpi" | "half" | "full";

const SPAN: Record<Width, number> = { kpi: 6, half: 12, full: 24 };
const HEIGHT: Record<Width, number> = { kpi: 3, half: 6, full: 6 };

export interface Placed {
  row: number;
  col: number;
  size_x: number;
  size_y: number;
}

export function widthOf(sizeX: number, display: string): Width {
  if (display === "scalar" || display === "smartscalar") return "kpi";
  return sizeX >= GRID_COLS ? "full" : "half";
}

/** Flow widgets into rows; a row's height is its tallest widget. */
export function flow(widths: Width[]): Placed[] {
  const out: Placed[] = [];
  let row = 0;
  let col = 0;
  let rowHeight = 0;
  for (const w of widths) {
    const span = SPAN[w];
    if (col + span > GRID_COLS) {
      row += rowHeight;
      col = 0;
      rowHeight = 0;
    }
    out.push({ row, col, size_x: span, size_y: HEIGHT[w] });
    col += span;
    rowHeight = Math.max(rowHeight, HEIGHT[w]);
  }
  return out;
}
