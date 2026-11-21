import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIAL_PATH = ROOT / 'scripts' / 'run_simpy_candidate_trial.py'
SPEC = importlib.util.spec_from_file_location('simpy_candidate_trial', TRIAL_PATH)
TRIAL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(TRIAL)


class SimPyCandidateTrialTests(unittest.TestCase):
    def test_wheel_must_use_reviewed_artifact_filename(self):
        with self.assertRaisesRegex(ValueError, 'ordinary SimPy 4.1.2 wheel'):
            TRIAL.inspect_wheel(Path('simpy.whl'))

    def test_wheel_hash_is_checked_before_archive_import(self):
        with tempfile.TemporaryDirectory() as directory:
            wheel = Path(directory) / TRIAL.WHEEL_NAME
            wheel.write_bytes(b'modified candidate wheel')
            with self.assertRaisesRegex(ValueError, 'wheel SHA-256'):
                TRIAL.inspect_wheel(wheel)

    def test_source_archive_must_use_reviewed_artifact_filename(self):
        with self.assertRaisesRegex(ValueError, 'ordinary SimPy 4.1.2 source archive'):
            TRIAL.inspect_source_archive(Path('simpy.tar.gz'))

    def test_source_archive_hash_is_checked_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            sdist = Path(directory) / TRIAL.SDIST_NAME
            sdist.write_bytes(b'modified candidate source archive')
            with self.assertRaisesRegex(ValueError, 'source SHA-256'):
                TRIAL.inspect_source_archive(sdist)


if __name__ == '__main__':
    unittest.main()
