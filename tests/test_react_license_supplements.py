import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.react_license_supplements import validate


ROOT = Path(__file__).resolve().parents[1]


class ReactLicenseSupplementTests(unittest.TestCase):
    def _copy_fixture(self, root):
        for relative in (
            "research/react-license-supplements.json",
            "research/react-macos-arm64-dependency-audit.json",
            "examples/react-app/package-lock.json",
        ):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        manifest = json.loads((root / "research/react-license-supplements.json").read_text(encoding="utf-8"))
        for row in manifest["notices"]:
            target = root / row["file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / row["file"], target)
        return manifest

    def test_pinned_upstream_notices_match_lock_and_audit(self):
        self.assertEqual([], validate(ROOT))

    def test_notice_whitespace_normalization_is_recorded(self):
        manifest = json.loads((ROOT / "research/react-license-supplements.json").read_text(encoding="utf-8"))
        for row in manifest["notices"]:
            text = (ROOT / row["file"]).read_text(encoding="utf-8")
            self.assertEqual(text, text.rstrip() + chr(10))
            self.assertFalse(any(line.endswith((" ", chr(9))) for line in text.splitlines()), row["file"])

    def test_crlf_checkout_has_the_same_notice_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._copy_fixture(root)
            lf = bytes((10,))
            crlf = bytes((13, 10))
            for row in manifest["notices"]:
                path = root / row["file"]
                path.write_bytes(path.read_bytes().replace(lf, crlf))
            self.assertEqual([], validate(root))

    def test_modified_notice_fails_hash_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._copy_fixture(root)
            first_notice = root / manifest["notices"][0]["file"]
            text = first_notice.read_text(encoding="utf-8")
            first_notice.write_text(text + chr(10) + "modified" + chr(10), encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("SHA-256 mismatch" in error for error in errors), errors)

if __name__ == "__main__":
    unittest.main()
