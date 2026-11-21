import React, { useMemo } from 'react';

interface LiquidGlassFilterProps {
  displacementScale?: number;
  blurStdDev?: number;
}

/**
 * Generates a smooth rounded-bevel optical displacement map as a valid PNG Data URI.
 * Outer rounded perimeter refracts strongly like a curved glass edge, while the interior
 * remains optically calm so foreground typography stays crisp.
 */
function createBevelDisplacementMap(): string {
  if (typeof document === 'undefined') return '';
  const w = 256;
  const h = 128;
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  if (!ctx) return '';

  const img = ctx.createImageData(w, h);
  const data = img.data;
  const rx = 0.22;
  const ry = 0.22;
  const rimWidth = 0.22;

  for (let y = 0; y < h; y++) {
    const ny = (y / (h - 1)) * 2 - 1; // -1..1
    for (let x = 0; x < w; x++) {
      const nx = (x / (w - 1)) * 2 - 1; // -1..1

      // Rounded-box SDF in normalized [-1, 1] space
      const qx = Math.abs(nx) - (1 - rx);
      const qy = Math.abs(ny) - (1 - ry);
      const outX = Math.max(qx, 0);
      const outY = Math.max(qy, 0);
      const sdf =
        Math.hypot(outX, outY) + Math.min(Math.max(qx, qy), 0) - Math.min(rx, ry);

      // Distance inward from outer edge (0 at edge, >0 inside)
      const distFromEdge = Math.max(0, -sdf);
      const bevelT = Math.max(0, 1 - distFromEdge / rimWidth);
      const bevelStrength = bevelT * bevelT * (3 - 2 * bevelT);

      const outMag = Math.hypot(outX, outY);
      let dirX = 0;
      let dirY = 0;
      if (outMag > 0.0001) {
        dirX = Math.sign(nx) * (outX / outMag);
        dirY = Math.sign(ny) * (outY / outMag);
      } else if (qx > qy) {
        dirX = Math.sign(nx);
      } else {
        dirY = Math.sign(ny);
      }

      const dx = dirX * bevelStrength;
      const dy = dirY * bevelStrength;

      const idx = (y * w + x) * 4;
      data[idx] = Math.max(0, Math.min(255, Math.round(128 + dx * 118)));
      data[idx + 1] = Math.max(0, Math.min(255, Math.round(128 + dy * 118)));
      data[idx + 2] = 128;
      data[idx + 3] = 255;
    }
  }

  ctx.putImageData(img, 0, 0);
  return canvas.toDataURL('image/png');
}

export function LiquidGlassFilter({
  displacementScale = -30,
  blurStdDev = 1.05,
}: LiquidGlassFilterProps) {
  const displacementUri = useMemo(() => createBevelDisplacementMap(), []);

  if (!displacementUri) return null;

  return (
    <svg
      className="glass-surface__filter"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <filter
          id="glass-filter-_r_b_"
          colorInterpolationFilters="sRGB"
          x="0%"
          y="0%"
          width="100%"
          height="100%"
        >
          <feImage
            x="0"
            y="0"
            width="100%"
            height="100%"
            preserveAspectRatio="none"
            result="map"
            href={displacementUri}
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="map"
            id="redchannel"
            result="dispRed"
            scale={displacementScale + 4}
            xChannelSelector="R"
            yChannelSelector="G"
          />
          <feColorMatrix
            in="dispRed"
            type="matrix"
            values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0"
            result="red"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="map"
            id="greenchannel"
            result="dispGreen"
            scale={displacementScale}
            xChannelSelector="R"
            yChannelSelector="G"
          />
          <feColorMatrix
            in="dispGreen"
            type="matrix"
            values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0"
            result="green"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="map"
            id="bluechannel"
            result="dispBlue"
            scale={displacementScale - 4}
            xChannelSelector="R"
            yChannelSelector="G"
          />
          <feColorMatrix
            in="dispBlue"
            type="matrix"
            values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0"
            result="blue"
          />
          <feBlend in="red" in2="green" mode="screen" result="rg" />
          <feBlend in="rg" in2="blue" mode="screen" result="output" />
          <feGaussianBlur in="output" stdDeviation={blurStdDev} />
        </filter>
      </defs>
    </svg>
  );
}
