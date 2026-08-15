/** The seven figures leadership reads first. */
import type { Dashboard } from "@/hooks/useDashboard";
import { fmt1, signed } from "@/lib/scoring";

export const ExecutiveSummary = ({ dash }: { dash: Dashboard }) => {
  const { summary, targets, filters, waves } = dash;
  const shortfall = targets.org - summary.rate;

  return (
    <section id="s1">
      <div className="shead">
        <h2>Executive summary</h2>
        <p>
          {summary.departments} departments · {summary.counted} employees · {waves[filters.wave]}
        </p>
      </div>

      <div className="hero">
        <div className="card hero-main">
          <span className="badge">
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: summary.band.colour,
                display: "inline-block",
              }}
            />
            Organisation maturity: {summary.band.name}
          </span>
          <span className="eyebrow" style={{ display: "block" }}>
            Organisation-wide AI adoption rate
          </span>

          <div className="hero-fig">
            <div className="big mono">
              {fmt1(summary.rate)}
              <i>%</i>
            </div>
            <div style={{ paddingBottom: 10 }}>
              {/* On the first wave there is nothing to compare against, and
                  showing a change of zero would imply adoption stood still. */}
              {summary.delta === null ? (
                <>
                  <div className="mono" style={{ fontSize: 16 }}>Baseline</div>
                  <div style={{ fontSize: 11.5, color: "var(--txt-3)" }}>
                    First survey wave, nothing to compare against yet
                  </div>
                </>
              ) : (
                <>
                  <div className={`mono ${summary.delta >= 0 ? "up" : "down"}`} style={{ fontSize: 16 }}>
                    {summary.delta >= 0 ? "▲ " : "▼ "}
                    {signed(summary.delta)} pts
                  </div>
                  <div style={{ fontSize: 11.5, color: "var(--txt-3)" }}>
                    vs {waves[filters.wave - 1]}
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="track">
            <i style={{ width: `${summary.rate}%` }} />
            <b style={{ left: `calc(${targets.org}% - 1px)` }} />
          </div>
          <div style={{ fontSize: 12, color: "var(--txt-3)" }}>
            Employee-weighted across {summary.departments} departments ·{" "}
            {shortfall <= 0
              ? `above the ${targets.org}% target`
              : `${fmt1(shortfall)} points below the ${targets.org}% target`}
          </div>
        </div>

        <div className="kgrid">
          <div className="card kcell">
            <span className="eyebrow">Departments assessed</span>
            <div className="v mono">{summary.departments}</div>
            <div className="s">
              {summary.departments === summary.totalDepartments
                ? "All departments in scope"
                : `Filtered from ${summary.totalDepartments} departments`}
            </div>
          </div>

          <div className="card kcell">
            <span className="eyebrow">Employees assessed</span>
            <div className="v mono">{summary.counted}</div>
            <div className="s">
              {filters.users === "all"
                ? "Headcount in scope"
                : filters.users === "active"
                  ? "Active AI users only"
                  : "Not yet using AI"}
            </div>
          </div>

          <div className="card kcell">
            <span className="eyebrow">Actively using AI</span>
            <div className="v mono">
              {fmt1(summary.activePct)}
              <i>%</i>
            </div>
            <div className="s">
              {summary.active} of {summary.staff} employees used an AI tool in the last 30 days
            </div>
          </div>

          <div className="card kcell">
            <span className="eyebrow">Highest and lowest</span>
            {summary.highest && (
              <>
                <div className="nm">▲ {summary.highest.dept.name}</div>
                <div className="s">
                  {fmt1(summary.highest.rate)}% · {summary.highest.band.name}
                </div>
              </>
            )}
            {summary.lowest && (
              <>
                <div className="nm" style={{ marginTop: 9, color: "#D28A70" }}>
                  ▼ {summary.lowest.dept.name}
                </div>
                <div className="s">
                  {fmt1(summary.lowest.rate)}% · {summary.lowest.band.name}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};
