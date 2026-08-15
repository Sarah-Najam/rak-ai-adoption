/** Org and per-department targets, with each department's standing against them. */
import type { Dashboard } from "@/hooks/useDashboard";
import { STATUS_CLASS, STATUS_LABEL, fmt1, signed } from "@/lib/scoring";

export const TargetsPanel = ({ dash }: { dash: Dashboard }) => {
  const { views, targets, setTargets, setDeptTarget } = dash;
  const ranked = [...views].sort((a, b) => b.rate - a.rate);
  const atTarget = ranked.filter((v) => v.rate >= v.target).length;

  return (
    <div>
      <div className="shead"><h2>Targets &amp; benchmarking</h2></div>
      <div className="card pad">
        <div className="tset">
          <div className="b">
            <label className="eyebrow" htmlFor="t-org">Org target</label>
            <input
              id="t-org" className="mono" type="number" min={0} max={100} value={targets.org}
              onChange={(e) => setTargets({ ...targets, org: Number(e.target.value) })}
            />
          </div>
          <div className="b">
            <label className="eyebrow" htmlFor="t-qtr">This quarter</label>
            <input
              id="t-qtr" className="mono" type="number" min={0} max={100} value={targets.quarter}
              onChange={(e) => setTargets({ ...targets, quarter: Number(e.target.value) })}
            />
          </div>
          <div className="b">
            <label className="eyebrow" htmlFor="t-min">Minimum</label>
            <input
              id="t-min" className="mono" type="number" min={0} max={100} value={targets.min}
              onChange={(e) => setTargets({ ...targets, min: Number(e.target.value) })}
            />
          </div>
          <div className="b">
            <span className="eyebrow">At or above target</span>
            <div className="mono" style={{ fontSize: 19, paddingTop: 2 }}>
              {atTarget} / {ranked.length}
            </div>
          </div>
        </div>

        <div className="scrollx">
          <table>
            <thead>
              <tr>
                <th>Department</th>
                <th className="n">Rate</th>
                <th className="n">Target</th>
                <th className="n">Gap</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {ranked.map((v) => {
                const gap = v.rate - v.target;
                return (
                  <tr key={v.dept.id}>
                    <td>{v.dept.name}</td>
                    <td className="n">{fmt1(v.rate)}</td>
                    <td className="n">
                      <input
                        className="tin" type="number" min={0} max={100}
                        value={targets.byDept[v.dept.id] ?? 0}
                        onChange={(e) => setDeptTarget(v.dept.id, Number(e.target.value))}
                      />
                    </td>
                    <td className="n" style={{ color: gap >= 0 ? "#BEC8BE" : "#D28A70" }}>
                      {signed(gap)}
                    </td>
                    <td>
                      <span className={`chip ${STATUS_CLASS[v.status]}`}>{STATUS_LABEL[v.status]}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="hint">
          Set a department target to 0 to inherit the org-wide target. On track means within
          10 points. Critical means below the minimum acceptable rate.
        </div>
      </div>
    </div>
  );
};
