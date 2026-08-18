/** Everything known about one department, opened by clicking a tile. */
import { useEffect } from "react";

import type { Dashboard } from "@/hooks/useDashboard";
import {
  INDICATOR_META, LEVELS, STATUS_CLASS, STATUS_LABEL,
  adjustedMetrics, clamp, fmt0, fmt1, rateInWave, signed,
} from "@/lib/scoring";

export const DetailDrawer = ({ dash }: { dash: Dashboard }) => {
  const { selected, setSelected, filters, waves, weights } = dash;

  // Escape closes the drawer. Expected of anything that covers the page.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setSelected(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setSelected]);

  const open = selected !== null;
  const snapshot = selected?.dept.byWave[filters.wave];
  const levelLabel = LEVELS.find((l) => l.key === filters.level)?.label ?? "All levels";

  return (
    <>
      <div className={`scrim ${open ? "on" : ""}`} onClick={() => setSelected(null)} />
      <aside className={`drawer ${open ? "on" : ""}`} aria-hidden={!open} aria-label="Department detail">
        {selected && snapshot && (
          <>
            <div className="dh">
              <button className="dx" type="button" aria-label="Close" onClick={() => setSelected(null)}>×</button>
              <span className="eyebrow">{selected.dept.function}</span>
              <h3>{selected.dept.name}</h3>

              <div className="dsc">
                <span className="v mono" style={{ color: selected.band.colour }}>
                  {fmt1(selected.rate)}<em>%</em>
                </span>
                <span style={{ paddingBottom: 8 }}>
                  <span className={`chip ${STATUS_CLASS[selected.status]}`}>
                    {STATUS_LABEL[selected.status]}
                  </span>
                  <span className="mono" style={{ fontSize: 11, color: "rgba(234,241,244,.5)", marginLeft: 9 }}>
                    {selected.band.name} · target {selected.target}%
                  </span>
                </span>
              </div>

              {selected.previousRate === null ? (
                <div className="mono" style={{ marginTop: 10, fontSize: 12.5, color: "rgba(234,241,244,.5)" }}>
                  Baseline wave
                </div>
              ) : (
                <div className={`mono ${selected.rate >= selected.previousRate ? "up" : "down"}`}
                     style={{ marginTop: 10, fontSize: 12.5 }}>
                  {selected.rate >= selected.previousRate ? "▲ " : "▼ "}
                  {signed(selected.rate - selected.previousRate)} points vs {waves[filters.wave - 1]}
                </div>
              )}
            </div>

            <div className="db">
              <div className="kv">
                <div><div className="k">Adoption rate</div>
                  <div className="v">{fmt1(selected.rate)}% <small>{selected.band.name}</small></div></div>
                <div><div className="k">Active AI users</div>
                  <div className="v">{selected.active} <small>of {selected.staff}</small></div></div>
                <div><div className="k">Total employees</div>
                  <div className="v">{snapshot.staff} <small>{snapshot.mix.leadership} lead · {snapshot.mix.manager} mgr</small></div></div>
                <div><div className="k">Training completed</div>
                  <div className="v">{fmt0(snapshot.metrics.train)}% <small>of staff</small></div></div>
                <div><div className="k">Usage frequency</div>
                  <div className="v">{snapshot.sessions.toFixed(1)} <small>sessions / user / week</small></div></div>
                <div><div className="k">AI use cases</div>
                  <div className="v">{snapshot.cases} <small>documented</small></div></div>
                <div><div className="k">AI-enabled solutions</div>
                  <div className="v">{snapshot.aiSolutions} <small>agents + automations</small></div></div>
                <div><div className="k">Personal use</div>
                  <div className="v">{snapshot.aiSolutionsPersonal} <small>included in score</small></div></div>
              </div>

              <div className="blk">
                <h4>Indicator breakdown</h4>
                {(() => {
                  const adjusted = adjustedMetrics(snapshot.metrics, filters.level);
                  return INDICATOR_META.map((meta) => (
                    <div className="bl" key={meta.key}>
                      <span>{meta.label}</span>
                      <span className="tr"><i style={{ width: `${clamp(adjusted[meta.key])}%` }} /></span>
                      <span className="vv">{fmt0(adjusted[meta.key])}</span>
                    </div>
                  ));
                })()}
                <div className="hint">
                  Each indicator is scored 0 to 100, then combined using the weights in the
                  scoring model. Showing {levelLabel.toLowerCase()}.
                </div>
              </div>

              <div className="blk">
                <h4>Most-used AI tools</h4>
                <div className="tags">
                  {snapshot.tools.length === 0 && <span className="hint">Not recorded</span>}
                  {snapshot.tools.map(([name, share]) => (
                    <span className="tg" key={name}>{name}<b>{share}%</b></span>
                  ))}
                </div>
              </div>

              <div className="blk">
                <h4>AI-enabled processes</h4>
                <ul className="pl">
                  {snapshot.processes.length === 0 && <li>Not recorded</li>}
                  {snapshot.processes.map((p) => <li key={p}>{p}</li>)}
                </ul>
              </div>

              <div className="blk">
                <h4>Adoption by wave</h4>
                <div style={{ display: "flex", gap: 8 }}>
                  {waves.map((label, index) => {
                    const rate = rateInWave(selected.dept, index, weights, filters.level);
                    return (
                      <span key={label} style={{ flex: 1, textAlign: "center", padding: "0 4px" }}>
                        <span className="eyebrow" style={{ display: "block" }}>{label}</span>
                        <span className="mono" style={{ fontSize: 15 }}>
                          {rate === null ? "–" : `${fmt1(rate)}%`}
                        </span>
                      </span>
                    );
                  })}
                </div>
              </div>

              <div className="note">
                <h4 style={{ color: "#D28A70" }}>Key gap</h4>
                <div style={{ fontSize: 12.5 }}>{snapshot.gap}</div>
              </div>
              <div className="note opp">
                <h4>Opportunity</h4>
                <div style={{ fontSize: 12.5 }}>{snapshot.opportunity}</div>
              </div>
            </div>
          </>
        )}
      </aside>
    </>
  );
};
