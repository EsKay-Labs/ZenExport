"""Installation transactions, ownership, path safety and data preservation."""

import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from installer import setup
from tools.build_bundle import build
from tools.build_installer import payload


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_dir = tempfile.TemporaryDirectory()
        archive = Path(cls.bundle_dir.name) / "payload.zip"
        cls.receipt = payload(build(cls.bundle_dir.name), archive)
        cls.data = archive.read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.bundle_dir.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ZenExport Ελληνικά ")
        self.parent = Path(self.temporary.name).resolve()
        self.target = self.parent / "FusionAddins/ZenExport"

    def tearDown(self):
        self.temporary.cleanup()

    def revised_payload(self, version="99.0.0", extra=None):
        receipt, files = setup.read_payload(self.data)
        receipt["version"] = version
        files["zenexport/addin.py"] += b"\n# upgraded runtime\n"
        receipt["files"]["zenexport/addin.py"] = hashlib.sha256(files["zenexport/addin.py"]).hexdigest()
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            for name, data in files.items():
                archive.writestr(name, data)
            archive.writestr(setup.RECEIPT, json.dumps(receipt))
            for name, data in (extra or {}).items():
                archive.writestr(name, data)
        return output.getvalue()

    def test_complete_payload_and_startup_flag(self):
        result = setup.install(self.data, self.target)
        self.assertEqual(result["status"], "installed")
        self.assertTrue(result["restart_fusion"])
        for name, value in self.receipt["files"].items():
            self.assertEqual(setup.digest(self.target / name), value)
        manifest = json.loads((self.target / "ZenExport.manifest").read_text())
        self.assertTrue(manifest["runOnStartup"])
        self.assertNotIn("session_config.json", self.receipt["files"])

    def test_repeated_install_does_not_rewrite_an_unchanged_install(self):
        setup.install(self.data, self.target)
        before = (self.target / "ZenExport.py").stat().st_mtime_ns
        self.assertEqual(setup.install(self.data, self.target)["status"], "unchanged")
        self.assertEqual((self.target / "ZenExport.py").stat().st_mtime_ns, before)

    def test_upgrade_preserves_custom_files_and_backs_up_the_old_runtime(self):
        setup.install(self.data, self.target)
        private = self.target / "session_config.json"
        private.write_bytes(b"private-legacy-destinations")
        previous = (self.target / "zenexport/addin.py").read_bytes()
        result = setup.install(self.revised_payload(), self.target)
        self.assertEqual(result["version"], "99.0.0")
        self.assertEqual(private.read_bytes(), b"private-legacy-destinations")
        with zipfile.ZipFile(result["backup"]) as archive:
            self.assertEqual(archive.read("zenexport/addin.py"), previous)
            self.assertEqual(archive.read("session_config.json"), private.read_bytes())

    def test_downgrade_is_refused(self):
        setup.install(self.revised_payload(), self.target)
        before = (self.target / setup.RECEIPT).read_bytes()
        with self.assertRaisesRegex(ValueError, "newer"):
            setup.install(self.data, self.target)
        self.assertEqual((self.target / setup.RECEIPT).read_bytes(), before)

    def test_damaged_runtime_is_repaired_and_original_damage_is_backed_up(self):
        setup.install(self.data, self.target)
        code = self.target / "zenexport/addin.py"
        code.write_bytes(b"damaged")
        result = setup.install(self.data, self.target)
        self.assertEqual(setup.digest(code), self.receipt["files"]["zenexport/addin.py"])
        with zipfile.ZipFile(result["backup"]) as archive:
            self.assertEqual(archive.read("zenexport/addin.py"), b"damaged")

    def test_failed_publish_rolls_back_existing_installation(self):
        setup.install(self.data, self.target)
        before = {p.relative_to(self.target).as_posix(): p.read_bytes()
                  for p in self.target.rglob("*") if p.is_file()}
        rename = Path.rename

        def fail_stage(path, destination):
            if path.name.startswith(".zenexport-stage-"):
                raise PermissionError("simulated target lock")
            return rename(path, destination)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaisesRegex(PermissionError, "target lock"):
                setup.install(self.revised_payload(), self.target)
        self.assertEqual(before, {p.relative_to(self.target).as_posix(): p.read_bytes()
                                  for p in self.target.rglob("*") if p.is_file()})
        self.assertFalse(list(self.target.parent.glob(".zenexport-stage-*")))

    def test_uninstall_only_removes_owned_unchanged_files(self):
        setup.install(self.data, self.target)
        user_file = self.target / "notes.txt"
        user_file.write_bytes(b"keep")
        modified = self.target / "zenexport/model.py"
        modified.write_bytes(b"user edit")
        settings = self.parent / "Local/ZenExport/config.json"
        settings.parent.mkdir(parents=True)
        settings.write_bytes(b"private settings")
        result = setup.uninstall(self.target)
        self.assertEqual(result["modified_files_preserved"], ["zenexport/model.py"])
        self.assertEqual(user_file.read_bytes(), b"keep")
        self.assertEqual(modified.read_bytes(), b"user edit")
        self.assertEqual(settings.read_bytes(), b"private settings")
        self.assertFalse((self.target / "ZenExport.py").exists())

    def test_uninstall_removes_empty_owned_directory_and_is_repeatable(self):
        setup.install(self.data, self.target)
        setup.uninstall(self.target)
        self.assertFalse(self.target.exists())
        self.assertEqual(setup.uninstall(self.target)["status"], "absent")

    def test_unknown_destination_and_unknown_uninstall_are_refused(self):
        self.target.mkdir(parents=True)
        note = self.target / "important.txt"
        note.write_bytes(b"keep")
        with self.assertRaisesRegex(ValueError, "unrelated"):
            setup.install(self.data, self.target)
        with self.assertRaises(FileNotFoundError):
            setup.uninstall(self.target)
        self.assertEqual(note.read_bytes(), b"keep")

    def test_payload_extra_files_and_tampering_are_refused_before_install(self):
        with self.assertRaisesRegex(ValueError, "unexpected"):
            setup.install(self.revised_payload(extra={"../outside.py": b"bad"}), self.target)
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.data)) as source, zipfile.ZipFile(output, "w") as destination:
            for name in source.namelist():
                destination.writestr(name, b"tampered" if name == "ZenExport.py" else source.read(name))
        with self.assertRaisesRegex(ValueError, "checksum"):
            setup.install(output.getvalue(), self.target)
        self.assertFalse(self.target.parent.exists())

    def test_unsafe_receipt_paths_are_refused(self):
        for name in ("../outside.py", "/tmp/code", "C:/code.py", "zenexport/../code.py",
                     "zenexport\\model.py", "zenexport/model.py.", "zenexport/con.py", "config.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                setup.safe_name(name)

    def test_junction_or_symlink_target_is_refused_without_touching_outside(self):
        outside = self.parent / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_bytes(b"keep")
        self.target.parent.mkdir()
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(str(outside), str(self.target))
        else:
            self.target.symlink_to(outside, target_is_directory=True)
        try:
            with self.assertRaisesRegex(ValueError, "links or junctions"):
                setup.install(self.data, self.target)
            with self.assertRaises(ValueError):
                setup.uninstall(self.target)
            self.assertEqual((outside / "keep.txt").read_bytes(), b"keep")
        finally:
            if os.name == "nt":
                self.target.rmdir()
            else:
                self.target.unlink()

    def test_recognized_manual_install_is_adopted_with_a_backup(self):
        setup.install(self.data, self.target)
        (self.target / setup.RECEIPT).unlink()
        (self.target / "session_config.json").write_bytes(b"legacy destinations")
        result = setup.install(self.data, self.target)
        self.assertIsNotNone(result["backup"])
        self.assertEqual((self.target / "session_config.json").read_bytes(), b"legacy destinations")

    def test_default_target_and_legacy_selection_are_automatic(self):
        legacy = self.parent / "Autodesk/Autodesk Fusion 360/API/AddIns/ZenExport"
        setup.install(self.data, legacy)
        with patch.object(setup.sys, "platform", "win32"), patch.dict(os.environ, {"APPDATA": str(self.parent)}):
            self.assertEqual(setup.default_target(), legacy)
            with patch.object(setup, "recognized_manual_install", return_value=False):
                self.assertEqual(setup.default_target(), self.parent / "Autodesk/FusionAddins/ZenExport")
        with patch.object(setup.sys, "platform", "darwin"), patch.object(Path, "home", return_value=self.parent):
            self.assertEqual(setup.default_target(), self.parent / "Library/Application Support/Autodesk"
                             / "FusionAddins/ZenExport")
        with patch.object(setup.sys, "platform", "linux"), self.assertRaisesRegex(RuntimeError, "Linux"):
            setup.default_target()


if __name__ == "__main__":
    unittest.main()
