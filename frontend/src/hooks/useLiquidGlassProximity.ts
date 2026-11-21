import { useEffect } from 'react';
import {
  computeElementProximity,
  computeProximityGlassFrost,
} from '../utils/liquidGlassProximity';

/**
 * Updates --glass-frost on every `.liquidglass` element smoothly based on pointer proximity.
 */
export function useLiquidGlassProximity(baseFrost: number, radiusPx = 220) {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const resetAll = () => {
      document.querySelectorAll<HTMLElement>('.liquidglass').forEach((el) => {
        el.style.removeProperty('--glass-frost');
      });
    };

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
      resetAll();
      return;
    }

    let rafId: number | null = null;
    let pointerX = -9999;
    let pointerY = -9999;

    const updateElements = () => {
      rafId = null;
      const elements = document.querySelectorAll<HTMLElement>('.liquidglass');
      elements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        const proximity = computeElementProximity(pointerX, pointerY, rect, radiusPx);
        if (proximity > 0.001) {
          const nextFrost = computeProximityGlassFrost(baseFrost, proximity);
          el.style.setProperty('--glass-frost', String(nextFrost));
        } else {
          el.style.removeProperty('--glass-frost');
        }
      });
    };

    const onPointerMove = (e: PointerEvent) => {
      pointerX = e.clientX;
      pointerY = e.clientY;
      if (rafId === null) {
        rafId = window.requestAnimationFrame(updateElements);
      }
    };

    const onPointerReset = () => {
      pointerX = -9999;
      pointerY = -9999;
      if (rafId !== null) {
        window.cancelAnimationFrame(rafId);
        rafId = null;
      }
      resetAll();
    };

    window.addEventListener('pointermove', onPointerMove, { passive: true });
    document.documentElement.addEventListener('pointerleave', onPointerReset);
    window.addEventListener('blur', onPointerReset);

    return () => {
      window.removeEventListener('pointermove', onPointerMove);
      document.documentElement.removeEventListener('pointerleave', onPointerReset);
      window.removeEventListener('blur', onPointerReset);
      if (rafId !== null) {
        window.cancelAnimationFrame(rafId);
      }
      resetAll();
    };
  }, [baseFrost, radiusPx]);
}
