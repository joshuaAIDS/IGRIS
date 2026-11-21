export interface RectBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

/**
 * Computes smooth normalized proximity (0..1) from cursor coordinates to a rectangular element.
 * Inside or touching the element returns 1; at or beyond radiusPx returns 0.
 */
export function computeElementProximity(
  cursorX: number,
  cursorY: number,
  rect: RectBounds,
  radiusPx = 220,
): number {
  if (radiusPx <= 0 || !Number.isFinite(cursorX) || !Number.isFinite(cursorY)) {
    return 0;
  }
  const dx = Math.max(rect.left - cursorX, 0, cursorX - rect.right);
  const dy = Math.max(rect.top - cursorY, 0, cursorY - rect.bottom);
  const distance = Math.hypot(dx, dy);
  if (distance >= radiusPx) return 0;
  const linear = 1 - distance / radiusPx;
  return linear * linear * (3 - 2 * linear);
}

/**
 * Adjusts base --glass-frost based on cursor proximity (0..1),
 * keeping the shift subtle and bounded for fluid liquid-glass feedback.
 */
export function computeProximityGlassFrost(
  baseFrost: number,
  proximity: number,
  maxDelta = 0.16,
): number {
  const clampedProximity = Math.min(1, Math.max(0, proximity));
  const next = baseFrost + clampedProximity * maxDelta;
  return Number(Math.min(0.45, Math.max(0, next)).toFixed(4));
}
