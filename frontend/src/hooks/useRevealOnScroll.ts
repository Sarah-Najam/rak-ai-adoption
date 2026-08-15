/**
 * Fades each section in as it scrolls into view.
 *
 * The stylesheet hides sections until they get an "in" class. This adds it.
 *
 * Two safeguards, because a decorative animation must never be able to hide the
 * content it decorates. If IntersectionObserver is unavailable, every section is
 * revealed immediately. And anything already on screen at load is revealed on
 * the first pass rather than waiting for a scroll that may never come, since on
 * a tall monitor the whole page can be visible without scrolling at all.
 */

import { useEffect } from "react";

export const useRevealOnScroll = (enabled = true): void => {
  useEffect(() => {
    const sections = Array.from(document.querySelectorAll("section"));
    const revealAll = () => sections.forEach((s) => s.classList.add("in"));

    if (!enabled || typeof IntersectionObserver === "undefined") {
      revealAll();
      return undefined;
    }

    // Respect the operating system setting for reduced motion.
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) {
      revealAll();
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.05 },
    );

    sections.forEach((section) => observer.observe(section));

    // Belt and braces: if anything is still hidden shortly after load, show it.
    const failsafe = window.setTimeout(revealAll, 1500);

    return () => {
      observer.disconnect();
      window.clearTimeout(failsafe);
    };
  }, [enabled]);
};
