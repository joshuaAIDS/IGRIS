import test from 'node:test';
import assert from 'node:assert/strict';
import {
  computeElementProximity,
  computeProximityGlassFrost,
} from './liquidGlassProximity.ts';

const SAMPLE_RECT = {
  left: 100,
  top: 100,
  right: 200,
  bottom: 140,
};

test('computeElementProximity returns 1 inside the element and 0 outside radius', () => {
  assert.equal(computeElementProximity(150, 120, SAMPLE_RECT, 200), 1);
  assert.equal(computeElementProximity(100, 100, SAMPLE_RECT, 200), 1);
  assert.equal(computeElementProximity(450, 120, SAMPLE_RECT, 200), 0);
});

test('computeElementProximity decreases monotonically as cursor moves away', () => {
  const near = computeElementProximity(240, 120, SAMPLE_RECT, 200); // 40px away
  const mid = computeElementProximity(300, 120, SAMPLE_RECT, 200); // 100px away
  const far = computeElementProximity(360, 120, SAMPLE_RECT, 200); // 160px away

  assert.ok(near > mid && mid > far && far > 0);
});

test('computeProximityGlassFrost shifts baseFrost subtly and clamps cleanly', () => {
  assert.equal(computeProximityGlassFrost(0.1, 0), 0.1);
  assert.equal(computeProximityGlassFrost(0.1, 1), 0.26);
  assert.equal(computeProximityGlassFrost(0.1, 0.5), 0.18);
  assert.equal(computeProximityGlassFrost(0.4, 1, 0.2), 0.45);
});
