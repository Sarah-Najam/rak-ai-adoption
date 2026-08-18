import { DataTable } from "@/components/DataTable";
import { DetailDrawer } from "@/components/DetailDrawer";
import { ExecutiveSummary } from "@/components/ExecutiveSummary";
import { FilterBar } from "@/components/FilterBar";
import { Header } from "@/components/Header";
import { MaturityPanel } from "@/components/MaturityPanel";
import { SaveBar } from "@/components/SaveBar";
import { ScoringModel } from "@/components/ScoringModel";
import { TargetsPanel } from "@/components/TargetsPanel";
import { TreemapGrid } from "@/components/TreemapGrid";
import { TrendChart } from "@/components/TrendChart";
import { useDashboard } from "@/hooks/useDashboard";
import { useRevealOnScroll } from "@/hooks/useRevealOnScroll";
import { exportToExcel } from "@/lib/export";

const App = () => {
  const dash = useDashboard();

  // Runs once the data has loaded, so it observes sections that actually exist.
  useRevealOnScroll(!dash.loading);

  if (dash.loading) {
    return (
      <div className="wrap" style={{ paddingTop: 80, color: "var(--txt-3)" }}>
        Loading survey results…
      </div>
    );
  }

  if (dash.error) {
    return (
      <div className="wrap" style={{ paddingTop: 80 }}>
        <div className="warn">Could not load the dashboard: {dash.error}</div>
      </div>
    );
  }

  return (
    <>
      <Header
        wave={dash.waves[dash.filters.wave] ?? ""}
        source={dash.source}
        onExport={() => { void exportToExcel(dash); }}
      />
      <FilterBar dash={dash} />

      <div className="wrap">
       

        <SaveBar dash={dash} />
        <ExecutiveSummary dash={dash} />
        <TreemapGrid dash={dash} />

        <section id="s3" style={{ marginTop: 26 }}>
          <div className="cols">
            <MaturityPanel dash={dash} />
            <TargetsPanel dash={dash} />
          </div>
        </section>

        <TrendChart dash={dash} />

        <section id="s5" style={{ marginTop: 26 }}>
          <div className="cols">
            <ScoringModel dash={dash} />
            <DataTable dash={dash} />
          </div>
        </section>

        <footer>
          <span>
            RAK Properties PJSC · Learning &amp; Development
          </span>
          <span className="mono">8 indicators · 5 maturity bands</span>
        </footer>
      </div>

      <DetailDrawer dash={dash} />
    </>
  );
};

export default App;
