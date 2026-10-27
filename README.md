# 🛠️ ZenExport
### ⌨️ CTRL + S. Keep your CAD and printable parts together.

**Local F3D, STEP and STL exports for Autodesk Fusion — organized into matching, named revisions.**

Built by a maker for the repetitive part between changing a design and preparing it
for printing. Shared by **EsKay-Labs** as a free gift to the community. 🎁

[📦 Download 6.2.0 Preview](https://github.com/EsKay-Labs/ZenExport/releases/tag/v6.2.0) ·
[🐛 Report an issue](https://github.com/EsKay-Labs/ZenExport/issues) ·
[📜 MIT License](LICENSE)

## ⌨️ Your familiar shortcut, with local exports

With ZenExport's Save interception enabled, **CTRL + S starts a new local export
revision** for your active Fusion design.

Choose the project destination on your first export. After that, ZenExport remembers it.

```text
          ⌨️ CTRL + S
                │
       🏷️ Optional revision note
                │
        📁 MyProjectFolder/
                │
                ├── CAD/
                │   └── v05_M6 holes/
                │       └── F3D + STEP
                │
                ├── Models/
                │   └── v05_M6 holes/
                │       └── STL files
                │
                └── _Info/
                    └── v05_M6 holes/
                        └── Preview + reports
```

**How Save behaves:** interception is enabled by default. It replaces the intercepted
native Save with ZenExport's local export workflow; it does not also perform Fusion's
native/cloud save. Disable interception in settings if you prefer to use the
**ZenExport Save** toolbar command separately.

## ✨ What's useful about it?

- 💾 **Keep your source:** whole-design F3D archives and STEP copies.
- 🖨️ **Prepare your parts:** separate STL files for visible native solid bodies.
- 🔢 **Keep earlier revisions:** each requested export creates a fresh numbered revision.
- 🏷️ **Remember what changed:** descriptions such as `M6 holes` or `more clearance`.
- 📂 **Remember the destination:** return to the same project folder on subsequent saves.
- 📸 **Recognize each version:** optional viewport previews.
- 🔍 **See what happened:** per-file export results and timings.
- 🎛️ **Choose the workload:** full exports, CAD only, or F3D backup only.

### 📏 6.1.2 fix: correct STL size in Bambu Studio

STL exports now explicitly use **millimeters**, independent of the design's display
units. Earlier versions inherited the design units, which could produce tiny parts
when a slicer interpreted those coordinates as millimeters (for example, 50 mm
written as 5 in centimeters and imported as 5 mm).

After updating, **Stop → Run ZenExport**, press **CTRL + S**, and import the newly
exported STL at **100% scale**. Previously exported STLs are not modified; export
them again from the source design. This uses Fusion's `STLExportOptions.unitType`
API, available since May 2025. Live Fusion/Bambu size verification is still pending.

## 📁 A folder structure you can actually follow

```text
MyProjectFolder/
├── CAD/
│   └── v05_M6 holes/
│       ├── MyProject_v05.f3d
│       ├── MyProject_v05.step
│       └── Components/…
├── Models/
│   └── v05_M6 holes/
│       └── Component/
│           └── Body.stl
└── _Info/
    └── v05_M6 holes/
        ├── _preview.png
        ├── export_manifest.json
        └── export_events.jsonl
```

**Same revision name. Matching CAD and printable parts.** 🧩

The number preserves the sequence; your description explains the change. Greek
descriptions work too. Unsafe filename characters are replaced and long folder
descriptions are shortened; the full description remains in the report.

Descriptions apply to new revisions. A command for renaming existing revisions is
not implemented yet. `_Info` also holds small helpers for numbering and migration;
keep these with the project.

## 🚀 Get started

### Windows: double-click and go 🪟

Download **ZenExport-6.2.0-Windows-Setup.exe** from the
[release downloads](https://github.com/EsKay-Labs/ZenExport/releases/tag/v6.2.0) and open it.
It installs for your user automatically. **Restart Fusion**, open a design and press
**CTRL + S**. No folder picking, manual copying, Python installation or administrator
access is needed. Setup works offline.

### macOS: open the installer app 🍎

Download the **macOS-arm64 ZIP** for Apple silicon or **macOS-x86_64 ZIP** for Intel
from the same release. Unzip and open **ZenExport-Setup.app**, then restart Fusion.
The app installs the add-in automatically; you do not need to drag files into Fusion
folders. The two packages run natively on their respective processor architectures.

The installers are currently unsigned/not notarized. Windows or macOS may show a
publisher or download-security prompt; headless tests do not verify those prompts.
No native Linux installer is supplied because
[Fusion supports Windows and macOS](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-there-any-way-to-install-Fusion-360-in-Linux.html).

Reopening the installer updates or repairs its installation. Settings and exported
projects are retained, and a previous installation is backed up before replacement.
A recognized existing manual AddIns installation is reused; unrelated folders and
development checkouts are refused. Stop separately registered development/script
copies before using the installed copy so only one ZenExport runs.

<details>
<summary>Portable ZIP / installing directly from source</summary>

1. Download and extract the [portable ZIP](https://github.com/EsKay-Labs/ZenExport/releases/tag/v6.2.0).
2. Copy `ZenExport.bundle/Contents` into a folder named **ZenExport**.
3. In Fusion, open **Utilities → Scripts and Add-Ins** and add that folder.
4. Stop any older ZenExport instance, then run the new one. Optionally enable **Run on Startup**.
5. Open a disposable test design and press **CTRL + S**.
6. Choose your destination and project name, then optionally describe the revision.

Keep these items together:

```text
ZenExport/
├── ZenExport.py
├── ZenExport.manifest
└── zenexport/
    └── all included Python modules
```

You can also install from repository source using that same structure. Run one copy
of ZenExport at a time. Live Fusion discovery/startup still requires acceptance testing.

</details>

The installer uses Fusion's documented automatic-discovery location by default:

- Windows: `%APPDATA%\Autodesk\FusionAddins\ZenExport`
- macOS: `~/Library/Application Support/Autodesk/FusionAddins/ZenExport`

The included manifest enables Run on Startup. An existing recognized installation
in either the older `Autodesk Fusion 360/API/AddIns` or newer `Autodesk Fusion/API/AddIns`
location is updated in place if exactly one is found. Source folders under `Scripts`
are left alone. The installer never closes Fusion or saves/changes your open designs.

### 🧰 Toolbar commands

- **ZenExport Save:** export to the remembered project.
- **ZenExport: Choose Destination:** select a different destination and create an independent project context.

On Windows, holding Shift while invoking native Save also chooses a new destination.
The separate toolbar command does not require that platform-specific shortcut.

## 🏷️ Describe the change — or keep saving

With the description prompt enabled:

```text
CTRL + S → “M6 holes”       → v05_M6 holes
CTRL + S → “more clearance” → v06_more clearance
```

Leave the description blank for a plain numbered revision. Cancel the prompt to
leave without creating that revision.

Want fewer prompts? Set:

```json
"prompt_revision_name": false
```

Your next exports will use names such as `v07`, `v08`, and `v09`. ⚡

## 🎛️ Make it fit your workflow

Settings are created on first run. Stop ZenExport before editing them, then restart it.

- **Windows:** `%LOCALAPPDATA%\ZenExport\config.json`
- **macOS:** `~/Library/Application Support/ZenExport/config.json`

Edit the existing `settings` section and preserve your saved project contexts:

```json
"settings": {
  "intercept_native_save": true,
  "profile": "full",
  "mesh_quality": "high",
  "thumbnail": true,
  "open_folder": true,
  "prompt_revision_name": true
}
```

| Setting | What it controls |
| --- | --- |
| `intercept_native_save` | Route native Save, including CTRL + S on Windows, through ZenExport |
| `profile` | Choose `full`, `cad`, or `backup` |
| `mesh_quality` | Choose `low`, `medium`, or `high` |
| `thumbnail` | Save a viewport preview |
| `open_folder` | Open the project folder after a completed export |
| `prompt_revision_name` | Ask for an optional revision description |

| Profile | Whole-design F3D | Whole-design STEP | Body STLs | Component F3D/STEP |
| --- | --- | --- | --- | --- |
| 🧰 `full` | ✅ | ✅ | ✅ | ✅ |
| 📐 `cad` | ✅ | ✅ | — | — |
| 💾 `backup` | ✅ | — | — | — |

## 🔄 Already have older ZenExport projects?

The update can recover older destination bindings and reorganize supported older
layouts into matching **CAD**, **Models**, and **_Info** revision folders.

Migration checks for conflicting files, preserves native file contents, and keeps
copies of original reports. Interrupted metadata updates can resume from a journal.
If an old export has no reliable revision information, it is retained under
`_Legacy_unversioned`. Only empty old folders are removed.

Existing `session_config.json` bindings are imported without changing the original
file. Ambiguous matches offer a choice of saved destinations. A missing destination
is reported so you can reconnect its drive or deliberately choose another folder.

A copied design can inherit its original project's context. Use **Choose Destination**
when you intend to start an independent project.

## 🔍 When something needs attention

The revision's `_Info` folder contains:

- **`export_manifest.json`:** the export summary and file results.
- **`export_events.jsonl`:** completed per-file outcomes, useful after interruption.
- **`_preview.png`:** the optional viewport image.

The application log, **`zenexport.log`**, lives beside `config.json` and rotates
automatically. Configuration writes use atomic replacement; invalid configuration
is reported rather than silently discarding remembered destinations.

Failed or interrupted attempts can leave a partial revision for inspection. Retrying
uses a new number. The last-success marker advances only when every required export
succeeds. An optional preview failure is recorded separately.

## 🧪 Current release status

**6.2.0 is a preview update.**

**79 automated tests pass locally**, covering simulated Fusion events, filesystem
behavior, migration, packaging, STL units and installer transactions. The frozen
Windows EXE also passed isolated headless install, upgrade, repair and uninstall
checks without Fusion, with private settings and CAD/STL fixtures preserved.
Native CI builds/test-runs the Windows and both macOS installers; check
[GitHub Actions](https://github.com/EsKay-Labs/ZenExport/actions) for this update's result.

Earlier 6.0.3 and 6.1.0 exports succeeded in the local Fusion session. The final 6.1.2
save workflow and full recovery checks by reopening exported F3D/STEP files still
need live validation. Save interception should be checked against your Fusion version.

Start with a disposable design and retain separate known-good backups.

### A few practical details

- Local export does not guarantee clearing Fusion's modified flag or rename an Untitled tab;
  closing the design may still prompt for a native save.
- STL exports cover visible native BRep bodies. Repeated instances share part exports;
  STLs use component coordinates rather than placed assembly coordinates.
- STL coordinates are explicitly exported in millimeters; import new files at 100% scale.
- Linked assemblies, external references and configurations need additional recovery validation.
- Mesh bodies and drawings are outside the per-part export workflow.
- Cancellation takes effect between export files when Fusion delivers it.
- No automatic cleanup deletes older revisions. Full snapshots consume additional disk space.
- Headless installer checks do not establish live Fusion startup, export compatibility
  or Gatekeeper/SmartScreen approval. No MSI is supplied.
- ZenExport does not change Autodesk's licensing requirements or limits.
- Independent concurrent Fusion runtimes should use separate `ZENEXPORT_DATA_DIR` locations.

## 🤝 Made for makers

Useful bug reports include your Fusion version, what you tried, and the relevant
error message. Remove personal paths or project details before sharing logs.

[Open an issue](https://github.com/EsKay-Labs/ZenExport/issues) or contribute an improvement.

For development and packaging details:

- [Development checks and live acceptance](https://github.com/EsKay-Labs/ZenExport/blob/main/DEVELOPMENT.md)
- [Architecture and audit](https://github.com/EsKay-Labs/ZenExport/blob/main/.agent/knowledge/architecture.md)
- [Project plan](https://github.com/EsKay-Labs/ZenExport/blob/main/PROJECT-PLAN.md)
- [Distribution guide](https://github.com/EsKay-Labs/ZenExport/blob/main/HOW_TO_BUILD_MSI.md)
- [Release notes](https://github.com/EsKay-Labs/ZenExport/blob/main/RELEASE_NOTES.md)

**Free. Open source. MIT licensed. Happy making! 🛠️🖨️**
