/**
 * The weight sliders.
 *
 * This is what turns the dashboard from a report into a tool: leadership can
 * argue about what adoption means and watch the ranking change while they do.
 */
import type { Dashboard } from "@/hooks/useDashboard";
import { INDICATORS, INDICATOR_META } from "@/lib/scoring";

export const ScoringModel = ({ dash }: { dash: Dashboard }) => {
  const { weights, setWeight, resetWeights } = dash;
  const total = INDICATORS.reduce((sum, k) => sum + weights[k], 0);

  return (
    <div>
      <div className="shead"><h2>Scoring model</h2></div>
      <div className="card pad">
        <p style={{ margin: "0 0 12px", fontSize: 12.5, color: "var(--txt-3)" }}>
          Adoption is a weighted average of eight indicators, each scored 0 to 100.
          Drag a slider to change how much it counts.
        </p>

        {INDICATOR_META.map((meta) => (
          <div className="wr" key={meta.key}>
            <span className="l">
              {meta.label}
              <small>{meta.note}</small>
            </span>
            <input
              type="range" min={0} max={40} value={weights[meta.key]}
              aria-label={`Weight for ${meta.label}`}
              onChange={(e) => setWeight(meta.key, Number(e.target.value))}
            />
            <output className="mono">{weights[meta.key]}%</output>
          </div>
        ))}

        <div className="mono" style={{ textAlign: "right", paddingTop: 11, fontSize: 12, color: "var(--txt-3)" }}>
          Total weight {total}%
        </div>

     

        <button className="btn" style={{ marginTop: 14 }} type="button" onClick={resetWeights}>
          Reset default weights
        </button>
      </div>
    </div>
  );
};
