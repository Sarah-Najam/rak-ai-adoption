/**
 * The scoring model, in TypeScript.
 *
 * This mirrors backend/app/services/scoring.py. Having the rules in two places
 * is a real cost, so it is worth saying why it is here.
 *
 * The weight sliders have to feel instant. Every drag would otherwise be a round
 * trip to the API, and thirteen departments recalculating on every pixel of
 * movement is not something a network can keep up with. So the browser computes
 * the adoption rate from indicator scores the server has already produced.
 *
 * The split is deliberate: the server owns the hard part, turning raw survey
 * answers into the eight indicator scores. The browser only does the weighted
 * average, which is a dozen lines and easy to keep identical. The backend tests
 * are the source of truth if the two ever disagree.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export const INDICATORS = [
  "users",
  "freq",
  "train",
  "flow",
  "tasks",
  "cover",
  "prof",
  "comp",
] as const;

export type IndicatorKey = (typeof INDICATORS)[number];

export type Weights = Record<IndicatorKey, number>;

export interface IndicatorMeta {
  key: IndicatorKey;
  label: string;
  note: string;
  defaultWeight: number;
}

export const INDICATOR_META: IndicatorMeta[] = [
  { key: "users", label: "Active AI users", defaultWeight: 20,
    note: "% of staff who used an AI tool in the last 30 days" },
  { key: "freq", label: "Usage frequency", defaultWeight: 15,
    note: "AI sessions per user per week, scored against a target of 5" },
  { key: "train", label: "AI training completion", defaultWeight: 15,
    note: "% of staff who completed the assigned AI training" },
  { key: "flow", label: "AI in weekly workflow", defaultWeight: 15,
    note: "% using AI in real weekly work, not one-off trials" },
  { key: "tasks", label: "AI-assisted task volume", defaultWeight: 10,
    note: "AI-assisted tasks per user per month, against a target" },
  { key: "cover", label: "Eligible workflows covered", defaultWeight: 10,
    note: "% of AI-suitable workflows that actually use AI" },
  { key: "prof", label: "Proficiency & readiness", defaultWeight: 10,
    note: "Average score from the AI knowledge check" },
  { key: "comp", label: "Safe use of AI", defaultWeight: 5,
    note: "Company accounts used, no sensitive data in personal ones" },
];

export const DEFAULT_WEIGHTS: Weights = INDICATOR_META.reduce(
  (acc, m) => ({ ...acc, [m.key]: m.defaultWeight }),
  {} as Weights,
);

export type LevelKey = "all" | "leadership" | "manager" | "specialist" | "support";

export interface LevelMeta {
  key: LevelKey;
  label: string;
  adjustment: number;
}

/**
 * Seniority correlates with AI use, so filtering to one level shifts the
 * behavioural indicators. Structural ones such as training completion are
 * counted from records and must not move.
 */
export const LEVELS: LevelMeta[] = [
  { key: "all", label: "All levels", adjustment: 0 },
  { key: "leadership", label: "Leadership", adjustment: 7 },
  { key: "manager", label: "Managers", adjustment: 3 },
  { key: "specialist", label: "Specialists", adjustment: 0 },
  { key: "support", label: "Support & site", adjustment: -11 },
];

const LEVEL_SENSITIVE: ReadonlySet<IndicatorKey> = new Set<IndicatorKey>([
  "users",
  "freq",
  "flow",
  "prof",
]);

export interface Band {
  name: string;
  low: number;
  high: number;
  colour: string;
  darkText: boolean;
  description: string;
}

/** Brightness rises with adoption, using only the four approved brand colours. */
export const BANDS: Band[] = [
  { name: "Emerging",    low: 0,  high: 25,  colour: "#1E4258", darkText: false, description: "Aware, little real use" },
  { name: "Developing",  low: 26, high: 50,  colour: "#AF5F46", darkText: false, description: "Pockets of use, no routine" },
  { name: "Established", low: 51, high: 75,  colour: "#BEC8BE", darkText: true,  description: "Routine use by most" },
  { name: "Advanced",    low: 76, high: 90,  colour: "#A5C8D2", darkText: true,  description: "Embedded in core workflows" },
  { name: "Leading",     low: 91, high: 100, colour: "#FFFFFF", darkText: true,  description: "Sets the practice for others" },
];

export interface LevelMix {
  leadership: number;
  manager: number;
  specialist: number;
  support: number;
}

/** One department as measured in one wave. */
export interface DepartmentWave {
  staff: number;
  mix: LevelMix;
  metrics: Record<IndicatorKey, number>;
  sessions: number;
  cases: number;
  tools: [string, number][];
  processes: string[];
  gap: string;
  opportunity: string;
  respondents?: number;
  reliability?: "reliable" | "provisional" | "insufficient";
}

/** A department across every wave, which is what the UI works with. */
export interface Department {
  id: string;
  name: string;
  function: string;
  byWave: (DepartmentWave | undefined)[];
}

export interface Targets {
  org: number;
  quarter: number;
  min: number;
  byDept: Record<string, number>;
}

export interface DashboardData {
  waves: string[];
  departments: Department[];
  weights: Weights;
  targets: Targets;
  source: "api" | "file" | "sample";
}

export type TargetStatus = "above" | "on_track" | "below" | "critical";

// ---------------------------------------------------------------------------
// Maths
// ---------------------------------------------------------------------------

export const clamp = (v: number, low = 0, high = 100): number =>
  Math.max(low, Math.min(high, v));

export const bandFor = (rate: number): Band => {
  for (let i = BANDS.length - 1; i >= 0; i -= 1) {
    if (rate >= BANDS[i].low) return BANDS[i];
  }
  return BANDS[0];
};

/**
 * Rescale weights to sum to 100. Moving one slider should not silently change
 * what every other indicator means, and a set summing to 87 should still work.
 */
export const normaliseWeights = (weights: Weights): Weights => {
  const total = INDICATORS.reduce((sum, k) => sum + Math.max(0, weights[k] ?? 0), 0);
  if (total <= 0) return { ...DEFAULT_WEIGHTS };
  return INDICATORS.reduce(
    (acc, k) => ({ ...acc, [k]: (Math.max(0, weights[k] ?? 0) / total) * 100 }),
    {} as Weights,
  );
};

const levelAdjustment = (key: IndicatorKey, level: LevelKey): number => {
  if (!LEVEL_SENSITIVE.has(key)) return 0;
  return LEVELS.find((l) => l.key === level)?.adjustment ?? 0;
};

export const adjustedMetrics = (
  metrics: Record<IndicatorKey, number>,
  level: LevelKey,
): Record<IndicatorKey, number> =>
  INDICATORS.reduce(
    (acc, k) => ({ ...acc, [k]: clamp((metrics[k] ?? 0) + levelAdjustment(k, level)) }),
    {} as Record<IndicatorKey, number>,
  );

/** The headline number: a weighted mean of the eight indicator scores. */
export const adoptionRate = (
  metrics: Record<IndicatorKey, number>,
  weights: Weights,
  level: LevelKey = "all",
): number => {
  const w = normaliseWeights(weights);
  const values = adjustedMetrics(metrics, level);
  const total = INDICATORS.reduce((sum, k) => sum + values[k] * w[k], 0);
  return Math.round((total / 100) * 100) / 100;
};

/**
 * A department's rate in a given wave, or null when it was not measured then.
 *
 * Null rather than zero, always. Zero reads as "adoption collapsed to nothing",
 * null reads as "we did not measure it", and telling those apart is the entire
 * reason for running the survey twice.
 */
export const rateInWave = (
  dept: Department,
  wave: number,
  weights: Weights,
  level: LevelKey = "all",
): number | null => {
  const snapshot = dept.byWave[wave];
  if (!snapshot) return null;
  return adoptionRate(snapshot.metrics, weights, level);
};

export const staffInWave = (
  dept: Department,
  wave: number,
  level: LevelKey = "all",
): number => {
  const snapshot = dept.byWave[wave];
  if (!snapshot) return 0;
  return level === "all" ? snapshot.staff : (snapshot.mix[level] ?? 0);
};

export const activeUsers = (
  dept: Department,
  wave: number,
  level: LevelKey = "all",
): number => {
  const snapshot = dept.byWave[wave];
  if (!snapshot) return 0;
  const pct = clamp((snapshot.metrics.users ?? 0) + levelAdjustment("users", level));
  return Math.round((staffInWave(dept, wave, level) * pct) / 100);
};

/**
 * Employee-weighted mean across departments.
 *
 * A 9-person team at 82% and a 41-person team at 36% is not a 59% organisation.
 * An unweighted average lets small enthusiastic teams hide the fact that most
 * of the company is not using AI.
 */
export const organisationRate = (
  depts: Department[],
  wave: number,
  weights: Weights,
  level: LevelKey = "all",
): number | null => {
  let numerator = 0;
  let denominator = 0;
  depts.forEach((d) => {
    const rate = rateInWave(d, wave, weights, level);
    if (rate === null) return;
    const staff = staffInWave(d, wave, level);
    numerator += rate * staff;
    denominator += staff;
  });
  return denominator > 0 ? Math.round((numerator / denominator) * 100) / 100 : null;
};

export const ON_TRACK_TOLERANCE = 10;

export const targetFor = (dept: Department, targets: Targets): number =>
  targets.byDept[dept.id] || targets.org;

/** Four states, so a department merely behind is not confused with one at risk. */
export const targetStatus = (
  rate: number,
  target: number,
  minimum: number,
): TargetStatus => {
  if (rate < minimum) return "critical";
  if (rate >= target) return "above";
  if (rate >= target - ON_TRACK_TOLERANCE) return "on_track";
  return "below";
};

export const STATUS_LABEL: Record<TargetStatus, string> = {
  above: "Above target",
  on_track: "On track",
  below: "Below target",
  critical: "Critical",
};

export const STATUS_CLASS: Record<TargetStatus, string> = {
  above: "above",
  on_track: "track",
  below: "below",
  critical: "crit",
};

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

export const fmt1 = (v: number): string => (Math.round(v * 10) / 10).toFixed(1);
export const fmt0 = (v: number): string => String(Math.round(v));
export const signed = (v: number): string => (v >= 0 ? `+${fmt1(v)}` : fmt1(v));
