import { describe, expect, it } from 'vitest';
import { evaluate } from './logic';

describe('evaluate synthetic sample', () => {
  it('accepts inclusive range endpoints', () => {
    expect(evaluate({ id: 'S1', value: 0, lower: 0, upper: 10 }).message).toBe('ACCEPT');
    expect(evaluate({ id: 'S1', value: 10, lower: 0, upper: 10 }).accepted).toBe(true);
  });
  it('returns review outside the limits', () => {
    expect(evaluate({ id: 'S2', value: 10.1, lower: 0, upper: 10 }).message).toBe('REVIEW');
  });
  it('rejects invalid sample IDs and bounds', () => {
    expect(() => evaluate({ id: ' ', value: 1, lower: 0, upper: 2 })).toThrow('Sample ID');
    expect(() => evaluate({ id: 'S3', value: 1, lower: 3, upper: 2 })).toThrow('Lower limit');
  });
});
