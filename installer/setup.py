"""Native launcher and headless installation engine for Windows and macOS."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile

RECEIPT = ".zenexport-install.json"
REQUIRED = {"ZenExport.py", "ZenExport.manifest", "zenexport/__init__.py", "zenexport/addin.py"}


def safe_name(name):
    path = PurePosixPath(name)
    if (not isinstance(name, str) or not name or path.is_absolute() or "\\" in name
            or ":" in name or any(p in (".", "..", "") or p.endswith((".", " "))
                                  for p in name.split("/"))):
        raise ValueError("Unsafe installer path: " + str(name))
    if path.stem.upper() in {"CON", "PRN", "AUX", "NUL"}:
        raise ValueError("Reserved installer filename: " + name)
    if name not in {"LICENSE", "README.md", "INSTALLER_NOTICES.txt", "ZenExport.py", "ZenExport.manifest"} and not re.fullmatch(
            r"zenexport/[a-z_]+\.py", name):
        raise ValueError("Unexpected installer file: " + name)
    return name


def metadata(value):
    if (value.get("product") != "ZenExport" or value.get("schema") != 1
            or not re.fullmatch(r"\d+\.\d+\.\d+", value.get("version", ""))):
        raise ValueError("Invalid ZenExport installation receipt")
    files = value.get("files")
    if not isinstance(files, dict) or not REQUIRED <= files.keys() or len(files) > 64:
        raise ValueError("Incomplete ZenExport payload")
    for name, digest in files.items():
        safe_name(name)
        if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("Invalid file checksum")
    return value


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_link(path):
    return (path.is_symlink() or (path.exists()
            and bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)))


def check_path(path):
    """Reject Windows junctions as well as symlinks before copying or deleting."""
    path = Path(os.path.abspath(path))
    for item in (path, *path.parents):
        if is_link(item):
            raise ValueError("Installer paths must not use links or junctions: " + str(item))
        if item.exists() and not item.is_dir():
            raise ValueError("Expected an installation directory: " + str(item))
    return path


def check_tree(path):
    for directory, folders, files in os.walk(path, followlinks=False):
        check_path(directory)
        for name in folders:
            check_path(Path(directory) / name)
        for name in files:
            item = Path(directory) / name
            if is_link(item) or not item.is_file():
                raise ValueError("Unsupported file in installation: " + str(item))


def remove_temporary(path, parent, prefix):
    # Recursive deletion is confined to an installer-created sibling directory.
    path, parent = check_path(path), check_path(parent)
    if path.parent != parent or not path.name.startswith(prefix):
        raise ValueError("Refusing to remove a directory outside installer staging")
    check_tree(path)
    shutil.rmtree(path)


@contextmanager
def installation_lock(parent):
    lock = parent / ".zenexport-install.lock"
    if is_link(lock):
        raise ValueError("Installer lock must not be a symlink")
    with lock.open("a+b") as stream:
        stream.seek(0)
        stream.write(b"0")
        stream.flush()
        stream.seek(0)
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def read_payload(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if (len(names) != len(set(names)) or len(names) > 65
                or sum(i.file_size for i in archive.infolist()) > 16 * 1024 * 1024):
            raise ValueError("Invalid installer archive")
        receipt = metadata(json.loads(archive.read(RECEIPT)))
        if set(names) != {RECEIPT, *receipt["files"]}:
            raise ValueError("Installer archive contains unexpected files")
        files = {name: archive.read(name) for name in receipt["files"]}
        for name, content in files.items():
            if hashlib.sha256(content).hexdigest() != receipt["files"][name]:
                raise ValueError("Installer checksum mismatch: " + name)
        manifest = json.loads(files["ZenExport.manifest"])
        if manifest.get("type") != "addin" or manifest.get("runOnStartup") is not True:
            raise ValueError("Fusion add-in must be enabled for startup")
        return receipt, files


def recognized_manual_install(target):
    if not all((target / name).is_file() for name in REQUIRED):
        return False
    try:
        manifest = json.loads((target / "ZenExport.manifest").read_text(encoding="utf-8-sig"))
        return (manifest.get("type") == "addin" and manifest.get("author") == "ZenExport"
                and "_zenexport_runtime" in (target / "ZenExport.py").read_text(encoding="utf-8-sig"))
    except (ValueError, OSError):
        return False


def default_target():
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"]) / "Autodesk"
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support/Autodesk"
    else:
        raise RuntimeError("Autodesk Fusion supports Windows and macOS, not native Linux")
    target = base / "FusionAddins/ZenExport"
    if target.exists():
        return target
    # Reuse one recognized manual AddIns installation, preserving its settings.
    legacy = [base / name / "API/AddIns/ZenExport"
              for name in ("Autodesk Fusion", "Autodesk Fusion 360")]
    matches = [p for p in legacy if recognized_manual_install(p)]
    if len(matches) > 1:
        raise RuntimeError("Multiple manual ZenExport installations found; keep one before updating")
    return matches[0] if matches else target


def install(data, destination):
    receipt, files = read_payload(data)  # Verify before touching an installation.
    target = check_path(destination)
    if target == target.parent:
        raise ValueError("Cannot install at a filesystem root")
    target.parent.mkdir(parents=True, exist_ok=True)
    with installation_lock(target.parent):
        previous = None
        if target.exists():
            check_tree(target)
            if (target / ".git").exists():
                raise ValueError("Destination is a development checkout; its files were not replaced")
            if (target / RECEIPT).exists():
                previous = metadata(json.loads((target / RECEIPT).read_text(encoding="utf-8")))
                if tuple(map(int, previous["version"].split("."))) > tuple(map(int, receipt["version"].split("."))):
                    raise ValueError("A newer ZenExport version is already installed")
            elif any(target.iterdir()) and not recognized_manual_install(target):
                raise ValueError("Destination contains unrelated files; nothing was replaced")
            if previous == receipt and all((target / name).is_file() and digest(target / name) == value
                                           for name, value in receipt["files"].items()):
                return {"status": "unchanged", "version": receipt["version"], "target": str(target)}
        backup = None
        if target.exists() and any(target.iterdir()):
            backup_root = check_path(target.parent / ".zenexport-install-backups")
            backup_root.mkdir(exist_ok=True)
            backup = backup_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-")
                                    + uuid.uuid4().hex + ".zip")
            with zipfile.ZipFile(backup, "x", compression=zipfile.ZIP_DEFLATED) as archive:
                for item in sorted(target.rglob("*")):
                    if item.is_file():
                        archive.write(item, item.relative_to(target).as_posix())
        stage = Path(tempfile.mkdtemp(prefix=".zenexport-stage-", dir=target.parent))
        old = target.parent / (".zenexport-old-" + uuid.uuid4().hex)
        try:
            if target.exists():
                shutil.copytree(target, stage, dirs_exist_ok=True)
            # Remove obsolete owned code from the new tree, retaining it in backup.
            for name in (previous or {}).get("files", {}):
                if name not in files:
                    (stage / name).unlink(missing_ok=True)
            for name, content in files.items():
                path = stage / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            (stage / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            for name, value in receipt["files"].items():
                if digest(stage / name) != value:
                    raise ValueError("Installed file checksum mismatch: " + name)
            if target.exists():
                target.rename(old)
            try:
                stage.rename(target)
            except OSError:
                if old.exists():
                    old.rename(target)
                raise
        finally:
            if stage.exists():
                remove_temporary(stage, target.parent, ".zenexport-stage-")
        if old.exists():
            remove_temporary(old, target.parent, ".zenexport-old-")
        return {"status": "installed", "version": receipt["version"], "target": str(target),
                "backup": str(backup) if backup else None, "restart_fusion": True}


def uninstall(destination):
    target = check_path(destination)
    if not target.exists():
        return {"status": "absent", "target": str(target)}
    with installation_lock(target.parent):
        check_tree(target)
        receipt = metadata(json.loads((target / RECEIPT).read_text(encoding="utf-8")))
        preserved = []
        for name, value in receipt["files"].items():
            path = target / name
            if path.exists():
                if digest(path) == value:
                    path.unlink()
                else:
                    preserved.append(name)
        (target / RECEIPT).unlink()
        for directory, _, _ in os.walk(target, topdown=False):
            if not any(Path(directory).iterdir()):
                Path(directory).rmdir()
        if target.exists():
            # Retain ownership when user files remain, so a later reinstall does
            # not mistake this known directory for an unrelated destination.
            receipt["uninstalled"] = True
            (target / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return {"status": "uninstalled", "target": str(target), "modified_files_preserved": preserved}


def notify(message, error=False):
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, "ZenExport Setup", 0x10 if error else 0x40)
    elif sys.platform == "darwin":
        escaped = message.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(["/usr/bin/osascript", "-e", 'display dialog "' + escaped
                        + '" with title "ZenExport Setup" buttons {"OK"} default button "OK"'], check=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install ZenExport for the current user, offline.")
    parser.add_argument("--silent", action="store_true", help="No windows or dialogs")
    parser.add_argument("--target", type=Path, help="Explicit isolated installation directory")
    parser.add_argument("--uninstall", action="store_true", help="Remove unchanged installed payload files")
    parser.add_argument("--report", type=Path, help="Write the result as JSON")
    args = parser.parse_args(argv)
    try:
        target = args.target if args.target is not None else default_target()
        if args.uninstall:
            result = uninstall(target)
            message = "ZenExport removed. Your project exports and per-user settings were kept."
        else:
            payload = Path(__file__).with_name("payload.zip").read_bytes()
            result = install(payload, target)
            message = ("ZenExport " + result["version"] + " is ready!\n\n"
                       "Restart Fusion, open your design and press CTRL + S.\n"
                       "No manual folder setup is needed.\n\nInstalled in:\n" + str(target))
        code = 0
    except Exception as error:
        result, code = {"status": "error", "error": str(error)}, 1
        message = "ZenExport could not complete setup:\n\n" + str(error)
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if sys.stdout is not None:
        print(json.dumps(result))
    if not args.silent:
        notify(message, error=bool(code))
    return code


if __name__ == "__main__":
    sys.exit(main())
