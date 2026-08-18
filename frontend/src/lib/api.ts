/**
 * Talking to the backend.
 *
 * Three sources are tried in order: the API, then a static data.json next to the
 * page, then the built-in sample. The middle option matters because it lets the
 * dashboard be published to SharePoint or Vercel as static files with no server
 * at all, which is how the first survey wave will be shown.
 *
 * The source is reported back so the UI can say plainly when figures are sample
 * data. Nobody should ever mistake demonstration numbers for real ones.
 */

import type { DashboardData, Department, DepartmentWave, IndicatorKey, Weights } from "./scoring";
import { DEFAULT_WEIGHTS, INDICATORS } from "./scoring";
import type { WireDepartment, WirePayload } from "./wire";

export const slug = (value: string): string =>
  value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "dept";

const toWave = (d: WireDepartment): DepartmentWave => {
  const staff = Math.max(1, Math.round(d.staff ?? 1));
  const mix = {
    leadership: d.mix?.leadership ?? 0,
    manager: d.mix?.manager ?? 0,
    specialist: d.mix?.specialist ?? 0,
    support: d.mix?.support ?? 0,
  };
  // A department with no level breakdown is treated as all specialists rather
  // than as empty, so the level filter cannot silently erase it.
  if (mix.leadership + mix.manager + mix.specialist + mix.support === 0) {
    mix.specialist = staff;
  }
  const metrics = INDICATORS.reduce(
    (acc, k) => ({ ...acc, [k]: Number(d.metrics?.[k] ?? 0) }),
    {} as Record<IndicatorKey, number>,
  );
  return {
    staff,
    mix,
    metrics,
    sessions: d.sessions ?? 0,
    cases: d.cases ?? 0,
    aiAgentsCount: d.aiAgentsCount ?? 0,
    aiAgentsPersonal: d.aiAgentsPersonal ?? 0,
    aiAutomationsCount: d.aiAutomationsCount ?? 0,
    aiAutomationsPersonal: d.aiAutomationsPersonal ?? 0,
    // Tuples arrive from JSON as plain arrays, so narrow them here rather than
    // trusting the shape further up.
    tools: (d.tools ?? [])
      .filter((pair) => pair.length >= 2)
      .map((pair) => [String(pair[0]), Number(pair[1])] as [string, number]),
    processes: d.processes ?? [],
    gap: d.gap || "Not recorded",
    opportunity: d.opportunity || "Not recorded",
    respondents: d.respondents,
    reliability: d.reliability,
  };
};

/** Merge departments across waves, keyed by name, so trends can be drawn. */
export const parsePayload = (
  payload: WirePayload,
  source: DashboardData["source"],
): DashboardData => {
  const waves = payload.waves?.length ? payload.waves : [{ label: "Wave 1", departments: [] }];
  const labels = waves.map((w, i) => w.label || `Wave ${i + 1}`);

  const byId = new Map<string, Department>();
  waves.forEach((wave, index) => {
    (wave.departments ?? []).forEach((d) => {
      const id = slug(d.name);
      const existing = byId.get(id) ?? {
        id,
        name: d.name,
        function: d.function || d.fn || "Unassigned",
        byWave: [] as (DepartmentWave | undefined)[],
      };
      existing.function = d.function || d.fn || existing.function;
      existing.byWave[index] = toWave(d);
      byId.set(id, existing);
    });
  });

  return {
    waves: labels,
    departments: [...byId.values()],
    weights: { ...DEFAULT_WEIGHTS, ...(payload.weights ?? {}) } as Weights,
    targets: {
      org: payload.targets?.org ?? 70,
      quarter: payload.targets?.quarter ?? 65,
      min: payload.targets?.min ?? 40,
      byDept: payload.targets?.byDept ?? {},
    },
    source,
  };
};

const fetchJson = async (url: string): Promise<WirePayload> => {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return (await response.json()) as WirePayload;
};

/**
 * Where the API lives, if there is one.
 *
 * Set VITE_API_URL to point at a deployed backend. Leave it unset and the
 * dashboard reads the published data.json instead, which is how it runs as a
 * static site with no server at all.
 */
const API_URL = import.meta.env.VITE_API_URL as string | undefined;

export const loadDashboard = async (): Promise<DashboardData> => {
  if (API_URL) {
    try {
      return parsePayload(await fetchJson(`${API_URL}/api/v1/dashboard`), "api");
    } catch {
      // The API is configured but unreachable. Fall through to the file, so a
      // backend outage degrades to yesterday's published numbers rather than a
      // blank screen.
    }
  }
  try {
    return parsePayload(await fetchJson("/data.json"), "file");
  } catch {
    // Nothing published yet.
  }
  const { SAMPLE_PAYLOAD } = await import("./sample");
  return parsePayload(SAMPLE_PAYLOAD, "sample");
};
