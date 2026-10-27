"""Run the actual frozen installer offline, against an isolated user profile."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def smoke(executable):
    executable = Path(executable).resolve()
    with tempfile.TemporaryDirectory(prefix="ZenExport installer Ελληνικά ") as temporary:
        home = Path(temporary).resolve()
        roaming = home / "Roaming space"
        local = home / "Local space"
        roaming.mkdir()
        local.mkdir()
        env = dict(os.environ, APPDATA=str(roaming), LOCALAPPDATA=str(local), HOME=str(home))
        # Prevent the frozen installer from finding any external Python/tools.
        env["PATH"] = str(Path(os.environ.get("SystemRoot", "/usr")) / "System32")
        target = (roaming / "Autodesk/FusionAddins/ZenExport" if sys.platform == "win32"
                  else home / "Library/Application Support/Autodesk/FusionAddins/ZenExport")
        settings = local / "ZenExport/config.json"
        settings.parent.mkdir(parents=True)
        settings.write_bytes(b'{"private_settings": true}')
        project = home / "CAD project/Models/v01/Body.stl"
        project.parent.mkdir(parents=True)
        project.write_bytes(b"user-model-must-not-change")
        steps = []

        def run(*arguments, expected=0):
            report = home / "result.json"
            process = subprocess.run([str(executable), "--silent", "--report", str(report), *arguments],
                                     env=env, timeout=90, capture_output=True)
            if process.returncode != expected:
                raise AssertionError((process.returncode, process.stdout, process.stderr,
                                      report.read_text(encoding="utf-8") if report.exists() else "no report"))
            return json.loads(report.read_text(encoding="utf-8"))

        result = run()
        assert Path(result["target"]) == target, result
        assert result["status"] == "installed", result
        receipt = json.loads((target / ".zenexport-install.json").read_text(encoding="utf-8"))
        for name, value in receipt["files"].items():
            assert hashlib.sha256((target / name).read_bytes()).hexdigest() == value, name
        manifest = json.loads((target / "ZenExport.manifest").read_text(encoding="utf-8"))
        assert manifest["runOnStartup"] is True
        steps.append("fresh install to automatically discovered per-user path; every payload hash verified")
        assert run()["status"] == "unchanged"
        steps.append("repeat install is idempotent")
        custom = target / "my-notes.txt"
        custom.write_bytes(b"keep-this-file")
        old_receipt = dict(receipt, version="0.0.1", files=dict(receipt["files"]))
        retired = target / "zenexport/retired.py"
        retired.write_bytes(b"old-runtime-file")
        old_receipt["files"]["zenexport/retired.py"] = hashlib.sha256(retired.read_bytes()).hexdigest()
        (target / ".zenexport-install.json").write_text(json.dumps(old_receipt), encoding="utf-8")
        result = run()
        assert result["status"] == "installed" and result["backup"]
        assert not retired.exists() and custom.read_bytes() == b"keep-this-file"
        steps.append("upgrade replaces an older receipt and removes obsolete owned runtime files")
        code = target / "zenexport/addin.py"
        code.write_bytes(b"damaged-installation")
        result = run()
        assert result["status"] == "installed" and result["backup"]
        assert hashlib.sha256(code.read_bytes()).hexdigest() == receipt["files"]["zenexport/addin.py"]
        assert custom.read_bytes() == b"keep-this-file"
        steps.append("repair restores runtime and preserves custom files with a backup")
        assert run("--uninstall")["status"] == "uninstalled"
        assert not (target / "ZenExport.py").exists()
        assert custom.read_bytes() == b"keep-this-file"
        assert settings.read_bytes() == b'{"private_settings": true}'
        assert project.read_bytes() == b"user-model-must-not-change"
        steps.append("uninstall preserves custom files, user settings and CAD/STL exports")
        assert run()["status"] == "installed"
        assert custom.read_bytes() == b"keep-this-file"
        assert run("--uninstall")["status"] == "uninstalled"
        steps.append("reinstall after uninstall works even when custom files were retained")
        # Installation into unrelated content must fail without changing it.
        unrelated = home / "unrelated"
        unrelated.mkdir()
        note = unrelated / "important.txt"
        note.write_bytes(b"unrelated-content")
        assert run("--target", str(unrelated), expected=1)["status"] == "error"
        assert note.read_bytes() == b"unrelated-content"
        steps.append("unrelated nonempty target is refused")
        print(json.dumps({"platform": sys.platform, "executable": str(executable),
                          "version": receipt["version"], "headless_checks": steps}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    smoke(parser.parse_args().executable)
