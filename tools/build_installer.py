"""Build an offline Windows EXE or macOS app with its own embedded Python."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_bundle import build  # noqa: E402


def payload(bundle, destination):
    files = {"INSTALLER_NOTICES.txt": (ROOT / "installer/THIRD_PARTY_NOTICES.txt").read_bytes()}
    with zipfile.ZipFile(bundle) as archive:
        for name in archive.namelist():
            relative = name.removeprefix("ZenExport.bundle/")
            if relative.startswith("Contents/"):
                files[relative.removeprefix("Contents/")] = archive.read(name)
            elif relative in ("README.md", "LICENSE"):
                files[relative] = archive.read(name)
    from zenexport.config import VERSION
    receipt = {"schema": 1, "product": "ZenExport", "version": VERSION,
               "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}}
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted({**files, ".zenexport-install.json":
                                 json.dumps(receipt, sort_keys=True).encode("utf-8")}.items()):
            item = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, data)
    return receipt


def build_installer(output):
    if sys.platform not in ("win32", "darwin"):
        raise RuntimeError("Native installers must be built on Windows or macOS")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    work = output / "installer-build"
    work.mkdir(exist_ok=True)
    receipt = payload(build(output), work / "payload.zip")
    name = "ZenExport-Setup"
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--noupx",
               "--windowed", "--name", name, "--distpath", str(output),
               "--workpath", str(work / "work"), "--specpath", str(work),
               "--add-data", str(work / "payload.zip") + ":."]
    if sys.platform == "win32":
        command.append("--onefile")
    else:
        command.extend(["--onedir", "--osx-bundle-identifier", "labs.eskay.zenexport.setup"])
    command.append(str(ROOT / "installer/setup.py"))
    subprocess.run(command, check=True, cwd=ROOT)
    if sys.platform == "win32":
        artifact = output / ("ZenExport-" + receipt["version"] + "-Windows-Setup.exe")
        (output / (name + ".exe")).replace(artifact)
    else:
        architecture = platform.machine()
        artifact = output / ("ZenExport-" + receipt["version"] + "-macOS-" + architecture + ".zip")
        subprocess.run(["/usr/bin/ditto", "-c", "-k", "--keepParent", str(output / (name + ".app")),
                        str(artifact)], check=True)
    artifact.with_suffix(artifact.suffix + ".sha256").write_text(
        hashlib.sha256(artifact.read_bytes()).hexdigest() + "  " + artifact.name + "\n", encoding="utf-8")
    print("Installer: " + str(artifact))
    return artifact


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    build_installer(parser.parse_args().output)
