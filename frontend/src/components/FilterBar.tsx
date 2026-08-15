/** Every filter the dashboard supports, in one sticky row. */
import type { Dashboard } from "@/hooks/useDashboard";
import type { LevelKey } from "@/lib/scoring";
import { BANDS, LEVELS } from "@/lib/scoring";

interface Props {
  dash: Dashboard;
}

export const FilterBar = ({ dash }: Props) => {
  const { filters, setFilter, resetFilters, options, waves, departments } = dash;

  return (
    <div className="filters">
      <div className="filters-in">
        <div className="f">
          <label htmlFor="f-dept">Department</label>
          <select
            id="f-dept"
            value={filters.department}
            onChange={(e) => setFilter("department", e.target.value)}
          >
            <option value="all">All departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>

        <div className="f">
          <label htmlFor="f-wave">Wave</label>
          <select
            id="f-wave"
            value={filters.wave}
            onChange={(e) => setFilter("wave", Number(e.target.value))}
          >
            {waves.map((label, i) => (
              <option key={label} value={i}>{label}</option>
            ))}
          </select>
        </div>

        <div className="f">
          <label htmlFor="f-fn">Function</label>
          <select id="f-fn" value={filters.fn} onChange={(e) => setFilter("fn", e.target.value)}>
            <option value="all">All functions</option>
            {options.functions.map((fn) => (
              <option key={fn} value={fn}>{fn}</option>
            ))}
          </select>
        </div>

        <div className="f">
          <label htmlFor="f-level">Employee level</label>
          <select
            id="f-level"
            value={filters.level}
            onChange={(e) => setFilter("level", e.target.value as LevelKey)}
          >
            {LEVELS.map((l) => (
              <option key={l.key} value={l.key}>{l.label}</option>
            ))}
          </select>
        </div>

        <div className="f">
          <label htmlFor="f-tool">AI tool</label>
          <select id="f-tool" value={filters.tool} onChange={(e) => setFilter("tool", e.target.value)}>
            <option value="all">All tools</option>
            {options.tools.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="f">
          <label htmlFor="f-mat">Maturity</label>
          <select
            id="f-mat"
            value={filters.maturity}
            onChange={(e) => setFilter("maturity", e.target.value)}
          >
            <option value="all">All maturity</option>
            {BANDS.map((b) => (
              <option key={b.name} value={b.name}>
                {b.name} ({b.low}-{b.high}%)
              </option>
            ))}
          </select>
        </div>

        <div className="f">
          <label>Users counted</label>
          <div className="seg">
            {(["all", "active", "inactive"] as const).map((value) => (
              <button
                key={value}
                type="button"
                aria-pressed={filters.users === value}
                onClick={() => setFilter("users", value)}
              >
                {value === "all" ? "All" : value === "active" ? "Active" : "Inactive"}
              </button>
            ))}
          </div>
        </div>

        <button className="lnk" type="button" onClick={resetFilters}>Reset</button>
      </div>
    </div>
  );
};
