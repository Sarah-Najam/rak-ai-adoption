/**
 * The wire format: what the API returns and what data.json contains.
 *
 * Kept separate from the domain types in scoring.ts because they change for
 * different reasons. The wire format is a contract with the backend and must
 * tolerate missing fields; the domain types are what the UI relies on and are
 * fully populated by the time they reach a component.
 */

import type { DepartmentWave, IndicatorKey, Weights } from "./scoring";

export interface WireDepartment {
  name: string;
  function?: string;
  fn?: string;
  staff?: number;
  mix?: Partial<DepartmentWave["mix"]>;
  metrics?: Partial<Record<IndicatorKey, number>>;
  sessions?: number;
  cases?: number;
  aiAgentsCount?: number;
  aiAgentsPersonal?: number;
  aiAutomationsCount?: number;
  aiAutomationsPersonal?: number;
  /** Pairs of tool name and the share of the department using it. */
  tools?: (string | number)[][];
  processes?: string[];
  gap?: string;
  opportunity?: string;
  respondents?: number;
  reliability?: DepartmentWave["reliability"];
}

export interface WireWave {
  label?: string;
  departments?: WireDepartment[];
}

export interface WirePayload {
  waves?: WireWave[];
  weights?: Partial<Weights>;
  targets?: {
    org?: number;
    quarter?: number;
    min?: number;
    byDept?: Record<string, number>;
  };
}
