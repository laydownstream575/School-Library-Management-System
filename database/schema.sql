-- School Library Management System — SQLite Schema
-- All application data lives in this database. Excel is only used for
-- import/export/reports/backup, never as the main store.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- books: book details and quantity tracking
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT,
    book_key TEXT,
    total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0),
    available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (available_quantity <= total_quantity)
);

-- ---------------------------------------------------------------------------
-- students: student / member records
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    class_name TEXT,
    division TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- book_issues: one row per issue; the same row is updated on return
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'ISSUED'
        CHECK (status IN ('ISSUED', 'RETURNED', 'LOST', 'DAMAGED')),
    remarks TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (student_id) REFERENCES students(id),

    CHECK (
        return_date IS NULL
        OR return_date >= issue_date
    )
);

-- ---------------------------------------------------------------------------
-- settings: application configuration (key/value)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT
);

-- ---------------------------------------------------------------------------
-- activity_logs: audit trail of important actions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- migration_audit: records of automated data corrections during schema
-- migrations. status='manual_review_required' means a human must verify.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS migration_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_from INTEGER NOT NULL,
    migration_to INTEGER NOT NULL,
    table_name TEXT NOT NULL,
    row_id INTEGER,
    column_name TEXT NOT NULL DEFAULT '',
    old_value TEXT,
    new_value TEXT,
    status TEXT NOT NULL DEFAULT 'corrected'
        CHECK (status IN ('corrected', 'manual_review_required')),
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------------------------------------------------------------------------
-- Prevent the same student holding the same book twice at once.
-- Partial unique index only applies while status = 'ISSUED'.
-- ---------------------------------------------------------------------------
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_issue
ON book_issues(student_id, book_id)
WHERE status = 'ISSUED';

-- ---------------------------------------------------------------------------
-- Search / filter indexes
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);

CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);

CREATE INDEX IF NOT EXISTS idx_students_code ON students(student_code);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_name);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);

CREATE INDEX IF NOT EXISTS idx_issues_book_id ON book_issues(book_id);
CREATE INDEX IF NOT EXISTS idx_issues_student_id ON book_issues(student_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON book_issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_issue_date ON book_issues(issue_date);
CREATE INDEX IF NOT EXISTS idx_issues_due_date ON book_issues(due_date);
CREATE INDEX IF NOT EXISTS idx_issues_return_date ON book_issues(return_date);

-- ---------------------------------------------------------------------------
-- Default settings (only inserted if not already present)
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO settings (setting_key, setting_value)
VALUES
('school_name', 'ABC Public School'),
('library_name', 'School Library'),
('default_due_days', '7'),
('low_stock_limit', '2'),
('backup_path', 'backups'),
('export_path', 'exports');
