"""Synthetic local-only NiceGUI measurement acceptance application."""
from nicegui import ui

from app.logic import Measurement, make_measurement


def home() -> None:
    # State belongs to this page/client, not the process shared by every user.
    records: list[Measurement] = []
    ui.label('Synthetic measurement review').classes('text-h4')
    ui.label('Local example data only. Values do not represent production measurements.')
    sample_id = ui.input('Sample ID', validation={'Required': lambda value: bool((value or '').strip())}).props('aria-label="Sample ID"')
    value = ui.number('Measured value', value=0.0).props('aria-label="Measured value"')
    lower = ui.number('Lower limit', value=0.0).props('aria-label="Lower limit"')
    upper = ui.number('Upper limit', value=10.0).props('aria-label="Upper limit"')
    status = ui.label('No measurement submitted.').props('role="status" aria-live="polite"')
    error = ui.label('').props('role="alert" aria-live="assertive"')
    summary = ui.label('Accepted: 0; Review: 0').props('aria-label="Result summary"')
    result_list = ui.column().props('aria-label="Measurement results"')

    def submit():
        error.set_text('')
        try:
            record = make_measurement(sample_id.value or '', float(value.value), float(lower.value), float(upper.value))
        except (TypeError, ValueError) as exc:
            error.set_text(str(exc))
            return
        if any(existing.sample_id == record.sample_id for existing in records):
            error.set_text('Sample ID has already been evaluated.')
            return
        records.append(record)
        label = 'ACCEPT' if record.accepted else 'REVIEW'
        status.set_text(f'{record.sample_id}: {label} ({record.value:g})')
        status.classes('text-positive' if record.accepted else 'text-warning', remove='text-negative text-positive text-warning')
        with result_list:
            ui.label(f'{record.sample_id}: {label} — {record.value:g}')
        accepted = sum(item.accepted for item in records)
        summary.set_text(f'Accepted: {accepted}; Review: {len(records) - accepted}')

    def clear_results():
        records.clear()
        result_list.clear()
        summary.set_text('Accepted: 0; Review: 0')
        status.set_text('No measurement submitted.')
        error.set_text('')

    ui.button('Evaluate sample', on_click=submit)
    ui.button('Clear results', on_click=clear_results)


if __name__ == '__main__':
    ui.run(root=home, host='127.0.0.1', port=8080, title='Synthetic measurement review', show=False, reload=False)
