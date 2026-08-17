/** The eight indicator scores per department, as loaded from the survey. */
import type { Dashboard } from "@/hooks/useDashboard";
import { INDICATOR_META, fmt1 } from "@/lib/scoring";
import { Info } from "@/components/Info";

/** Short column headings, since eight full labels will not fit across a table. */
const SHORT: Record<string, string> = {
  users: "Users", freq: "Freq", train: "Train", flow: "Flow",
  tasks: "Tasks", cover: "Cover", prof: "Prof", comp: "Safe",
};

const EXPLAIN: Record<string, string> = {
  users: "Share of staff who used any AI tool for work in the last 30 days.",
  freq: "Days per week multiplied by sessions per day, scored against a target of 5 sessions a week.",
  train: "Share of staff who have completed any AI training.",
  flow: "How often AI is part of the actual job, on a six-point scale from never to every working day.",
  tasks: "AI-assisted tasks per person per month, scored against a target of 20.",
  cover: "Of the tasks a person repeats every week, the share that now use AI.",
  prof: "Average score on the knowledge check, answered by everyone including people who do not use AI.",
  comp: "Company accounts used rather than personal ones, with no sensitive data pasted into personal accounts.",
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
                <th className="n">
                  Staff
                  <Info label="About the staff column">
                    Total headcount from the HR file, not the number of people who
                    answered the survey. Response rate is measured against this.
                  </Info>
                </th>
                {INDICATOR_META.map((m) => (
                  <th className="n" key={m.key}>
                    {SHORT[m.key]}
                    <Info label={`About ${m.label}`}>
                      <b>{m.label}</b>
                      <br />
                      {EXPLAIN[m.key]}
                    </Info>
                  </th>
                ))}
                <th className="n">
                  Rate
                  <Info label="About the adoption rate">
                    The eight scores combined using the weights in the scoring model.
                    Change a weight and this changes with it.
                  </Info>
                </th>
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
          the raw survey responses. Hover any heading for what it measures.
        </div>
      </div>
    </div>
  );
};