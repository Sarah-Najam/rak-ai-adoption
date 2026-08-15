/**
 * The single source of truth for the dashboard.
 *
 * Everything the user can change lives here: which wave, the filters, the
 * weights, the targets, and which department is open. Components stay
 * presentational and read from this, which keeps the filtering rules in one
 * place rather than scattered across ten files that slowly disagree.
 *
 * Derived values are memoised on the inputs they actually depend on. The weight
 * sliders fire on every pixel of movement, so recomputing thirteen departments
 * on each event needs to stay cheap.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { loadDashboard } from "@/lib/api";
import type {
  DashboardData,
  Department,
  IndicatorKey,
  LevelKey,
  Targets,
  Weights,
} from "@/lib/scoring";
import {
  DEFAULT_WEIGHTS,
  activeUsers,
  adoptionRate,
  bandFor,
  organisationRate,
  rateInWave,
  staffInWave,
  targetFor,
  targetStatus,
} from "@/lib/scoring";

export type UserCount = "all" | "active" | "inactive";

export interface Filters {
  department: string;
  wave: number;
  fn: string;
  level: LevelKey;
  tool: string;
  maturity: string;
  users: UserCount;
  search: string;
}

const INITIAL_FILTERS: Filters = {
  department: "all",
  wave: 0,
  fn: "all",
  level: "all",
  tool: "all",
  maturity: "all",
  users: "all",
  search: "",
};

export interface DepartmentView {
  dept: Department;
  rate: number;
  band: ReturnType<typeof bandFor>;
  staff: number;
  active: number;
  counted: number;
  target: number;
  status: ReturnType<typeof targetStatus>;
  previousRate: number | null;
}

export const useDashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>(INITIAL_FILTERS);
  const [weights, setWeights] = useState<Weights>(DEFAULT_WEIGHTS);
  const [targets, setTargets] = useState<Targets>({
    org: 70,
    quarter: 65,
    min: 40,
    byDept: {},
  });
  const [selected, setSelected] = useState<string | null>(null);
  const [compare, setCompare] = useState<string[]>([]);

  // ---- load ---------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;
    loadDashboard()
      .then((payload) => {
        if (cancelled) return;
        setData(payload);
        setWeights(payload.weights);
        setTargets(payload.targets);
        // Open on the most recent wave, which is what leadership wants to see.
        setFilters((f) => ({ ...f, wave: Math.max(0, payload.waves.length - 1) }));
        setCompare(payload.departments.slice(0, 2).map((d) => d.id));
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not load data");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const departments = data?.departments ?? [];
  const waves = data?.waves ?? [];
  const { wave, level } = filters;

  // ---- filtering ----------------------------------------------------------
  const visible = useMemo<Department[]>(() => {
    return departments.filter((d) => {
      const snapshot = d.byWave[wave];
      if (!snapshot) return false;
      if (filters.department !== "all" && d.id !== filters.department) return false;
      if (filters.fn !== "all" && d.function !== filters.fn) return false;
      if (filters.search && !d.name.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      if (filters.tool !== "all" && !snapshot.tools.some(([name]) => name === filters.tool)) {
        return false;
      }
      if (filters.maturity !== "all") {
        const rate = adoptionRate(snapshot.metrics, weights, level);
        if (bandFor(rate).name !== filters.maturity) return false;
      }
      // Filtering to a level that does not exist in a department would show it
      // with a headcount of zero, which reads as a data error rather than a filter.
      if (level !== "all" && (snapshot.mix[level] ?? 0) === 0) return false;

      const staff = staffInWave(d, wave, level);
      const active = activeUsers(d, wave, level);
      if (filters.users === "active" && active <= 0) return false;
      if (filters.users === "inactive" && staff - active <= 0) return false;
      return true;
    });
  }, [departments, filters, wave, level, weights]);

  // ---- per department view ------------------------------------------------
  const views = useMemo<DepartmentView[]>(() => {
    return visible.map((dept) => {
      const rate = rateInWave(dept, wave, weights, level) ?? 0;
      const staff = staffInWave(dept, wave, level);
      const active = activeUsers(dept, wave, level);
      const target = targetFor(dept, targets);
      const counted =
        filters.users === "active" ? active : filters.users === "inactive" ? staff - active : staff;
      return {
        dept,
        rate,
        band: bandFor(rate),
        staff,
        active,
        counted,
        target,
        status: targetStatus(rate, target, targets.min),
        previousRate: wave > 0 ? rateInWave(dept, wave - 1, weights, level) : null,
      };
    });
  }, [visible, wave, weights, level, targets, filters.users]);

  // ---- organisation totals ------------------------------------------------
  const summary = useMemo(() => {
    const now = organisationRate(visible, wave, weights, level);
    const previous = wave > 0 ? organisationRate(visible, wave - 1, weights, level) : null;
    const staff = views.reduce((sum, v) => sum + v.staff, 0);
    const active = views.reduce((sum, v) => sum + v.active, 0);
    const counted = views.reduce((sum, v) => sum + v.counted, 0);
    const ranked = [...views].sort((a, b) => b.rate - a.rate);
    return {
      rate: now ?? 0,
      previous,
      delta: now !== null && previous !== null ? now - previous : null,
      staff,
      active,
      counted,
      activePct: staff > 0 ? (active / staff) * 100 : 0,
      departments: views.length,
      totalDepartments: departments.length,
      highest: ranked[0] ?? null,
      lowest: ranked[ranked.length - 1] ?? null,
      band: bandFor(now ?? 0),
    };
  }, [visible, views, wave, weights, level, departments.length]);

  // ---- filter option lists ------------------------------------------------
  const options = useMemo(() => {
    const functions = [...new Set(departments.map((d) => d.function))].sort();
    const tools = new Set<string>();
    departments.forEach((d) =>
      d.byWave[wave]?.tools.forEach(([name]) => tools.add(name)),
    );
    return { functions, tools: [...tools].sort() };
  }, [departments, wave]);

  // ---- actions ------------------------------------------------------------
  const setFilter = useCallback(<K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters((f) => ({ ...f, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters((f) => ({ ...INITIAL_FILTERS, wave: f.wave }));
  }, []);

  const setWeight = useCallback((key: IndicatorKey, value: number) => {
    setWeights((w) => ({ ...w, [key]: value }));
  }, []);

  const resetWeights = useCallback(() => setWeights(DEFAULT_WEIGHTS), []);

  const setDeptTarget = useCallback((id: string, value: number) => {
    setTargets((t) => ({ ...t, byDept: { ...t.byDept, [id]: value } }));
  }, []);

  const toggleCompare = useCallback((id: string) => {
    setCompare((current) => {
      if (current.includes(id)) return current.filter((c) => c !== id);
      // Four lines is the most a reader can follow at once.
      return [...current.slice(-3), id];
    });
  }, []);

  const selectedView = useMemo(
    () => views.find((v) => v.dept.id === selected) ?? null,
    [views, selected],
  );

  return {
    loading: data === null && error === null,
    error,
    source: data?.source ?? "sample",
    waves,
    departments,
    visible,
    views,
    summary,
    options,
    filters,
    setFilter,
    resetFilters,
    weights,
    setWeight,
    resetWeights,
    targets,
    setTargets,
    setDeptTarget,
    selected: selectedView,
    setSelected,
    compare,
    toggleCompare,
  };
};

export type Dashboard = ReturnType<typeof useDashboard>;
