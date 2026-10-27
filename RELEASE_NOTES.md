# ZenExport 6.2.0 preview — double-click installation

Released: 2026-10-28.

## 📦 Install without manual folder setup

- **Windows:** open `ZenExport-6.2.0-Windows-Setup.exe`, then restart Fusion.
- **macOS:** unzip the package for Apple silicon (`arm64`) or Intel (`x86_64`),
  open `ZenExport-Setup.app`, then restart Fusion.
- Offline payload and embedded Python; no separate Python installation or admin
  access is required. Linux is not supported by the native Fusion desktop app.
- Automatically selects Fusion's per-user discovery folder and enables startup in
  the manifest. One recognized legacy AddIns installation is updated in place.
- Repeat installs are idempotent; updates and repairs retain settings and exports,
  back up the previous installation, and roll back a failed directory publication.
- Uninstall removes unchanged owned files while keeping custom/edited files.
- New shared installer engine, build tools and native Windows/macOS CI. 79 local
  automated tests pass; the actual Windows EXE passed isolated headless checks.

The STL millimeter fix from 6.1.2 is included. The export workflow is otherwise
unchanged. Stop separately registered development/script copies before using the
installed version. Installation does not close Fusion or modify open designs.

Installers are unsigned/not notarized. Download security prompts and live Fusion
startup/export acceptance remain separate checks; headless success does not prove
those behaviors. The release remains a preview. Build/test details and command-line
uninstall instructions are in HOW_TO_BUILD_MSI.md.

---

# ZenExport 6.1.2 preview — STL scale fix

Released: 2026-10-25.

## 📏 Fixed: tiny STL imports in Bambu Studio and other mm-based slicers

ZenExport previously left `STLExportOptions.unitType` at Fusion's design default.
STL does not store a unit declaration, so coordinates exported in centimeters or
inches could be interpreted as millimeters by the slicer. For example, a 50 mm
part exported as 5 centimeters could appear as 5 mm.

Every new STL export now explicitly sets
`adsk.fusion.DistanceUnits.MillimeterDistanceUnits`. CAD exports and model geometry
are unchanged. If Fusion rejects this setting, the STL is reported as failed
instead of advancing the successful-backup marker.

## ⌨️ Apply the fix

1. Download and extract `ZenExport-6.1.2.zip`; replace the installed runtime files.
2. In Fusion's Scripts and Add-Ins, **Stop → Run ZenExport** to load the update.
3. Open the source design and press **CTRL + S** for a new export revision.
4. Import the **new STL at 100% scale** in Bambu Studio.

Old STL files are not rewritten. Re-export them from the source design; do not
apply a blanket scale multiplier to an archive containing mixed original units.

## Verification and compatibility

- 65 automated tests pass locally, including regression coverage for mm, cm,
  meters and inches and rejection of the STL unit setting.
- The installed Fusion API exposes the required `unitType` property and millimeter
  enum; the expanded surface check verifies 67 API members.
- Requires Fusion's STL `unitType` API, introduced in May 2025.
- Native Fusion export and Bambu Studio dimension verification remain pending;
  the live check was interrupted before execution. Automated translator simulations
  do not establish live geometry or recovery validation.
- The release remains a preview. Existing local/native Save and recovery limits
  described in the README still apply.

API reference: https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_STLExportOptions_unitType.htm

---

# ZenExport 6.1.1 preview

Free and open source under the MIT license. Shared by EsKay-Labs as a gift to the
Fusion and 3D-printing community.

## Changes

- Matching named revisions under `CAD/vNN_description`, `Models/vNN_description`,
  and `_Info/vNN_description`; all STEP/F3D files stay under CAD.
- Optional revision descriptions on each new save. Renaming existing revisions
  through a dedicated command is not implemented.
- Remembered design destinations, portable context identity, and migration of older
  project bindings without repeatedly asking for a new folder.
- Main-thread exports without custom-event posting; protection against duplicate
  exports during reentrant Save events.
- Staged outputs, truthful success/partial/cancelled reports, per-file timings,
  and success markers that advance only after all required files succeed.
- Conflict-checked migration of older layouts, preserved native file bytes,
  original report backups, and a resumable metadata-update journal.
- Modular runtime, full/cad/backup profiles, automated tests, and Windows CI.
- Portable ZIP with source, installation instructions, MIT license, and SHA-256 checksum.

## Download and install

Download `ZenExport-6.1.1.zip` and optionally verify it against its `.sha256` file.
Extract it, copy `ZenExport.bundle/Contents` into a folder named `ZenExport`, and
add that folder through Fusion's Scripts and Add-Ins dialog. Stop older copies
before starting this one. The ZIP README contains the full instructions.

## Verification and limits

63 automated tests pass locally. Lint, bytecode compilation, and deterministic ZIP
packaging pass. [Windows CI on the main branch](https://github.com/EsKay-Labs/ZenExport/actions/runs/40033840353)
also passes on Python 3.10 and 3.13 after correcting test-only path-alias and keyboard-state
assumptions; the released runtime files are unchanged. Earlier 6.0.3/6.1.0 exports succeeded in the local Fusion session.
The final 6.1.1 save workflow and recovery by reopening F3D/STEP still need live
validation. macOS and MSI installation have not been verified; no MSI is supplied.

This is a preview: start with a disposable design and retain separate known-good
backups. Local export does not perform Fusion's native/cloud save or guarantee
clearing its modified flag. Native Save interception is enabled by default and
can be disabled in settings. STLs are visible native BRep parts in component
coordinates. Linked assemblies and external references need additional recovery
validation. The add-in does not change Autodesk licensing limits.
