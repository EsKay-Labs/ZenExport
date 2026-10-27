# Building and validating ZenExport distribution

## Native offline installers (6.2.0)

Build each installer on its native OS with Python 3.13:

```powershell
python -m pip install -r requirements-build.txt
python tools/build_installer.py
```

Windows creates `dist/ZenExport-6.2.0-Windows-Setup.exe`: a windowed, self-contained
EXE with embedded Python and the complete offline payload. It does not request
administrator access. macOS creates `ZenExport-Setup.app` and an architecture-labelled
ZIP (`arm64` or `x86_64`) with executable permissions preserved by `ditto`.
Build separately on each Mac architecture. No native Linux target is provided.
Every distributable has a `.sha256` sidecar.

The default target is the current user's `Autodesk/FusionAddins/ZenExport` directory,
under Windows APPDATA or macOS Library/Application Support. Fusion documents this as
an automatic discovery path. The installed manifest sets `runOnStartup: true`.
One recognized legacy AddIns installation is adopted instead if present. Multiple
legacy copies, unrelated nonempty targets, links/junctions and development checkouts
are refused; separately registered source copies under Scripts remain untouched.

The shared engine verifies the embedded SHA-256 payload, stages writes, backs up the
previous installation in a sibling `.zenexport-install-backups` directory, and rolls
back a failed directory publication. Unknown custom files survive upgrade. The
receipt `.zenexport-install.json` records file ownership: uninstall only deletes
unchanged owned files and preserves user edits, settings, logs and exported projects.
The sibling lock file remains available for coordination. Upgrades refuse downgrades.
No registry, system-wide settings, network request or Fusion preference edit is needed.

### Headless verification of the actual executable

Windows:

```powershell
python tools/test_installer_headless.py dist/ZenExport-6.2.0-Windows-Setup.exe
```

macOS:

```sh
python tools/test_installer_headless.py dist/ZenExport-Setup.app/Contents/MacOS/ZenExport-Setup
```

The smoke test uses an isolated temporary user profile with spaces/Greek characters,
limits PATH so no external Python is available, and tests automatic target discovery,
payload hashes, repeat installation, upgrade, repair, backups, uninstall and unrelated
folder refusal. It verifies private settings and CAD/STL fixtures remain unchanged.
It does not launch, terminate or automate Fusion. Unit tests also cover failed-publish
rollback, downgrades, malicious payload paths, symlinks/Windows junctions and adoption.
GitHub Actions builds and runs these tests on Windows, Apple silicon and Intel macOS.

For unattended deployment, the EXE/app executable accepts `--silent`, `--target PATH`,
`--report result.json`, and `--uninstall`. Normal double-click installation needs no
arguments. To uninstall, run the same installer executable with `--silent --uninstall`;
add `--target` only if using an explicitly overridden installation path.

Installers are currently unsigned/ad-hoc signed and not notarized. User-facing
SmartScreen/Gatekeeper prompts and Fusion discovery/startup require separate live
acceptance. Do not bypass OS protections or claim that CI validates downloaded-app
approval. Future signing must use the project's own trusted signing identities.
The packaged INSTALLER_NOTICES.txt includes Python and PyInstaller licensing notices.


## Portable bundle (verified)

Run from the repository root with Python 3.10 or newer:

```powershell
py -3.13 tools/build_bundle.py
```

This creates `dist/ZenExport-6.2.0.zip` and a SHA-256 sidecar. Extract the ZIP to obtain
`ZenExport.bundle`. The bundle includes PackageContents.xml, the Fusion entry point,
its .manifest, all eight runtime modules, the README, and the MIT license. It excludes session_config.json,
per-user configuration, logs, tests, development tools, and unrelated project files.
Repeated builds from identical source bytes with the same Python/zlib toolchain
produce identical ZIP bytes.

Bundle generation and payload completeness are tested. Fusion's discovery and loading
of this bundle have not been tested during the infrastructure refactor. Retain the
manual Scripts and Add-Ins loading route until the live acceptance checklist passes.

## Optional Windows MSI (source corrected; build/install pending)

`installer_source.wxs` targets WiX v3 syntax and a machine-wide 64-bit installation
under `C:\ProgramData\Autodesk\ApplicationPlugins\ZenExport.bundle`.
WiX is not installed in the current environment, so no MSI was produced or installed.
Use an existing trusted WiX v3 toolchain if MSI packaging is required.

From the repository root, with the WiX tools available on PATH:

```powershell
New-Item -ItemType Directory -Path dist -Force
candle.exe -arch x64 installer_source.wxs -out dist/installer_source.wixobj
light.exe dist/installer_source.wixobj -out dist/ZenExport-6.2.0.msi
```

The source now includes each runtime file as an individual installer component and
never installs personal context state. Runtime settings/logs are created separately
in the user's writable ZenExport data directory. The original UpgradeCode is retained.
The product version, bundle version, and Python runtime version are all 6.2.0.

## Release acceptance

1. Run automated checks in README, and create the bundle.
2. Compile/link MSI if distributing one, inspect its payload, and test install,
   upgrade, and uninstall on a clean Windows environment.
3. Confirm Fusion discovers exactly one installed copy. Stop any development copy
   before loading the installed one.
4. Complete the README live acceptance checklist, including reopening the first F3D
   and a linked assembly recovery test.
5. Sign distributable installers through the project's release process, if applicable.

Do not infer live Fusion compatibility or successful MSI installation from ZIP creation
or XML parsing alone.
