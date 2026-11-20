import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

  it('shows a specific error for a cleared numeric field', () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText('Sample ID'), { target: { value: 'S-2' } });
    fireEvent.change(screen.getByLabelText('Measured value'), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: 'Evaluate sample' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Measured value is required.');
    expect(screen.getByLabelText('Measurement results')).toBeEmptyDOMElement();
  });

  it('supports keyboard-only submission and announces the result', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.tab();
    await user.type(screen.getByLabelText('Sample ID'), 'S-3');
    await user.tab();
    await user.type(screen.getByLabelText('Measured value'), '5');
    await user.tab();
    await user.tab();
    await user.tab();
    await user.keyboard('{Enter}');
    expect(screen.getByRole('status')).toHaveTextContent('S-3: ACCEPT');
    expect(screen.getByLabelText('Measurement results')).toHaveTextContent('S-3: ACCEPT');
  });
});
