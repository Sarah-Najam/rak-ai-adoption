/**
 * Save and reset for the settings leadership can change.
 *
 * It only appears once something has actually been edited. A permanent save
 * button on a page where nothing has changed is noise, and worse, it implies
 * the page is a form to be filled in rather than a report to be read.
 *
 * The wording is deliberately explicit about scope. "Saved in this browser" is
 * a limitation, and stating it here is much better than a colleague opening the
 * link, seeing different targets, and concluding the dashboard is unreliable.
 */

import { useState } from "react";

import type { Dashboard } from "@/hooks/useDashboard";

export const SaveBar = ({ dash }: { dash: Dashboard }) => {
  const { dirty, savedAt, saveSettings, resetSettings } = dash;
  const [failed, setFailed] = useState(false);

  if (!dirty && !savedAt) return null;

  const savedLabel = savedAt
    ? new Date(savedAt).toLocaleString(undefined, {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  return (
    <div className="savebar">
      <span className="savebar-text">
        {dirty ? (
          <>
            <b>Unsaved changes</b> to weights or targets. They apply to this view
            now, but will be lost on refresh unless you save them.
          </>
        ) : (
          <>
            <b>Saved in this browser</b> on {savedLabel}. Colleagues opening the
            link still see the published settings.
          </>
        )}
      </span>

      <span className="savebar-actions">
        {dirty && (
          <button
            className="btn solid"
            type="button"
            onClick={() => setFailed(!saveSettings())}
          >
            Save settings
          </button>
        )}
        <button className="btn" type="button" onClick={() => { resetSettings(); setFailed(false); }}>
          Reset to published
        </button>
      </span>

      {failed && (
        <span className="savebar-text" style={{ color: "#D9937C" }}>
          Could not save. Browser storage may be blocked in private mode.
        </span>
      )}
    </div>
  );
};