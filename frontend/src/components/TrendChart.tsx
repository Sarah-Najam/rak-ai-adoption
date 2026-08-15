/**
 * Adoption over time.
 *
 * Each point is one survey wave. Nothing is interpolated and nothing is
 * generated: with a single wave loaded the chart says so rather than drawing a
 * line, because a smooth rising curve that never happened, sitting next to real
 * numbers, is the fastest way to lose an audience's trust.
 *
 * Departments missing from a wave leave a gap in their line instead of dropping
 * to zero. Zero would read as "adoption collapsed" when the truth is "we did
 * not measure it".
 */

import { useEffect, useRef, useState } from "react";

import type { Dashboard } from "@/hooks/useDashboard";
import { fmt1, rateInWave } from "@/lib/scoring";

const LINE_COLOURS = ["#A5C8D2", "#BEC8BE", "#AF5F46", "#FFFFFF"];
const HEIGHT = 340;
const MARGIN = { top: 18, right: 18, bottom: 36, left: 40 };

interface Series {
  name: string;
  values: (number | null)[];
  colour: string;
}

/** Build one polyline per unbroken run, so gaps stay gaps. */
const segments = (
  values: (number | null)[],
  x: (i: number) => number,
  y: (v: number) => number,
): string[] => {
  const runs: string[] = [];
  let current: string[] = [];
  values.forEach((value, index) => {
    if (value === null) {
      if (current.length > 1) runs.push(current.join(" "));
      current = [];
    } else {
      current.push(`${x(index)},${y(value)}`);
    }
  });
  if (current.length > 1) runs.push(current.join(" "));
  return runs;
};

export const TrendChart = ({ dash }: { dash: Dashboard }) => {
  const { waves, visible, weights, targets, filters, compare, toggleCompare } = dash;
  const boxRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(720);
  const [hover, setHover] = useState<number | null>(null);

  useEffect(() => {
    const node = boxRef.current;
    if (!node) return undefined;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(320, entry.contentRect.width)));
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const inner = {
    w: width - MARGIN.left - MARGIN.right,
    h: HEIGHT - MARGIN.top - MARGIN.bottom,
  };
  const x = (i: number) =>
    MARGIN.left + (waves.length < 2 ? inner.w / 2 : i * (inner.w / (waves.length - 1)));
  const y = (v: number) => MARGIN.top + inner.h - (v / 100) * inner.h;

  const orgValues: (number | null)[] = waves.map((_, index) => {
    let numerator = 0;
    let denominator = 0;
    visible.forEach((d) => {
      const rate = rateInWave(d, index, weights, filters.level);
      const snapshot = d.byWave[index];
      if (rate === null || !snapshot) return;
      const staff = filters.level === "all" ? snapshot.staff : snapshot.mix[filters.level];
      numerator += rate * staff;
      denominator += staff;
    });
    return denominator > 0 ? numerator / denominator : null;
  });

  const series: Series[] = compare
    .map((id, i) => {
      const dept = visible.find((d) => d.id === id);
      if (!dept) return null;
      return {
        name: dept.name,
        colour: LINE_COLOURS[i % LINE_COLOURS.length],
        values: waves.map((_, index) => rateInWave(dept, index, weights, filters.level)),
      };
    })
    .filter((s): s is Series => s !== null);

  return (
    <section id="s4">
      <div className="shead">
        <h2>Adoption trends</h2>
        <p>Each point is one survey wave</p>
      </div>

      <div className="card pad">
        <div className="chips">
          <span style={{ fontSize: 11.5, color: "var(--txt-3)", marginRight: 4 }}>Compare</span>
          {visible.map((d) => {
            const index = compare.indexOf(d.id);
            const on = index >= 0;
            return (
              <button
                key={d.id}
                type="button"
                aria-pressed={on}
                style={on ? { color: LINE_COLOURS[index % LINE_COLOURS.length] } : undefined}
                onClick={() => toggleCompare(d.id)}
              >
                <i />
                {d.name}
              </button>
            );
          })}
        </div>

        <div className="cbox" ref={boxRef}>
          <svg width="100%" height={HEIGHT} viewBox={`0 0 ${width} ${HEIGHT}`} role="img"
               aria-label="AI adoption rate by survey wave">
            <defs>
              <linearGradient id="orgFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#A5C8D2" stopOpacity="0.28" />
                <stop offset="100%" stopColor="#A5C8D2" stopOpacity="0" />
              </linearGradient>
            </defs>

            {[0, 20, 40, 60, 80, 100].map((g) => (
              <g key={g}>
                <line x1={MARGIN.left} y1={y(g)} x2={width - MARGIN.right} y2={y(g)}
                      stroke="rgba(165,200,210,.12)" />
                <text x={MARGIN.left - 9} y={y(g) + 4} textAnchor="end" fontSize="10"
                      fill="rgba(234,241,244,.38)">{g}</text>
              </g>
            ))}

            {waves.map((label, i) => (
              <text key={label} x={x(i)} y={HEIGHT - 12} textAnchor="middle" fontSize="10"
                    fill="rgba(234,241,244,.38)">{label}</text>
            ))}

            <line x1={MARGIN.left} y1={y(targets.org)} x2={width - MARGIN.right} y2={y(targets.org)}
                  stroke="#BEC8BE" strokeWidth="1.4" strokeDasharray="5 4" />
            <text x={width - MARGIN.right} y={y(targets.org) - 7} textAnchor="end" fontSize="9.5"
                  fill="#BEC8BE" letterSpacing="1">TARGET {targets.org}%</text>

            {orgValues.filter((v) => v !== null).length > 1 && (
              <polygon
                fill="url(#orgFill)"
                points={`${MARGIN.left},${y(0)} ${orgValues
                  .map((v, i) => (v === null ? null : `${x(i)},${y(v)}`))
                  .filter(Boolean)
                  .join(" ")} ${x(waves.length - 1)},${y(0)}`}
              />
            )}

            {segments(orgValues, x, y).map((points, i) => (
              <polyline key={`org-${i}`} points={points} fill="none" stroke="#A5C8D2"
                        strokeWidth="2.6" strokeLinejoin="round" strokeLinecap="round" />
            ))}
            {orgValues.map((v, i) =>
              v === null ? null : (
                <circle key={`orgpt-${i}`} cx={x(i)} cy={y(v)} r="4" fill="#051C2C"
                        stroke="#A5C8D2" strokeWidth="2.4" />
              ),
            )}

            {series.map((s) => (
              <g key={s.name}>
                {segments(s.values, x, y).map((points, i) => (
                  <polyline key={i} points={points} fill="none" stroke={s.colour}
                            strokeWidth="1.7" strokeLinejoin="round" opacity="0.9" />
                ))}
                {s.values.map((v, i) =>
                  v === null ? null : <circle key={i} cx={x(i)} cy={y(v)} r="2.6" fill={s.colour} />,
                )}
              </g>
            ))}

            {waves.length < 2 && (
              <text x={MARGIN.left + inner.w / 2} y={MARGIN.top + inner.h / 2} textAnchor="middle"
                    fontSize="12.5" fill="rgba(234,241,244,.45)">
                A trend line appears once the second survey wave is loaded
              </text>
            )}

            <rect
              x={MARGIN.left} y={MARGIN.top} width={inner.w} height={inner.h} fill="transparent"
              onMouseMove={(e) => {
                const box = (e.target as SVGRectElement).ownerSVGElement?.getBoundingClientRect();
                if (!box) return;
                const px = (e.clientX - box.left) * (width / box.width);
                const step = inner.w / Math.max(1, waves.length - 1);
                setHover(Math.max(0, Math.min(waves.length - 1, Math.round((px - MARGIN.left) / step))));
              }}
              onMouseLeave={() => setHover(null)}
            />
          </svg>

          {hover !== null && (
            <div className="ctip" style={{ opacity: 1, left: Math.max(0, x(hover) - 85) }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>{waves[hover]}</div>
              <div className="r" style={{ color: "#A5C8D2" }}>
                <span>Organisation</span>
                <b>{orgValues[hover] === null ? "no data" : `${fmt1(orgValues[hover]!)}%`}</b>
              </div>
              {series.map((s) => (
                <div className="r" key={s.name} style={{ color: s.colour }}>
                  <span>{s.name}</span>
                  <b>{s.values[hover] === null ? "no data" : `${fmt1(s.values[hover]!)}%`}</b>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
