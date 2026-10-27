# Project plan

Updated: 2026-10-28.

## Current focus

Audit and infrastructure implementation are complete for the code and automated
checks. Production acceptance remains pending inside Fusion; do not represent it as
verified. Detailed findings are in `.agent/knowledge/architecture.md`.

## Completed

- [x] 6.2.0: implement an offline per-user installer with embedded Python, automatic
      Fusion target selection, startup manifest, staged upgrades/rollback, backups,
      repair and ownership-aware uninstall. Add 14 installer regression tests and
      isolated frozen-executable headless checks; native CI covers Windows/macOS.
- [x] 6.1.2: explicitly export STL coordinates in millimeters and add regression
      coverage for mm/cm/m/inch defaults and rejected unit settings (65 tests).
- [x] 6.1.1: implement the clarified layout CAD/revision and Models/revision with
      identical labels; group reports under _Info/revision and open the project root.
- [x] Reorganize existing patterns v02/v03/v04 exports; verify 24 native/mesh/preview
      payloads remain byte-identical, back up the previous tree, and remove empty Revisions.
- [x] Add conflict/path-safety and interruption recovery checks for layout migration.
- [x] 6.1.0: organize each new revision into CAD (all STEP/F3D), Models (STL),
      and _Info (preview/reports); retain numbering across legacy CAD history.
- [x] Offer an optional revision description on save; support Greek text, empty
      descriptions, cancellation before changes, and concurrent named reservations.
- [x] 6.0.3: restore compatibility with session_config.json; migrate legacy bindings
      without changing the original, resume existing histories without folder prompts,
      and offer an existing-folder choice only for ambiguous matches.
- [x] 6.0.2: remove failed custom-event posting and restore synchronous command-handler
      exports; validate the document before cancelling Save and guard reentrant calls.
- [x] Add a regression environment where custom-event registration succeeds but posting
      always returns False, matching the live 6.0.1 report.
- [x] Read and map the actual working tree, including pre-existing local changes.
- [x] Preserve the original edited entry point in `.git/ZenExport.pre-infrastructure.py`.
- [x] Split Fusion integration, configuration, context/model traversal, filesystem
      operations, and export orchestration into an isolated runtime package.
- [x] Replace unsafe count-based skip behavior with explicit backup creation.
- [x] Bind portable context identity before the first archive; avoid name/revision identity.
- [x] Preserve distinct same-name entities and deduplicate repeated native part exports.
- [x] Keep exports on Fusion's main thread; clean up owned events on stop/destroy.
- [x] Add complete version snapshots, staged outputs, truthful reports, timings, and logs.
- [x] Add full/cad/backup profiles and mesh quality settings.
- [x] Add regression tests, lint configuration, and a Windows CI workflow.
- [x] Build a deterministic bundle excluding personal state; repair package XML/MSI sources.
- [x] Document migration, output layout changes, limitations, and acceptance procedure.
- [x] Publish all source changes and the 6.1.1 preview ZIP with MIT license and checksum.
- [x] Correct test path comparisons for Windows short-name aliases found by the first CI run.
- [x] Confirm corrected CI succeeds on Windows with Python 3.10 and 3.13 (run 40033840353).
- [x] Share the preview on three permitted Reddit communities and record verified
      URLs and publication limits in PUBLICATION_LOG.md.
- [x] Refresh the maker-facing README and all three published Reddit bodies with
      CTRL + S, emojis and the corrected project-root diagram; update the user's
      original r/3Dprinting post and verify each saved result. Record r/maker's
      self-promotion restriction without submitting a promotional post there.

## Required validation outside automated mocks

- [ ] Confirm installed 6.2.0 is discovered and started exactly once by a fresh
      Fusion session, and validate downloaded installer prompts/signing separately.
- [ ] Verify 6.1.2 STL dimensions against the Fusion source and Bambu Studio at
      100% scale; the attempted live check was interrupted before execution.
- [ ] Verify the 6.1.1 description prompt, paired revision folders, and project opening
      in Fusion on the next real save.
- [ ] Load/reload and real Save interception on the installed Fusion version.
- [ ] Retry 6.0.2 after Stop/Run; 6.0.0 and 6.0.1 failed before export while posting events.
- [ ] Verify 6.0.3 resumes real legacy archives (including patterns_v01) after Stop/Run.
- [ ] Reopen exported F3D/STEP and compare geometry, history, references, and units.
- [ ] Verify two Untitled tabs, repeated/hidden components, cancellation, and recovery.
- [ ] Measure per-format performance on representative small/medium/large projects.
- [ ] Compile, sign if required, and install/upgrade/uninstall the optional MSI.

## Prioritized backlog

1. Settings UI and independent format toggles, guided by live measurements.
2. Explicit linked-assembly/F3D/F3Z recovery policy, configurations, and mesh bodies.
3. Incremental derived exports with conservative invalidation and a complete F3D backup.
4. Explicit STL units and optional assembly-space mesh exports/3MF.
5. Version browser and opt-in retention after recovery is proven.
6. Cross-process context coordination if concurrent independent Fusion instances are needed.
