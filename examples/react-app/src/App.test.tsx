import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { App } from './App';

describe('sample review UI', () => {
  it('reports state and validation errors accessibly', () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText('Sample ID'), { target: { value: 'S-1' } });
    fireEvent.change(screen.getByLabelText('Measured value'), { target: { value: '11' } });
    fireEvent.click(screen.getByRole('button', { name: 'Evaluate sample' }));
    expect(screen.getByRole('status')).toHaveTextContent('S-1: REVIEW');
    expect(screen.getByLabelText('Measurement results')).toHaveTextContent('S-1: REVIEW');
    fireEvent.change(screen.getByLabelText('Sample ID'), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: 'Evaluate sample' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Sample ID');
  });
});
