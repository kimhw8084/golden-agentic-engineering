"""Synthetic local-only NiceGUI measurement acceptance application."""
from nicegui import ui

from logic import make_measurement

records = []


@ui.page('/')
def home():
    ui.label('Synthetic measurement review').classes('text-h4')
    ui.label('Local example data only. Values do not represent production measurements.')
    sample_id = ui.input('Sample ID', validation={'Required': lambda value: bool(value.strip())}).props('aria-label="Sample ID"')
    value = ui.number('Measured value', value=0.0).props('aria-label="Measured value"')
    lower = ui.number('Lower limit', value=0.0).props('aria-label="Lower limit"')
    upper = ui.number('Upper limit', value=10.0).props('aria-label="Upper limit"')
    status = ui.label('No measurement submitted.').props('role="status" aria-live="polite"')
    result_list = ui.column().props('aria-label="Measurement results"')

    def submit():
        try:
            record = make_measurement(sample_id.value or '', float(value.value), float(lower.value), float(upper.value))
        except (TypeError, ValueError) as exc:
            status.set_text(str(exc))
            status.classes('text-negative', remove='text-positive')
            return
        records.append(record)
        label = 'ACCEPT' if record.accepted else 'REVIEW'
        status.set_text(f'{record.sample_id}: {label} ({record.value:g})')
        status.classes('text-positive' if record.accepted else 'text-warning', remove='text-negative')
        with result_list:
            ui.label(f'{record.sample_id}: {label} — {record.value:g}')

    ui.button('Evaluate sample', on_click=submit)


if __name__ == '__main__':
    ui.run(host='127.0.0.1', port=8080, title='Synthetic measurement review', show=False, reload=False)
