"""Integration tests for services/backup_service.py."""

import os

import pytest

from services import ServiceError, backup_service


class TestBackupService:
    def test_backup_database(self, fresh_db):
        path = backup_service.backup_database()
        assert path is not None
        assert os.path.exists(path)
        assert path.endswith(".db")

    def test_backup_database_in_directory(self, fresh_db):
        backup_dir = os.path.join(os.path.dirname(fresh_db), "backup_test")
        path = backup_service.backup_database(directory=backup_dir)
        assert os.path.exists(path)
        assert backup_dir in path

    def test_list_backups(self, fresh_db):
        backup_service.backup_database()
        backups = backup_service.list_backups()
        assert len(backups) >= 1
        assert all(b.endswith(".db") for b in backups)

    def test_restore_database(self, fresh_db):
        # Create a backup first.
        backup_path = backup_service.backup_database()
        # Restore it.
        safety = backup_service.restore_database(backup_path)
        # A safety backup should have been created.
        assert safety is not None and os.path.exists(safety)

    def test_restore_missing_backup_raises(self, fresh_db):
        with pytest.raises(ServiceError, match="not be found"):
            backup_service.restore_database("nonexistent.db")

    def test_restore_invalid_file_raises(self, fresh_db):
        invalid = os.path.join(os.path.dirname(fresh_db), "not_a_backup.txt")
        with open(invalid, "w") as f:
            f.write("this is not a sqlite file")
        with pytest.raises(ServiceError, match="not a valid"):
            backup_service.restore_database(invalid)

    def test_last_backup_display_default(self, fresh_db):
        display = backup_service.last_backup_display()
        assert isinstance(display, str)

    def test_last_backup_display_after_backup(self, fresh_db):
        backup_service.backup_database()
        display = backup_service.last_backup_display()
        assert "No backup" not in display
