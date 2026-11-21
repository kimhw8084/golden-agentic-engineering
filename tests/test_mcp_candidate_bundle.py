import hashlib
import importlib.util
import json
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mcp_candidate_bundle", ROOT / "scripts" / "mcp_candidate_bundle.py")
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)


def make_wheel(directory, filename, name, version, requires=(), license_text="MIT License"):
    path = directory / filename
    dist_info = filename.split("-")[0].replace("_", "-") + f"-{version}.dist-info"
    metadata = "Metadata-Version: 2.1\nName: " + name + "\nVersion: " + version + "\nLicense: MIT\n"
    metadata += "".join(f"Requires-Dist: {requirement}\n" for requirement in requires)
    with zipfile.ZipFile(path, "w") as wheel:
        wheel.writestr(f"{dist_info}/METADATA", metadata + "\n")
        wheel.writestr(f"{dist_info}/WHEEL", "Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n")
        wheel.writestr(f"{dist_info}/licenses/LICENSE", license_text)
    return path


def macos_wheels(directory, *, mcp_requires=None, types_requires=()):
    directory.mkdir(exist_ok=True)
    make_wheel(directory, "mcp-2.3.0-py3-none-any.whl", "mcp", "2.3.0",
               mcp_requires if mcp_requires is not None else ["mcp-types==2.3.0"])
    make_wheel(directory, "mcp_types-2.3.0-py3-none-any.whl", "mcp-types", "2.3.0", types_requires)


class MCPCandidateBundleTests(unittest.TestCase):
    def test_committed_candidate_manifest_is_explicitly_unqualified_and_hash_pinned(self):
        manifest = json.loads((ROOT / "offline" / "mcp-sdk-candidate" / "candidate-manifest.json").read_text())
        self.assertEqual(manifest["status"], "CANDIDATE_ONLY_COMPANY_OSS_AND_TARGET_COMPATIBILITY_UNKNOWN")
        self.assertEqual(manifest["source"]["package"], "mcp==2.3.0")
        archives = manifest["candidate_archives"]
        self.assertEqual({item["filename"] for item in archives}, {
            "macos-arm64-cp311.tar.gz", "windows-amd64-cp311.tar.gz", "linux-x86_64-glibc217-cp311.tar.gz"
        })
        for archive in archives:
            self.assertRegex(archive["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(archive["bytes"], 0)
        runtime = manifest["runtime_evidence"]
        self.assertEqual(runtime["sdk_stdio_discovery_and_tool_call"], "PASS_ON_MACOS_ARM64_SYNTHETIC_FIXTURE")
        self.assertEqual(runtime["opencode_v2_2_7_mcp_2026_07_28_protocol"], "PASS_LOCAL_SYNTHETIC_CALL")
        self.assertEqual(runtime["opencode_v2_2_7_mcp_auto_protocol"], "PASS_LOCAL_SYNTHETIC_CALL")
        self.assertEqual(runtime["opencode_v2_2_7_standard_library_auto_fallback"], "PASS_LOCAL_SYNTHETIC_CALL")
        self.assertEqual(runtime["company_opencode"], "NOT_RUN")
        self.assertEqual(runtime["provider_reasoning_and_injection_resistance"], "NOT_EVALUATED_SCRIPTED_PROVIDER")
        self.assertTrue((ROOT / runtime["probe_evidence"]).is_file())
        self.assertNotIn("FAILED", json.dumps(runtime))

    def test_create_verifies_candidate_and_records_complete_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheels = root / "wheels"
            macos_wheels(wheels)
            archive = bundle.create_candidate(wheels, "macos-arm64-cp311", root / "out")
            result = bundle.verify_candidate(archive)
            self.assertEqual(result["status"], "VERIFIED_CANDIDATE_ONLY")
            self.assertEqual(result["target"], "macos-arm64-cp311")
            extracted = root / "inspect"
            extracted.mkdir()
            with tarfile.open(archive, "r:gz") as stream:
                stream.extractall(extracted)
            candidate = extracted / "macos-arm64-cp311"
            manifest = json.loads((candidate / "manifest.json").read_text())
            lock = (candidate / "requirements.lock").read_text()
            self.assertIn("mcp==2.3.0 --hash=sha256:", lock)
            self.assertEqual(manifest["target"]["company_oss_approval"], "NOT_OBTAINED")
            self.assertEqual(manifest["target"]["offline_install_test"], "NOT_RUN_FOR_THIS_TARGET")
            self.assertTrue((candidate / "cyclonedx.cdx.json").is_file())
            self.assertTrue((candidate / "license-inventory.json").is_file())

    def test_dependency_closure_evaluates_target_markers_and_transitive_requirements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mac = root / "mac"
            mac.mkdir()
            make_wheel(mac, "mcp-2.3.0-py3-none-any.whl", "mcp", "2.3.0", [
                "mcp-types==2.3.0", "optional-win==1.0; sys_platform == 'win32'"])
            make_wheel(mac, "mcp_types-2.3.0-py3-none-any.whl", "mcp-types", "2.3.0", ["leaf==1.0"])
            make_wheel(mac, "leaf-1.0-py3-none-any.whl", "leaf", "1.0")
            _, packages, dependencies = bundle.inspect_wheelhouse(mac, "macos-arm64-cp311")
            self.assertNotIn("optional-win", packages)
            self.assertEqual(dependencies["mcp-types"], ["leaf"])

            win = root / "win"
            win.mkdir()
            make_wheel(win, "mcp-2.3.0-py3-none-any.whl", "mcp", "2.3.0", [
                "mcp-types==2.3.0", "pywin32==311; sys_platform == 'win32'"])
            make_wheel(win, "mcp_types-2.3.0-py3-none-any.whl", "mcp-types", "2.3.0")
            make_wheel(win, "pywin32-311-cp311-cp311-win_amd64.whl", "pywin32", "311")
            _, packages, _ = bundle.inspect_wheelhouse(win, "windows-amd64-cp311")
            self.assertIn("pywin32", packages)

    def test_missing_transitive_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            wheels = Path(temp) / "wheels"
            wheels.mkdir()
            macos_wheels(wheels, types_requires=["missing-leaf==1.0"])
            with self.assertRaisesRegex(ValueError, "requires missing missing-leaf"):
                bundle.inspect_wheelhouse(wheels, "macos-arm64-cp311")

    def test_windows_requires_pywin32_even_if_marker_metadata_is_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            wheels = Path(temp) / "wheels"
            wheels.mkdir()
            macos_wheels(wheels)
            with self.assertRaisesRegex(ValueError, "missing its pywin32 dependency"):
                bundle.inspect_wheelhouse(wheels, "windows-amd64-cp311")

    def test_rejects_symlink_wheel(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheels = root / "wheels"
            wheels.mkdir()
            (wheels / "link.whl").symlink_to(root / "absent.whl")
            with self.assertRaisesRegex(ValueError, "only regular wheel files"):
                bundle.inspect_wheelhouse(wheels, "macos-arm64-cp311")

    def test_rejects_wheel_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            wheels = Path(temp) / "wheels"
            wheels.mkdir()
            wheel = make_wheel(wheels, "mcp-2.3.0-py3-none-any.whl", "mcp", "2.3.0")
            replacement = wheel.with_suffix(".replacement")
            with zipfile.ZipFile(wheel) as source, zipfile.ZipFile(replacement, "w") as target:
                for item in source.infolist():
                    target.writestr(item.filename, source.read(item.filename))
                target.writestr("../escape", "unsafe")
            replacement.replace(wheel)
            with self.assertRaisesRegex(ValueError, "Unsafe wheel member"):
                bundle.inspect_wheelhouse(wheels, "macos-arm64-cp311")

    def test_rejects_archive_tampering_and_bad_sidecar_filename(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheels = root / "wheels"
            macos_wheels(wheels)
            archive = bundle.create_candidate(wheels, "macos-arm64-cp311", root / "out")
            with archive.open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                bundle.verify_candidate(archive)

            sidecar = archive.with_suffix(archive.suffix + ".sha256")
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            sidecar.write_text(f"{digest}  different-name.tar.gz\n")
            with self.assertRaisesRegex(ValueError, "sidecar format or filename mismatch"):
                bundle.verify_candidate(archive)


if __name__ == "__main__":
    unittest.main()
