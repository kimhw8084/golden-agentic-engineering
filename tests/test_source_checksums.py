import unittest

from scripts.update_checksums import ROOT, source_files


class SourceChecksumTests(unittest.TestCase):
    def test_ignored_runtime_output_is_not_in_source_manifest(self):
        names = {path.relative_to(ROOT).as_posix() for path in source_files()}
        self.assertFalse(any(name == "out" or name.startswith("out/") for name in names))


if __name__ == "__main__":
    unittest.main()
