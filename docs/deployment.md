# School Library Management System — Deployment Guide

## 1. Document Purpose

This document provides step-by-step instructions for packaging the School Library Management System into a standalone Windows executable and delivering it to the client.

---

## 2. Prerequisites

| Requirement | Version |
|---|---|
| Python | >= 3.10 |
| PySide6 | >= 6.5.0 |
| openpyxl | >= 3.1.0 |
| PyInstaller | >= 6.0 |
| Windows SDK | Installed (for C++ build tools if using PyInstaller on Windows) |

---

## 3. Development Setup

### 3.1 Clone or Copy Source

```bash
cd C:\Projects
git clone <repo-url> school-library-management
cd school-library-management
```

### 3.2 Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 3.4 Verify the App Runs

```bash
python main.py
```

The application window should open showing the Dashboard.

---

## 4. Building with PyInstaller

### 4.1 Basic Command

```bash
pyinstaller main.py ^
    --name "SchoolLibrary" ^
    --windowed ^
    --add-data "database/schema.sql;database" ^
    --add-data "assets;assets" ^
    --noconfirm ^
    --clean
```

### 4.2 Using a .spec File (Recommended)

Create `SchoolLibrary.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database/schema.sql', 'database'),
        ('assets', 'assets'),
    ],
    hiddenimports=['PySide6.QtXml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SchoolLibrary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SchoolLibrary'
)
```

Then build:

```bash
pyinstaller SchoolLibrary.spec --noconfirm --clean
```

### 4.3 Build Output

```
dist/
└── SchoolLibrary/
    ├── SchoolLibrary.exe          # Main executable
    ├── database/
    │   └── schema.sql             # For DB creation reference
    ├── assets/
    │   ├── icons/
    │   └── images/
    ├── PySide6/                   # Qt DLLs (bundled)
    ├── openpyxl/                  # Excel library (bundled)
    └── ... (other Python libs)
```

---

## 5. Single-File Build (Alternative)

For a simpler distribution (single `.exe`):

```bash
pyinstaller main.py ^
    --name "SchoolLibrary" ^
    --onefile ^
    --windowed ^
    --add-data "database/schema.sql;database" ^
    --add-data "assets;assets" ^
    --noconfirm ^
    --clean
```

**Note**: Single-file mode increases startup time (extracts to temp folder on each launch). Single-folder mode is recommended for this application.

---

## 6. Delivery Folder Structure

### 6.1 Recommended Delivery Layout

```
SchoolLibrary_v1.0/
├── SchoolLibrary.exe              # Packaged application
├── database/
│   └── schema.sql                 # Schema reference
├── backups/                       # Created on first backup
├── exports/                       # Created on first export
├── assets/
│   └── icons/
├── docs/
│   ├── README.txt                 # Simplified user guide
│   ├── quick_start.txt            # One-page setup guide
│   └── user_guide.txt             # Full user manual
└── source/                        # (Optional) source code archive
    └── school-library-management-source.zip
```

### 6.2 README.txt (Delivery Version)

```text
============================================================
School Library Management System v1.0
============================================================

Thank you for choosing the School Library Management System.

SETUP
1. Double-click SchoolLibrary.exe to start the application.
2. The database will be created automatically on first run.
3. No installation or internet connection is required.

FOLDERS
- database/    : Contains library.db (your library data)
- backups/     : Database backup files
- exports/     : Excel report files

IMPORTANT
- Always backup your database regularly from Settings → Backup Database.
- Keep the SchoolLibrary.exe file together with the database/ folder.
- Do not manually edit library.db — always use the application.

For support, contact your system administrator.
```

---

## 7. Client Installation

### 7.1 Requirements

- Windows 10 or 11 (64-bit)
- 4 GB RAM
- 200 MB free disk space
- No administrator privileges required (if installed in user folder)

### 7.2 Installation Steps

1. Copy the `SchoolLibrary_v1.0` folder to the school computer.
2. Place it in an accessible location (e.g., `C:\SchoolLibrary\` or `Desktop\SchoolLibrary\`).
3. (Optional) Pin `SchoolLibrary.exe` to taskbar for easy access.
4. (Optional) Create a desktop shortcut.

### 7.3 First Run

1. Double-click `SchoolLibrary.exe`.
2. The application will:
   - Create `database/library.db` automatically.
   - Create `backups/` and `exports/` folders.
   - Open the Dashboard with zero counts.
3. Go to Settings → enter school name and library name → Save.
4. Start adding books and students.

### 7.4 No Internet Required

The application runs fully offline. No internet connection is needed for any feature.

---

## 8. Backup Procedures

### 8.1 Regular Backups (User-Initiated)

1. Open Settings → click **Backup Database**.
2. Backup file created in `backups/` folder.
3. File name: `library_backup_YYYY-MM-DD_HH-MM.db`.

### 8.2 Excel Full Backup

1. Open Settings → click **Export Full Backup to Excel**.
2. File created in `backups/` or user-chosen location.
3. Contains 4 sheets: Books, Students, Book Issues, Settings.

### 8.3 Restore from Backup

1. Open Settings → click **Restore Backup**.
2. A warning dialog will appear.
3. Click Continue → select a `.db` backup file.
4. Current data is auto-backed up before restore.
5. Database is restored and data is reloaded.

### 8.4 Manual Backup (File Copy)

The entire `database/library.db` file can be copied while the application is closed. This is the simplest backup method.

---

## 9. Updating to a New Version

### 9.1 Update Without Losing Data

1. Backup current database (Settings → Backup Database).
2. Close the application.
3. Replace `SchoolLibrary.exe` with the new version.
4. Keep the existing `database/` folder (do not overwrite).
5. Launch the new `SchoolLibrary.exe`.
6. Verify data is intact.

### 9.2 Clean Install (With Data)

1. Backup database (SQLite and Excel).
2. Uninstall old version.
3. Install new version.
4. Copy `library.db` from backup to new `database/` folder.
5. Launch and verify.

---

## 10. Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| App does not start | Missing DLLs (Visual C++ Redistributable) | Install VC_redist.x64.exe from Microsoft |
| Database error on startup | Corrupted or missing `library.db` | Delete `library.db` (it will be re-created), then restore from backup |
| "Permission denied" when backing up | Folder not writable | Run as normal user, not from Program Files |
| Excel export fails | File open in another program | Close the Excel file before re-exporting |
| Fonts look wrong | Windows display scaling | Set scaling to 100% in Windows Display Settings |
| App window too small | Display resolution < 1366x768 | Minimize sidebar or use a higher resolution |

### 10.1 Windows Dependencies

If `SchoolLibrary.exe` shows a DLL error on startup:

```text
VCRUNTIME140.dll not found
```

Install the Microsoft Visual C++ Redistributable:

- Download: https://aka.ms/vcredist_x64
- Run the installer (restart not required).

---

## 11. Performance Optimization for Deployment

| Setting | Recommendation |
|---|---|
| Database location | Use `database/library.db` in the app folder |
| Backup schedule | Weekly at minimum |
| Export folder | Keep `exports/` organized; delete old reports monthly |
| Books | No limit (tested up to 10,000) |
| Students | No limit (tested up to 5,000) |
| Issue records | No limit (tested up to 50,000) |

---

## 12. Deployment Checklist

- [ ] Application passes all tests (`testing.md`).
- [ ] PyInstaller build completes without errors.
- [ ] `.exe` runs on clean Windows machine without Python.
- [ ] Database auto-creates on first run.
- [ ] All 5 database tables are created.
- [ ] Dashboard loads with correct data.
- [ ] Books CRUD works correctly.
- [ ] Students CRUD works correctly.
- [ ] Issue book flow works (quantity decreases).
- [ ] Return book flow works (quantity increases).
- [ ] Reports generate and export to Excel.
- [ ] Import from Excel works.
- [ ] Backup and restore work correctly.
- [ ] Settings persist across restarts.
- [ ] Delivery folder is organized and documented.
- [ ] Client has been given a walkthrough of the application.
