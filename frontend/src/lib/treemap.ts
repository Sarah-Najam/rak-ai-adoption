/**
 * Squarified treemap layout.
 *
 * A naive treemap slices the rectangle one way each time and produces long thin
 * slivers that are impossible to compare by eye. The squarified algorithm
 * (Bruls, Huizing and van Wijk, 2000) instead builds rows and keeps adding to a
 * row while the worst aspect ratio in it improves, which keeps tiles close to
 * square. That matters here because the whole point of the grid is that area is
 * readable at a glance.
 */

export interface TreemapItem {
  id: string;
  value: number;
}

export interface TreemapTile extends TreemapItem {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface Sized extends TreemapItem {
  area: number;
}

/** Worst aspect ratio in a row. Lower is squarer. */
const worstRatio = (row: Sized[], rowArea: number, side: number): number => {
  let min = Infinity;
  let max = -Infinity;
  row.forEach((c) => {
    if (c.area < min) min = c.area;
    if (c.area > max) max = c.area;
  });
  const s2 = side * side;
  const a2 = rowArea * rowArea;
  if (min <= 0 || a2 <= 0) return Infinity;
  return Math.max((s2 * max) / a2, a2 / (s2 * min));
};

const squarify = (items: Sized[], rect: Rect, out: TreemapTile[]): void => {
  if (items.length === 0 || rect.w <= 0.5 || rect.h <= 0.5) return;

  const side = Math.min(rect.w, rect.h);
  const row: Sized[] = [];
  let rowArea = 0;
  let best = Infinity;
  let i = 0;

  // Keep adding tiles while the row gets squarer, then stop.
  while (i < items.length) {
    const candidate = items[i];
    const nextArea = rowArea + candidate.area;
    const ratio = worstRatio([...row, candidate], nextArea, side);
    if (row.length === 0 || ratio <= best) {
      row.push(candidate);
      rowArea = nextArea;
      best = ratio;
      i += 1;
    } else break;
  }

  const rest = items.slice(row.length);

  if (rect.w >= rect.h) {
    // Lay the row down the left edge, then recurse into what is left.
    const colWidth = rowArea / rect.h;
    let y = rect.y;
    row.forEach((c) => {
      const h = c.area / colWidth;
      out.push({ ...c, x: rect.x, y, w: colWidth, h });
      y += h;
    });
    squarify(rest, { x: rect.x + colWidth, y: rect.y, w: rect.w - colWidth, h: rect.h }, out);
  } else {
    const rowHeight = rowArea / rect.w;
    let x = rect.x;
    row.forEach((c) => {
      const w = c.area / rowHeight;
      out.push({ ...c, x, y: rect.y, w, h: rowHeight });
      x += w;
    });
    squarify(rest, { x: rect.x, y: rect.y + rowHeight, w: rect.w, h: rect.h - rowHeight }, out);
  }
};

/**
 * Lay out items in a box. Value maps to area, so a department at 90 takes
 * roughly three times the space of one at 30.
 */
export const layoutTreemap = (
  items: TreemapItem[],
  width: number,
  height: number,
): TreemapTile[] => {
  if (width <= 0 || height <= 0 || items.length === 0) return [];

  // A department at 0 would otherwise vanish entirely and look like missing data.
  const sorted = items
    .map((it) => ({ ...it, value: Math.max(it.value, 1) }))
    .sort((a, b) => b.value - a.value);

  const total = sorted.reduce((sum, c) => sum + c.value, 0);
  const scale = (width * height) / total;
  const sized: Sized[] = sorted.map((c) => ({ ...c, area: c.value * scale }));

  const out: TreemapTile[] = [];
  squarify(sized, { x: 0, y: 0, w: width, h: height }, out);
  return out;
};
