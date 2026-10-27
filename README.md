# 🛠️ ZenExport

### ⌨️ CTRL + S → your CAD files and printable parts, together.

ZenExport is a free Autodesk Fusion add-in that saves local **F3D, STEP and STL**
files into matching, named revision folders. Choose a project folder once, then
keep working and saving. A small gift from **EsKay-Labs** to fellow makers. 🎁

**6.2.0 Preview · Windows & macOS · MIT license**

[📦 Downloads](https://github.com/EsKay-Labs/ZenExport/releases/tag/v6.2.0) ·
[🐛 Report a problem](https://github.com/EsKay-Labs/ZenExport/issues) ·
[📜 License](LICENSE)

## 🚀 1. Choose how to install

Both options install the same add-in. You do **not** need to install Python.
If you already use ZenExport, stop the old copy before switching to the new one.
Run only one copy at a time.

### Option 1: automatic installer

**🪟 Windows**

1. Download [ZenExport-6.2.0-Windows-Setup.exe](https://github.com/EsKay-Labs/ZenExport/releases/download/v6.2.0/ZenExport-6.2.0-Windows-Setup.exe).
2. Open it. The installer selects the folder and copies the files for your user.
3. Restart Fusion.

> **⚠️ Windows warning — please read before downloading**
>
> Windows SmartScreen may show **“Windows protected your PC”** and
> **“Publisher: Unknown publisher.”** This has been observed with this release:
> the installer is **not digitally signed** and has no established publisher reputation.
>
> Automated installation tests do not remove this warning or establish Windows trust.
> **If you prefer not to run the unsigned EXE, use Option 2 below to install manually.**

**🍎 macOS**

1. Download the ZIP for your Mac: [Apple silicon — M1/M2/M3 and later](https://github.com/EsKay-Labs/ZenExport/releases/download/v6.2.0/ZenExport-6.2.0-macOS-arm64.zip)
   or [Intel](https://github.com/EsKay-Labs/ZenExport/releases/download/v6.2.0/ZenExport-6.2.0-macOS-x86_64.zip).
2. Unzip it and open **ZenExport-Setup.app**.
3. Restart Fusion.

The Mac installer is not notarized, so macOS may also warn or block it.
You can use the manual option below instead.

The installers work offline and do not require administrator access. Reopening one
updates or repairs its installation while retaining settings and exported projects.

### Option 2: manual installation — Windows or macOS

Use this option if you prefer to install the files yourself instead of running an installer.

1. Download the [portable ZenExport-6.2.0.zip](https://github.com/EsKay-Labs/ZenExport/releases/download/v6.2.0/ZenExport-6.2.0.zip)
   and extract it.
2. Open **ZenExport.bundle**. Copy its **Contents** folder to a permanent location,
   such as your Documents folder, and rename that copied folder **ZenExport**.
3. In Fusion, open **Utilities → Add-Ins → Scripts and Add-Ins**.
4. Click **+ / Add**, then choose your **ZenExport** folder.
5. Select **ZenExport**, click **Run**, and enable **Run on Startup**.

The folder you select must contain these items together:

```text
ZenExport/
├── ZenExport.py
├── ZenExport.manifest
└── zenexport/
    └── all included Python modules
```

Keep that folder in place after installation. Fusion loads the add-in from it.
Manual installation uses the same code and preview release; it does not run the Setup EXE.

**Linux:** no native package is supplied because
[Autodesk Fusion supports Windows and macOS](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-there-any-way-to-install-Fusion-360-in-Linux.html).

## ⌨️ 2. Make your first save

On macOS, use **⌘ Cmd + S** for the native Save shortcut.

1. Open a disposable test design in Fusion and press **CTRL + S**.
2. Choose where to keep your project and give its folder a name.
3. Optionally describe the revision, for example **M6 holes**, then finish the export.

On later saves, ZenExport remembers the destination and creates a new revision.
Leave the description blank for a number only, or cancel to leave without creating it.

> **How CTRL + S works:** Save interception is enabled by default. ZenExport creates
> local exports **instead of Fusion's native/cloud save**; it does not do both.
> To keep native Save, disable interception and use the **ZenExport Save** toolbar
> command separately. See [optional settings](https://github.com/EsKay-Labs/ZenExport/blob/main/CONFIGURATION.md).

## 📁 3. Find your files

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

- 💾 **CAD:** your Fusion archive and STEP files, including component CAD exports.
- 🖨️ **Models:** individual STL files for visible solid bodies, ready for your slicer.
- 📸 **_Info:** an optional preview and reports showing what exported successfully.

**Matching revision names help you keep the CAD and printable parts together.** 🧩
Greek descriptions work too. Earlier revisions are retained; there is no automatic cleanup.
Descriptions name new revisions; renaming an existing revision is not implemented yet.

STLs are exported in **millimeters**. Import newly exported files in Bambu Studio
at **100% scale**. If you have tiny STLs from before the 6.1.2 fix, export them again
from the source design; updating ZenExport does not rewrite old files.

## 🧰 Everyday controls

- **CTRL + S / ZenExport Save:** export to the remembered project.
- **ZenExport: Choose Destination:** start an independent project in another folder.
- Prefer fewer prompts? You can turn off the revision-description prompt in
  [optional settings](https://github.com/EsKay-Labs/ZenExport/blob/main/CONFIGURATION.md).

## 🧪 What has been checked?

**79 automated tests pass.** The actual Windows EXE and both Mac apps passed
headless installation, upgrade, repair, uninstall and reinstall checks in isolated
profiles. Settings and CAD/STL test files were preserved.
[See the native installer test run](https://github.com/EsKay-Labs/ZenExport/actions/runs/40600617188).

**This is still a preview.** Headless tests do not verify SmartScreen/Gatekeeper
approval or automatic loading inside Fusion. Live checks of startup, the current
save workflow, STL dimensions in a slicer and recovery by reopening F3D/STEP are
still pending. Start with a test design and retain separate known-good backups.

A few useful limits:

- Fusion can still ask for a native save when closing a modified or Untitled design.
- STLs use native component coordinates; repeated instances share part exports.
- Mesh bodies and drawings are outside the per-part export workflow. Linked assemblies,
  external references and configurations need further recovery validation.
- A failed or interrupted export can leave a partial revision. Read its report;
  a retry creates a new number. A partial export is not a complete backup.

## 🤝 Need a hand?

[Report a problem](https://github.com/EsKay-Labs/ZenExport/issues) with your Fusion
version, what you tried and the error message. Remove personal paths/project details
before sharing logs.

- [Settings, older projects and troubleshooting](https://github.com/EsKay-Labs/ZenExport/blob/main/CONFIGURATION.md)
- [Build, install and uninstall details](https://github.com/EsKay-Labs/ZenExport/blob/main/HOW_TO_BUILD_MSI.md)
- [Development checks and live acceptance](https://github.com/EsKay-Labs/ZenExport/blob/main/DEVELOPMENT.md)
- [Release notes](https://github.com/EsKay-Labs/ZenExport/blob/main/RELEASE_NOTES.md)

**Free. Open source. Happy making! 🛠️🖨️**
