# Development and live acceptance

The runtime uses Python's standard library and Fusion's bundled `adsk` API.
Python 3.10+ is required. Local tests ran on 3.11/3.13; Windows CI also passed on 3.10/3.13.

## Local checks

```powershell
py -3.13 -m unittest discover -s tests -v
py -3.13 -m compileall -q ZenExport.py zenexport tools tests
py -3.13 -m venv .venv
./.venv/Scripts/python.exe -m pip install ruff==0.14.1
./.venv/Scripts/python.exe -m ruff check .
py -3.13 tools/build_bundle.py
```

Check member availability in an installed Fusion API without importing its native libraries:

```powershell
py -3.13 tools/verify_fusion_api.py "<Fusion installation>/API/Python/packages/adsk"
```

This checks member existence, not live native behavior. CI runs lint, tests,
compilation and deterministic bundle creation on Windows. Check Actions for the
current result. See HOW_TO_BUILD_MSI.md for distribution; no MSI build is verified.

The diagnostic SHA-256 fingerprint never authorizes skipping a requested backup.
Exports run on Fusion's main thread without custom-event posting. Output reports
use schema 3 and project-relative file paths. Configuration writes are atomic;
the per-user store is intended for one active runtime. `ZENEXPORT_DATA_DIR` permits
isolated development and independent concurrent Fusion runtimes.

## Pending live acceptance

Use a disposable project and retain a separate known-good backup.

- Load, stop and reload twice; confirm one pair of toolbar commands and no duplicate
  interception. Check native Save with interception enabled and disabled.
- Verify the final description prompt, paired revision folders, and opening of the
  project root in Fusion with ZenExport 6.2.0.
- Export two separate Untitled documents to different folders; edit and switch tabs.
- Reopen the first exported F3D and confirm its destination is remembered.
- Change a parameter without adding timeline items; confirm a new numbered revision.
- Test repeated, same-name, renamed, linked and nested hidden components; inspect
  STL body counts, coordinates, units and visibility.
- Force an export or filesystem failure; inspect partial status and a successful retry.
- Test cancellation, missing destinations and linked assemblies. Reopen F3D/STEP
  and compare geometry, parametric history, units and references against the source.
- Measure full/cad/backup on representative small and large designs. Use per-format
  timings before making performance claims.
- Verify macOS and any future MSI install/upgrade/uninstall separately.

Earlier 6.0.3/6.1.0 exports succeeded in the local Fusion session; they do not
establish semantic recovery or final 6.2.0 acceptance. Earlier filesystem migration
preserved payload hashes, which likewise does not prove exported-model validity.
