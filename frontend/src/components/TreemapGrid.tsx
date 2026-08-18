/**
 * The department adoption grid.
 *
 * Box area is proportional to the adoption rate, so the question leadership
 * actually asks, which departments are ahead and which are lagging, is answered
 * by size before anyone reads a number. Colour carries the maturity band.
 *
 * The layout is measured from the DOM rather than assumed, because the treemap
 * has to be recalculated whenever the container resizes. A ResizeObserver is
 * used instead of a window resize listener so it also reacts to the drawer
 * opening, the filter row wrapping onto two lines, or a phone rotating.
 */

import { useEffect, useLayoutEffect, useRef, useState } from "react";

import type { Dashboard, DepartmentView } from "@/hooks/useDashboard";
import { BANDS, STATUS_LABEL, fmt1, signed } from "@/lib/scoring";
import { layoutTreemap } from "@/lib/treemap";

const GAP = 4;

interface Size {
  width: number;
  height: number;
}

interface TooltipState {
  view: DepartmentView;
  x: number;
  y: number;
}

const Tooltip = ({ state, wave }: { state: TooltipState | null; wave: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [offset, setOffset] = useState({ left: 0, top: 0 });

  // Flip the tooltip when it would run off the edge of the window, which is
  // most of the time for the departments on the right of the grid.
  useLayoutEffect(() => {
    if (!state || !ref.current) return;
    const box = ref.current.getBoundingClientRect();
    const pad = 16;
    let left = state.x + pad;
    let top = state.y + pad;
    if (left + box.width > window.innerWidth - 10) left = state.x - box.width - pad;
    if (top + box.height > window.innerHeight - 10) top = state.y - box.height - pad;
    setOffset({ left: Math.max(8, left), top: Math.max(8, top) });
  }, [state]);

  if (!state) return null;
  const { view } = state;
  const snapshot = view.dept.byWave[0];

  return (
    <div id="tip" ref={ref} role="tooltip" style={{ opacity: 1, left: offset.left, top: offset.top }}>
      <h4>{view.dept.name}</h4>
      <div className="tr"><span>Adoption rate</span><b>{fmt1(view.rate)}%</b></div>
      <div className="tr"><span>Maturity</span><b>{view.band.name}</b></div>
      <div className="tr"><span>Target</span><b>{view.target}% · {STATUS_LABEL[view.status]}</b></div>
      <div className="tr">
        <span>vs previous wave</span>
        <b>{view.previousRate === null ? "baseline" : `${signed(view.rate - view.previousRate)} pts`}</b>
      </div>
      <div className="tr"><span>Active users</span><b>{view.active} of {view.staff}</b></div>
      <div className="tf" style={{ marginTop: 4, marginBottom: -2 }}>AI Solutions Development</div>
      <div className="tr"><span>AI agents built</span><b>{snapshot?.aiAgentsCount ?? 0}</b></div>
      <div className="tr" style={{ paddingLeft: 14, opacity: 0.75 }}><span>of which, personal use</span><b>{snapshot?.aiAgentsPersonal ?? 0}</b></div>
      <div className="tr"><span>Processes automated</span><b>{snapshot?.aiAutomationsCount ?? 0}</b></div>
      <div className="tr" style={{ paddingLeft: 14, opacity: 0.75 }}><span>of which, personal use</span><b>{snapshot?.aiAutomationsPersonal ?? 0}</b></div>     
      {snapshot && (
        <div className="tr">
          <span>Sessions / user / week</span>
          <b>{snapshot.sessions.toFixed(1)}</b>
        </div>
      )}
      <div className="tf">{view.dept.function} · {wave}</div>
    </div>
  );
};

export const TreemapGrid = ({ dash }: { dash: Dashboard }) => {
  const { views, setSelected, selected, waves, filters } = dash;
  const stageRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<Size>({ width: 0, height: 0 });
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  useEffect(() => {
    const node = stageRef.current;
    if (!node) return undefined;
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setSize({ width, height });
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const tiles = layoutTreemap(
    views.map((v) => ({ id: v.dept.id, value: v.rate })),
    size.width,
    size.height,
  );
  const byId = new Map(views.map((v) => [v.dept.id, v]));

  return (
    <section id="s2">
      <div className="shead">
        <h2>Department adoption grid</h2>
        <p>Box size is the AI adoption rate. Colour is the maturity band.</p>
      </div>

      <div className="card gridwrap">
        <div className="gbar">
          <div className="legend">
            {BANDS.map((band) => {
              const count = views.filter((v) => v.band.name === band.name).length;
              return (
                <span className="lg" key={band.name}>
                  <span className="sw" style={{ background: band.colour }} />
                  <b>{band.name}</b>
                  <span>{band.low}-{band.high}% · {count}</span>
                </span>
              );
            })}
          </div>
        </div>

        <div id="stage" ref={stageRef}>
          <div id="board">
            {views.length === 0 && (
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  display: "grid",
                  placeItems: "center",
                  color: "var(--txt-3)",
                  fontSize: 13,
                }}
              >
                No departments match these filters.
              </div>
            )}

            {tiles.map((tile) => {
              const view = byId.get(tile.id);
              if (!view) return null;
              const width = Math.max(tile.w - GAP, 2);
              const height = Math.max(tile.h - GAP, 2);

              // Small tiles cannot hold a label without becoming unreadable, so
              // detail is added only as space allows.
              const large = width > 150 && height > 112;
              const medium = width > 98 && height > 66;
              const valueSize = large ? 32 : medium ? 23 : Math.max(12, Math.min(18, width / 4.6));

              return (
                <button
                  key={tile.id}
                  type="button"
                  className="tile"
                  data-sel={selected?.dept.id === view.dept.id ? "1" : undefined}
                  style={{ left: tile.x, top: tile.y, width, height }}
                  aria-label={`${view.dept.name}, adoption ${fmt1(view.rate)} percent, ${view.band.name} maturity`}
                  onClick={() => setSelected(view.dept.id)}
                  onMouseEnter={(e) => setTooltip({ view, x: e.clientX, y: e.clientY })}
                  onMouseMove={(e) => setTooltip({ view, x: e.clientX, y: e.clientY })}
                  onMouseLeave={() => setTooltip(null)}
                  onBlur={() => setTooltip(null)}
                >
                  <span
                    className={`top ${view.band.darkText ? "dark-txt" : "light-txt"}`}
                    style={{ background: view.band.colour }}
                  >
                    <span>{medium && <span className="t-name">{view.dept.name}</span>}</span>
                    <span>
                      <span className="t-val" style={{ fontSize: valueSize }}>
                        {fmt1(view.rate)}
                        <em>%</em>
                      </span>
                      {large && (
                        <span className="t-meta">
                          {view.band.name} · {view.staff} staff · {view.active} active
                        </span>
                      )}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="ghint">
          <span>Hover a department for a quick read</span>
          <span>Click any box to open the full drill-down</span>
        </div>
      </div>

      <Tooltip state={tooltip} wave={waves[filters.wave] ?? ""} />
    </section>
  );
};
