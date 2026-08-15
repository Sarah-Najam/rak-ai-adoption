/** Brand lockup, reporting period, and the data actions. */
import { RAK_LOGO } from "@/lib/logo";

interface Props {
  wave: string;
  source: "api" | "file" | "sample";
  onExport: () => void;
}

export const Header = ({ wave, source, onExport }: Props) => (
  <header className="top">
    <div className="top-in">
      <div className="lockup">
        <img className="logo-img" alt="RAK Properties" src={RAK_LOGO} />
        <div className="rule" />
        <div className="ttl">
          <span className="eyebrow">Learning &amp; Development</span>
          <h1>AI Adoption Index</h1>
        </div>
      </div>

      <div className="stamp">
        <span className="eyebrow">Survey wave</span>
        <div className="v">{wave}</div>
        <span className="eyebrow" style={{ marginTop: 6, display: "block" }}>
          Data source
        </span>
        <div className="v">
          <span className="pulse" />
          {source === "api" ? "Live API" : source === "file" ? "Published file" : "Sample data"}
        </div>
      </div>

      <div className="acts">
        <button className="btn solid" onClick={onExport} type="button">
          Export to Excel
        </button>
      </div>
    </div>
  </header>
);
