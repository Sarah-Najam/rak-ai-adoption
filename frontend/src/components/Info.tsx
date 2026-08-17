

import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

interface Props {
  children: React.ReactNode;
  label: string;
}

const CLOSE_DELAY = 180;
const GAP = 12;

export const Info = ({ children, label }: Props) => {
  const [open, setOpen] = useState(false);
  const [style, setStyle] = useState<React.CSSProperties>({ visibility: "hidden" });

  const buttonRef = useRef<HTMLButtonElement>(null);
  const bubbleRef = useRef<HTMLDivElement>(null);
  const timer = useRef<number | undefined>(undefined);
  const id = useId();

  const cancelClose = useCallback(() => {
    if (timer.current) window.clearTimeout(timer.current);
  }, []);

  
  const closeSoon = useCallback(() => {
    cancelClose();
    timer.current = window.setTimeout(() => setOpen(false), CLOSE_DELAY);
  }, [cancelClose]);

  const openNow = useCallback(() => {
    cancelClose();
    setOpen(true);
  }, [cancelClose]);

  // Measure after the bubble exists, then place it. Hidden until measured, so
  // it never flashes in the wrong position first.
  useLayoutEffect(() => {
    if (!open || !buttonRef.current || !bubbleRef.current) return;
    const trigger = buttonRef.current.getBoundingClientRect();
    const bubble = bubbleRef.current.getBoundingClientRect();
    const margin = 10;

    let left = trigger.left + trigger.width / 2 - bubble.width / 2;
    left = Math.max(margin, Math.min(left, window.innerWidth - bubble.width - margin));

    // Prefer below, which keeps the heading being explained readable. Flip above
    // only when there is genuinely no room.
    const below = trigger.bottom + GAP;
    const fitsBelow = below + bubble.height < window.innerHeight - margin;
    const top = fitsBelow ? below : Math.max(margin, trigger.top - bubble.height - GAP);

    setStyle({ left, top, visibility: "visible" });
  }, [open, children]);

  useEffect(() => {
    if (!open) {
      setStyle({ visibility: "hidden" });
      return undefined;
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onClick = (e: MouseEvent) => {
      const target = e.target as Node;
      if (buttonRef.current?.contains(target) || bubbleRef.current?.contains(target)) return;
      setOpen(false);
    };
    // Scrolling moves the trigger but not a fixed bubble, so close rather than
    // leave it floating over unrelated content.
    const onScroll = () => setOpen(false);

    window.addEventListener("keydown", onKey);
    window.addEventListener("click", onClick);
    window.addEventListener("scroll", onScroll, true);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("click", onClick);
      window.removeEventListener("scroll", onScroll, true);
    };
  }, [open]);

  useEffect(() => cancelClose, [cancelClose]);

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        className="info-dot"
        aria-label={label}
        aria-expanded={open}
        aria-describedby={open ? id : undefined}
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
          setOpen((v) => !v);
        }}
        onMouseEnter={openNow}
        onMouseLeave={closeSoon}
        onFocus={openNow}
        onBlur={closeSoon}
      >
        i
      </button>

      {open &&
        createPortal(
          <div
            ref={bubbleRef}
            id={id}
            role="tooltip"
            className="info-bubble"
            style={style}
            onMouseEnter={openNow}
            onMouseLeave={closeSoon}
          >
            {children}
          </div>,
          document.body,
        )}
    </>
  );
};