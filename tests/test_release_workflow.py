import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_tags_run_the_full_fail_closed_gate(self):
        workflow = (ROOT / '.github' / 'workflows' / 'release-qualification.yml').read_text(encoding='utf-8')
        self.assertIn("tags: ['golden-*']", workflow)
        self.assertIn('python scripts/golden.py check --full', workflow)
        self.assertNotIn('scripts/golden.py check --fast', workflow)
        self.assertIn('python scripts/security_scan.py --history', workflow)


if __name__ == '__main__':
    unittest.main()
