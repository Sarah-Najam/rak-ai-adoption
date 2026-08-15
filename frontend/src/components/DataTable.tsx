/** The eight indicator scores per department, as loaded from the survey. */
import type { Dashboard } from "@/hooks/useDashboard";
import { INDICATOR_META, fmt1 } from "@/lib/scoring";

const SHORT: Record<string, string> = {
  users: "Users", freq: "Freq", train: "Train", flow: "Flow",
  tasks: "Tasks", cover: "Cover", prof: "Prof", comp: "Safe",
};

export const DataTable = ({ dash }: { dash: Dashboard }) => {
  const { views, filters } = dash;

  return (
    <div>
      <div className="shead">
        <h2>Departments &amp; source data</h2>
        <p>Scored from the survey responses</p>
      </div>
      <div className="card pad">
        <div className="scrollx">
          <table>
            <thead>
              <tr>
                <th>Department</th>
                <th className="n">Staff</th>
                {INDICATOR_META.map((m) => (
                  <th className="n" key={m.key} title={m.label}>{SHORT[m.key]}</th>
                ))}
                <th className="n">Rate</th>
              </tr>
            </thead>
            <tbody>
              {views.map((v) => {
                const snapshot = v.dept.byWave[filters.wave];
                if (!snapshot) return null;
                return (
                  <tr key={v.dept.id}>
                    <td>{v.dept.name}</td>
                    <td className="n">{snapshot.staff}</td>
                    {INDICATOR_META.map((m) => (
                      <td className="n" key={m.key}>{Math.round(snapshot.metrics[m.key])}</td>
                    ))}
                    <td className="n" style={{ color: v.band.colour, fontWeight: 600 }}>
                      {fmt1(v.rate)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="hint">
          All eight indicator columns are 0 to 100 scores, produced by the scoring service from
          the raw survey responses.
        </div>
      </div>
    </div>
  );
};
