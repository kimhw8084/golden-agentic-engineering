export type Sample = { id: string; value: number; lower: number; upper: number };

export function evaluate(sample: Sample): { accepted: boolean; message: string } {
  if (!sample.id.trim()) throw new Error('Sample ID is required.');
  if (![sample.value, sample.lower, sample.upper].every(Number.isFinite)) throw new Error('Values and limits must be finite numbers.');
  if (sample.lower > sample.upper) throw new Error('Lower limit must not exceed upper limit.');
  return { accepted: sample.value >= sample.lower && sample.value <= sample.upper,
    message: sample.value >= sample.lower && sample.value <= sample.upper ? 'ACCEPT' : 'REVIEW' };
}
