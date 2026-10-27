# Optional settings, older projects and troubleshooting

You can use ZenExport without editing any settings. Start with the
[installation and first-save guide](https://github.com/EsKay-Labs/ZenExport#readme).

## Optional settings

Settings are created on first run. Stop ZenExport before editing them, then restart it.

- Windows: `%LOCALAPPDATA%\ZenExport\config.json`
- macOS: `~/Library/Application Support/ZenExport/config.json`

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

Set `intercept_native_save` to `false` to keep Fusion's native/cloud Save and invoke
ZenExport separately through its toolbar command. Set `prompt_revision_name` to
`false` for numbered revisions without the description prompt.

| Profile | Whole-design F3D | Whole-design STEP | Body STLs | Component F3D/STEP |
| --- | --- | --- | --- | --- |
| `full` | Yes | Yes | Yes | Yes |
| `cad` | Yes | Yes | No | No |
| `backup` | Yes | No | No | No |

On Windows, holding Shift while invoking native Save chooses a new destination.
The separate **ZenExport: Choose Destination** toolbar command works without that shortcut.
Use it when a copied design should start an independent project instead of inheriting
the original project's context.

## Revision names

Leave the description blank for a numbered revision, or cancel to leave without
creating one. Unsafe filename characters are replaced and long folder descriptions
are shortened; the full description remains in the report. Existing revisions cannot
be renamed through a dedicated command yet. No automatic retention deletes revisions.

## Older projects

ZenExport can recover older destination bindings and reorganize supported older
layouts into matching CAD, Models and _Info revision folders.

Migration checks for conflicting files, preserves native file contents and keeps
copies of original reports. Interrupted metadata updates can resume from a journal.
Exports without reliable revision information are retained under `_Legacy_unversioned`.
Only empty old folders are removed.

Existing `session_config.json` bindings are imported without changing the original.
Ambiguous matches offer a choice of saved destinations. A missing destination is
reported so you can reconnect its drive or deliberately choose another folder.

## Reports and logs

Each revision's `_Info` folder contains:

- `export_manifest.json`: the export summary and file results.
- `export_events.jsonl`: completed per-file outcomes, useful after interruption.
- `_preview.png`: the optional viewport image.

`_Info` also contains helpers for numbering and migration; keep these with the project.
The rotating application log, `zenexport.log`, lives beside `config.json`.
Configuration writes use atomic replacement; invalid configuration is reported
instead of silently discarding remembered destinations.

A failed or interrupted attempt can leave a partial revision. Retrying uses a new
number. The last-success marker advances only when every required export succeeds;
an optional preview failure is recorded separately. Cancellation takes effect between
export files when Fusion delivers it. Full snapshots consume additional disk space.

Independent concurrent Fusion runtimes should use separate `ZENEXPORT_DATA_DIR` locations.
STL units require Fusion's `STLExportOptions.unitType` API, introduced in May 2025.
ZenExport does not change Autodesk's licensing requirements or limits.

## Installation details

The automatic installer uses `%APPDATA%\Autodesk\FusionAddins\ZenExport` on Windows,
or `~/Library/Application Support/Autodesk/FusionAddins/ZenExport` on macOS.
It reuses one recognized installation in an older `Autodesk Fusion 360/API/AddIns`
or newer `Autodesk Fusion/API/AddIns` location if found. Source folders under `Scripts`
are left alone. It does not close Fusion or save/change open designs.

See [build, install and uninstall details](https://github.com/EsKay-Labs/ZenExport/blob/main/HOW_TO_BUILD_MSI.md)
for backups, ownership checks, unattended installation and uninstall commands.
