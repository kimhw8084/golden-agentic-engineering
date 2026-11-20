import { FormEvent, useState } from 'react';
import { evaluate } from './logic';

type Result = { id: string; value: number; label: string };

export function App() {
  const [results, setResults] = useState<Result[]>([]);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('No sample evaluated.');
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    const fields = new FormData(event.currentTarget);
    try {
      const id = String(fields.get('sampleId') ?? '');
      const value = Number(fields.get('value'));
      const lower = Number(fields.get('lower'));
      const upper = Number(fields.get('upper'));
      const outcome = evaluate({ id, value, lower, upper });
      const row = { id: id.trim(), value, label: outcome.message };
      setResults((current) => [...current, row]);
      setMessage(`${row.id}: ${row.label} (${row.value})`);
    } catch (cause) {
      const detail = cause instanceof Error ? cause.message : 'Sample could not be evaluated.';
      setError(detail); setMessage('Review the error before continuing.');
    }
  }
  return <main>
    <h1>Synthetic measurement review</h1>
    <p>Local example values only. No production data is used.</p>
    <form onSubmit={submit}>
      <label>Sample ID <input name="sampleId" required /></label>
      <label>Measured value <input name="value" type="number" step="any" required /></label>
      <label>Lower limit <input name="lower" type="number" step="any" defaultValue="0" required /></label>
      <label>Upper limit <input name="upper" type="number" step="any" defaultValue="10" required /></label>
      <button type="submit">Evaluate sample</button>
    </form>
    <p role="status" aria-live="polite">{message}</p>
    {error && <p role="alert">{error}</p>}
    <h2>Results</h2>
    <ul aria-label="Measurement results">{results.map((row, i) => <li key={`${row.id}-${i}`}>{row.id}: {row.label} — {row.value}</li>)}</ul>
  </main>;
}
