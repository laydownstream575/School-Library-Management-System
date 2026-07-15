# School Library Management System — Security Considerations

## 1. Document Purpose

This document outlines security considerations, data safety practices, and risk mitigation for the School Library Management System desktop application.

Since this is an offline, single-user desktop application (version 1), the security model is minimal but intentional.

---

## 2. Security Model Overview

| Property | Version 1 |
|---|---|
| Authentication | None. Single-user (librarian/admin). |
| Authorization | Full access for the single user. |
| Network | No network access. Fully offline. |
| Data at rest | SQLite file on local filesystem. |
| Data in transit | N/A — no network communication. |
| Audit trail | Activity logs table (optional, reserved for future use). |

---

## 3. Data Storage Security

### 3.1 Database File

- **Location**: `database/library.db` (inside application folder or user data folder).
- **Format**: Standard SQLite file.
- **Encryption**: None in version 1. SQLite supports SEE (SQLite Encryption Extension) for future use if needed.
- **Portability**: The `.db` file can be copied freely. It is the user's responsibility to protect it.

### 3.2 No Sensitive Data

The application stores:
- Book titles, authors, categories, quantities
- Student names, classes, contact details
- Issue/return records

No passwords, financial data, government IDs, or health information is stored.

### 3.3 Recommendation

If the school requires additional protection, the application folder can be placed on an encrypted volume (BitLocker, VeraCrypt) or the database file can be protected via Windows file permissions.

---

## 4. Data Integrity

### 4.1 Transaction Protection

All critical write operations use SQLite transactions:

- **Issue Book**: Single transaction — fails atomically if any check fails.
- **Return Book**: Single transaction — quantity update and status change are atomic.
- **Excel Import**: Each row is imported individually with error isolation; one bad row does not block valid rows.

### 4.2 Constraint Enforcement

- Database-level `CHECK` constraints prevent invalid quantities.
- `UNIQUE` constraints prevent duplicate student IDs and ISBNs.
- Partial unique index prevents duplicate pending issues.
- `FOREIGN KEY` constraints maintain referential integrity.

### 4.3 Application-Level Validation

- Services validate all inputs before calling the database.
- Validators return specific error messages for each rule violation.
- UI displays validation errors directly, never raw database errors.

---

## 5. Protection Against Data Loss

### 5.1 Backup Options

| Method | Description | Frequency |
|---|---|---|
| Manual SQLite backup | Copies `library.db` to `backups/` with timestamp | On demand (user-initiated) |
| Manual Excel backup | Exports all tables as Excel sheets | On demand (user-initiated) |
| Pre-restore auto-backup | Before restoring a backup, current DB is copied automatically | Automatic |

### 5.2 Safe Delete

- Books and students are **deactivated** (status = `INACTIVE`), never permanently deleted.
- Old issue/return history is preserved even after deactivation.
- Reactivation is possible.

### 5.3 Recovery

- Restore from any SQLite backup file.
- Excel backup can be re-imported as a secondary recovery path.

---

## 6. File Permissions

### 6.1 Required Permissions

| Path | Permission | Reason |
|---|---|---|
| `database/` | Read + Write | DB creation and updates |
| `backups/` | Read + Write | Backup creation and restore |
| `exports/` | Read + Write | Excel export file creation |
| `assets/` | Read only | Icons and images |

### 6.2 Recommendation

The application folder should be placed where the librarian user has full read/write access (e.g., `Documents/LibrarySystem/` or a shared school drive).

---

## 7. Excel Import Safety

### 7.1 Validation Before Import

- Required columns are checked before any data is written.
- Each row is validated independently.
- Non-numeric quantity values are rejected.
- Duplicate student IDs are reported as errors.

### 7.2 Import Summary

After import, a summary is displayed:

```
Import completed.
Valid rows imported: 120
Skipped rows: 5
```

The user can review skipped rows and fix the source file.

---

## 8. Excel Export Safety

- Export files are written to `exports/` folder.
- Files are named with date/time stamps to prevent accidental overwrites.
- Exported files contain no formulas or macros — only data.

---

## 9. Software Supply Chain

### 9.1 Dependencies

| Package | Source | Notes |
|---|---|---|
| PySide6 | PyPI (official Qt bindings) | Commercially licensed (LGPL) |
| openpyxl | PyPI | BSD license |
| sqlite3 | Bundled with Python | Public domain |
| PyInstaller | PyPI | GPL with exception for packaged apps |

All dependencies are installed via `pip` from the official Python Package Index.

### 9.2 Update Policy

- Dependencies should be updated regularly via `pip install --upgrade`.
- `requirements.txt` specifies minimum versions, not exact pins, to allow patch updates.
- PySide6 security patches should be applied promptly.

---

## 10. Future Security Enhancements

| Feature | Benefit | Planned Version |
|---|---|---|
| Login screen with password | Prevents unauthorized access | v2 |
| Role-based access (Admin/Librarian/Viewer) | Limits data modification to authorized roles | v2 |
| Database file encryption | Protects data if laptop is lost | v2+ |
| Activity logging | Audit trail of changes | v2+ |
| Auto-backup on close | Prevent data loss from unexpected shutdown | v2+ |

---

## 11. Security Checklist for Deployment

- [ ] Application runs fully offline (no network capability).
- [ ] No hardcoded passwords or secrets in source code.
- [ ] Database file is in a writable location with user control.
- [ ] Backup folder exists and is writable.
- [ ] Excel import validates all columns and rows.
- [ ] Invalid data does not corrupt the database.
- [ ] Deactivation used instead of permanent delete.
- [ ] Critical write operations use SQLite transactions.
- [ ] No plaintext passwords stored (no login in v1).

---

## 12. Incident Response

For a desktop application with no network access, the following procedures apply:

| Incident | Response |
|---|---|
| Database corruption | Restore from latest backup; if no backup exists, re-import from Excel backup |
| Accidental data deletion | Reactivate the record (it was deactivated, not deleted) |
| Accidental data modification | Edit the record back to correct values |
| File permission error | Move application folder to a location with full read/write access |
| Excel file won't open | Ensure file is saved with `.xlsx` extension; re-export report |
| Suspected data inconsistency | Run reports; compare total vs available quantities against issue records |
