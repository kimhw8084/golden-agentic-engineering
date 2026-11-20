import importlib.util
import io
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('golden_control', ROOT / 'scripts' / 'golden_control.py')
control = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(control)


class GoldenControlUITests(unittest.TestCase):
    def test_local_page_and_task_route_api_are_served(self):
        class Request:
            def __init__(self, path):
                self.path = path
                self.wfile = io.BytesIO()
                self.response = None
                self.headers = {}

            def send_response(self, status):
                self.response = status

            def send_header(self, name, value):
                self.headers[name] = value

            def end_headers(self):
                pass

            def _send_file(self, path, content_type):
                self.response = 200
                self.content_type = content_type
                self.wfile.write(path.read_bytes())

            def send_error(self, status):
                self.response = status

        page = Request('/')
        control.ControlHandler.do_GET(page)
        self.assertEqual(page.response, 200)
        self.assertIn('TASK ROUTING', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('COMPANY_START_HERE.md', page.wfile.getvalue().decode('utf-8'))

        workflows = Request('/api/workflows')
        control.ControlHandler.do_GET(workflows)
        self.assertEqual(workflows.response, 200)
        payload = json.loads(workflows.wfile.getvalue())
        self.assertEqual(payload['schema'], 'golden-task-routing/v1')
        self.assertEqual(len(payload['workflows']), 12)


if __name__ == '__main__':
    unittest.main()
