"""Optional user-visible NiceGUI UI tests; no browser is required."""
import os
import sys
import unittest
from pathlib import Path

try:
    from nicegui import ui
    from nicegui.testing import user_simulation
except ImportError:  # the company/offline Python-only path may not have NiceGUI staged
    ui = None
    user_simulation = None

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@unittest.skipIf(ui is None, 'NiceGUI is not installed in this offline environment.')
class MeasurementUiTests(unittest.IsolatedAsyncioTestCase):
    async def test_validation_state_results_duplicate_and_clear(self):
        if 'PYTEST_CURRENT_TEST' not in os.environ:
            self.skipTest('NiceGUI UI simulation requires pytest; standard-library tests remain available.')
        async with user_simulation(main_file=ROOT / 'app' / 'main.py') as user:
            await user.open('/')
            await user.should_see('No measurement submitted.')
            await user.should_see('Accepted: 0; Review: 0')

            user.find(kind=ui.button, content='Evaluate sample').click()
            await user.should_see('Sample ID is required.')
            await user.should_see('No measurement submitted.')

            user.find(ui.input, content='Sample ID').type('S-ACCEPT')
            user.find(kind=ui.button, content='Evaluate sample').click()
            await user.should_see('S-ACCEPT: ACCEPT (0)')
            await user.should_see('Accepted: 1; Review: 0')

            user.find(ui.input, content='Sample ID').clear().type('S-REVIEW')
            user.find(kind=ui.number, content='Measured value').clear().type('11')
            user.find(kind=ui.button, content='Evaluate sample').click()
            await user.should_see('S-REVIEW: REVIEW (11)')
            await user.should_see('Accepted: 1; Review: 1')

            user.find(ui.input, content='Sample ID').clear().type('S-ACCEPT')
            user.find(kind=ui.button, content='Evaluate sample').click()
            await user.should_see('Sample ID has already been evaluated.')
            await user.should_see('Accepted: 1; Review: 1')

            user.find(kind=ui.button, content='Clear results').click()
            await user.should_see('Accepted: 0; Review: 0')
            await user.should_see('No measurement submitted.')
            await user.should_not_see('S-ACCEPT: ACCEPT')
            await user.should_not_see('S-REVIEW: REVIEW')


if __name__ == '__main__':
    unittest.main()
