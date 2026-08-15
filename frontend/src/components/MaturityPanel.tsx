/** How many departments sit in each maturity band. */
import type { Dashboard } from "@/hooks/useDashboard";
import { BANDS, fmt0 } from "@/lib/scoring";

export const MaturityPanel = ({ dash }: { dash: Dashboard }) => {
  const { views } = dash;
  const total = Math.max(1, views.length);

  return (
    <div>
      <div className="shead"><h2>Adoption maturity</h2></div>
      <div className="card pad">
        <div className="matbar">
          {BANDS.map((band) => {
            const count = views.filter((v) => v.band.name === band.name).length;
            if (count === 0) return null;
            return (
              <div
                key={band.name}
                style={{ flex: count, background: band.colour }}
                title={`${band.name}: ${count}`}
              />
            );
          })}
        </div>

        {BANDS.map((band) => {
          const inBand = views.filter((v) => v.band.name === band.name);
          return (
            <div className="mrow" key={band.name}>
              <span className="sw" style={{ background: band.colour }} />
              <span className="nm">
                {band.name}
                <em>{band.low}-{band.high}%</em>
                <div>{inBand.map((v) => v.dept.name).join(", ") || band.description}</div>
              </span>
              <span className="c">{inBand.length}</span>
              <span className="p">{fmt0((inBand.length / total) * 100)}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
