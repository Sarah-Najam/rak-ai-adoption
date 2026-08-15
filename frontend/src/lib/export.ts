/**
 * Excel export.
 *
 * SheetJS is loaded from a CDN on demand rather than bundled. It is a large
 * dependency used by one button, and loading it lazily keeps the dashboard fast
 * for the many people who will never click it.
 */

import type { Dashboard } from "@/hooks/useDashboard";
import { INDICATOR_META, fmt1 } from "@/lib/scoring";

const CDN = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";

declare global {
  interface Window { XLSX?: any }
}

const loadSheetJs = (): Promise<any> =>
  new Promise((resolve, reject) => {
    if (window.XLSX) { resolve(window.XLSX); return; }
    const script = document.createElement("script");
    script.src = CDN;
    script.onload = () => (window.XLSX ? resolve(window.XLSX) : reject(new Error("XLSX missing")));
    script.onerror = () => reject(new Error("Could not load the Excel library"));
    document.head.appendChild(script);
  });

export const exportToExcel = async (dash: Dashboard): Promise<void> => {
  const XLSX = await loadSheetJs();
  const { views, summary, waves, filters, weights, targets } = dash;

  const departments = views.map((v) => {
    const snapshot = v.dept.byWave[filters.wave];
    const row: Record<string, string | number> = {
      Department: v.dept.name,
      "Business function": v.dept.function,
      "Total staff": snapshot?.staff ?? 0,
      Leadership: snapshot?.mix.leadership ?? 0,
      Managers: snapshot?.mix.manager ?? 0,
      Specialists: snapshot?.mix.specialist ?? 0,
      "Support & site": snapshot?.mix.support ?? 0,
    };
    INDICATOR_META.forEach((m) => {
      row[`${m.label} (0-100)`] = Math.round(snapshot?.metrics[m.key] ?? 0);
    });
    row["Sessions per user per week"] = snapshot?.sessions ?? 0;
    row["AI use cases"] = snapshot?.cases ?? 0;
    row["Department target %"] = targets.byDept[v.dept.id] ?? 0;
    row["Key gap"] = snapshot?.gap ?? "";
    row.Opportunity = snapshot?.opportunity ?? "";
    row["ADOPTION RATE % (calculated)"] = Number(fmt1(v.rate));
    row["MATURITY (calculated)"] = v.band.name;
    return row;
  });

  const overview = [
    { Measure: "Survey wave", Value: waves[filters.wave] },
    { Measure: "Organisation AI adoption rate %", Value: Number(fmt1(summary.rate)) },
    { Measure: "Organisation target %", Value: targets.org },
    { Measure: "Minimum acceptable %", Value: targets.min },
    { Measure: "Departments assessed", Value: summary.departments },
    { Measure: "Employees assessed", Value: summary.staff },
    { Measure: "Employees actively using AI", Value: summary.active },
    { Measure: "Departments at or above target", Value: views.filter((v) => v.rate >= v.target).length },
  ];

  const model = INDICATOR_META.map((m) => ({
    Indicator: m.label,
    "Weight %": weights[m.key],
    "What it measures": m.note,
  }));

  const book = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(book, XLSX.utils.json_to_sheet(departments), "Departments");
  XLSX.utils.book_append_sheet(book, XLSX.utils.json_to_sheet(overview), "Summary");
  XLSX.utils.book_append_sheet(book, XLSX.utils.json_to_sheet(model), "Scoring model");

  const stamp = (waves[filters.wave] ?? "wave").replace(/[^A-Za-z0-9]+/g, "-");
  XLSX.writeFile(book, `RAK-Properties-AI-Adoption-${stamp}.xlsx`);
};
