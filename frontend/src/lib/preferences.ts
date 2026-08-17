/**
 * Saving the settings leadership can change: weights and targets.
 *
 * These are stored in the browser rather than on the server, which is a real
 * limitation worth stating plainly: they are per browser and per device, so a
 * target you set on your laptop is not visible to a colleague on theirs.
 *
 * That is the right trade-off for now. Server-side saving needs a login, and
 * the dashboard is currently published as a static file with no sign-in. When
 * the API is connected, PUT /api/v1/config/targets replaces this and the
 * settings become shared and versioned.
 *
 * Survey results are never stored here. Those come from data.json or the API,
 * so a stale copy in someone's browser can never contradict the published
 * numbers.
 */

import type { Targets, Weights } from "./scoring";

const KEY = "rak-ai-adoption:preferences:v1";

export interface Preferences {
  weights: Weights;
  targets: Targets;
  savedAt: string;
}

export const loadPreferences = (): Preferences | null => {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Preferences;
    if (!parsed.weights || !parsed.targets) return null;
    return parsed;
  } catch {
    // Private browsing, a full disk, or a corrupted value. None of these should
    // stop the dashboard loading, so fall back to the published defaults.
    return null;
  }
};

export const savePreferences = (weights: Weights, targets: Targets): boolean => {
  try {
    const payload: Preferences = { weights, targets, savedAt: new Date().toISOString() };
    window.localStorage.setItem(KEY, JSON.stringify(payload));
    return true;
  } catch {
    return false;
  }
};

export const clearPreferences = (): void => {
  try {
    window.localStorage.removeItem(KEY);
  } catch {
    // Nothing to do. The caller resets to the published values regardless.
  }
};