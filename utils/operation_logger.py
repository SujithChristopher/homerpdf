"""Operation logging and duplicate detection for Hospital PDF Manager."""

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class OperationLogger:
    """Manages operation logging and duplicate detection using SQLite database."""

    def __init__(self, db_path: Path):
        """
        Initialize logger and database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None

        # Ensure parent directory exists
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fallback to temp directory
            import tempfile
            self.db_path = Path(tempfile.gettempdir()) / "HospitalPDFManager" / "operations.db"
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Set restrictive file permissions (Windows only)
        if os.name == "nt":
            self._set_file_permissions()

    def _init_database(self):
        """Initialize database with schema and indices."""
        # Check if database exists and is valid
        db_exists = self.db_path.exists()

        try:
            # Connect to database
            self.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=10.0,
            )

            # Enable Write-Ahead Logging for better concurrency
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys=ON")

            # Test integrity if database exists
            if db_exists:
                result = self.conn.execute("PRAGMA integrity_check").fetchone()
                if result[0] != "ok":
                    raise sqlite3.DatabaseError("Database integrity check failed")

            # Create schema if not exists
            self._create_schema()

        except sqlite3.DatabaseError as e:
            if db_exists:
                # Backup corrupted database
                backup_path = self.db_path.with_suffix(".db.corrupted.bak")
                try:
                    shutil.copy2(self.db_path, backup_path)
                    print(f"Database corrupted, backup created: {backup_path}")
                except Exception:
                    pass

                # Delete and recreate
                try:
                    self.db_path.unlink()
                except Exception:
                    pass

                # Retry initialization
                self._init_database()
            else:
                raise

    def _create_schema(self):
        """Create database tables and indices."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation_type TEXT NOT NULL,
            time_point TEXT NOT NULL,
            center_code TEXT NOT NULL,
            hospital_number TEXT NOT NULL,
            pdf_files TEXT NOT NULL,
            merge_flag INTEGER NOT NULL,
            is_duplicate INTEGER NOT NULL,
            reprint_reason TEXT,
            username TEXT,
            operation_hash TEXT NOT NULL,
            file_count INTEGER NOT NULL,
            output_path TEXT
        )
        """

        create_hash_index = """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_operation_hash
        ON operations(operation_hash)
        """

        create_hospital_index = """
        CREATE INDEX IF NOT EXISTS idx_hospital_number
        ON operations(hospital_number)
        """

        create_timestamp_index = """
        CREATE INDEX IF NOT EXISTS idx_timestamp
        ON operations(timestamp)
        """

        self.conn.execute(create_table_sql)
        self.conn.execute(create_hash_index)
        self.conn.execute(create_hospital_index)
        self.conn.execute(create_timestamp_index)
        self.conn.commit()

    def _set_file_permissions(self):
        """Set restrictive Windows ACLs on database file (current user only)."""
        try:
            username = os.getlogin()

            # Remove inherited permissions and grant only current user full control
            subprocess.run(
                [
                    "icacls",
                    str(self.db_path),
                    "/inheritance:r",  # Remove inherited permissions
                    "/grant:r",
                    f"{username}:(F)",  # Grant current user full control
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, Exception) as e:
            # Log warning but don't fail - file will use default permissions
            print(f"Warning: Could not set restrictive permissions: {e}")

    @staticmethod
    def calculate_operation_hash(
        time_point: str,
        center_code: str,
        hospital_number: str,
        pdf_files: list[str],
        operation_type: str,
        merge_flag: bool,
    ) -> str:
        """
        Calculate SHA256 hash for duplicate detection (order-independent).

        Args:
            time_point: Time point (A0/A1/A2)
            center_code: Center code (CMC/MNP/LDH)
            hospital_number: Patient hospital number
            pdf_files: List of PDF filenames
            operation_type: Operation type (download/print)
            merge_flag: Whether PDFs were merged

        Returns:
            SHA256 hash string
        """
        # Sort PDF files for order-independent comparison
        sorted_pdfs = sorted(pdf_files)

        # Create composite key
        composite = {
            "time_point": time_point,
            "center_code": center_code,
            "hospital_number": hospital_number,
            "pdf_files": sorted_pdfs,
            "operation_type": operation_type,
            "merge_flag": merge_flag,
        }

        # Convert to JSON string (sorted keys for consistency)
        json_str = json.dumps(composite, sort_keys=True)

        # Calculate SHA256 hash
        return hashlib.sha256(json_str.encode()).hexdigest()

    def check_duplicate(
        self,
        time_point: str,
        center_code: str,
        hospital_number: str,
        pdf_files: list[str],
        operation_type: str,
        merge_flag: bool,
    ) -> Optional[dict]:
        """
        Check if operation is duplicate.

        Args:
            time_point: Time point (A0/A1/A2)
            center_code: Center code (CMC/MNP/LDH)
            hospital_number: Patient hospital number
            pdf_files: List of PDF filenames
            operation_type: Operation type (download/print)
            merge_flag: Whether PDFs will be merged

        Returns:
            None if not duplicate, else dict with previous operation details
        """
        # Calculate operation hash
        operation_hash = self.calculate_operation_hash(
            time_point, center_code, hospital_number, pdf_files, operation_type, merge_flag
        )

        # Query database for matching hash
        try:
            cursor = self.conn.execute(
                """
                SELECT id, timestamp, operation_type, time_point, center_code,
                       hospital_number, pdf_files, merge_flag, username
                FROM operations
                WHERE operation_hash = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (operation_hash,),
            )

            row = cursor.fetchone()

            if row:
                return {
                    "id": row[0],
                    "timestamp": row[1],
                    "operation_type": row[2],
                    "time_point": row[3],
                    "center_code": row[4],
                    "hospital_number": row[5],
                    "pdf_files": json.loads(row[6]),
                    "merge_flag": bool(row[7]),
                    "username": row[8],
                }

            return None

        except sqlite3.Error as e:
            print(f"Error checking duplicate: {e}")
            return None

    def log_operation(
        self,
        time_point: str,
        center_code: str,
        hospital_number: str,
        pdf_files: list[str],
        operation_type: str,
        merge_flag: bool,
        is_duplicate: bool,
        reprint_reason: Optional[str],
        output_path: Optional[str],
    ) -> int:
        """
        Log operation to database.

        Args:
            time_point: Time point (A0/A1/A2)
            center_code: Center code (CMC/MNP/LDH)
            hospital_number: Patient hospital number
            pdf_files: List of PDF filenames
            operation_type: Operation type (download/print)
            merge_flag: Whether PDFs were merged
            is_duplicate: Whether this is a duplicate operation
            reprint_reason: Reason for duplicate (if applicable)
            output_path: Where files were saved (None for print)

        Returns:
            Record ID of inserted operation
        """
        # Calculate operation hash
        operation_hash = self.calculate_operation_hash(
            time_point, center_code, hospital_number, pdf_files, operation_type, merge_flag
        )

        # Get current timestamp (ISO 8601 format)
        timestamp = datetime.now().isoformat()

        # Get username
        try:
            username = os.getlogin()
        except Exception:
            username = os.getenv("USERNAME") or os.getenv("USER") or "unknown"

        # Prepare data
        pdf_files_json = json.dumps(sorted(pdf_files))
        file_count = len(pdf_files)

        # Insert with retry logic for concurrent access
        max_retries = 3
        for attempt in range(max_retries):
            try:
                cursor = self.conn.execute(
                    """
                    INSERT INTO operations (
                        timestamp, operation_type, time_point, center_code,
                        hospital_number, pdf_files, merge_flag, is_duplicate,
                        reprint_reason, username, operation_hash, file_count,
                        output_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        timestamp,
                        operation_type,
                        time_point,
                        center_code,
                        hospital_number,
                        pdf_files_json,
                        1 if merge_flag else 0,
                        1 if is_duplicate else 0,
                        reprint_reason,
                        username,
                        operation_hash,
                        file_count,
                        output_path,
                    ),
                )

                self.conn.commit()
                return cursor.lastrowid

            except sqlite3.IntegrityError:
                # Hash collision (duplicate) - this is expected, just update
                # with the new timestamp and reason
                cursor = self.conn.execute(
                    """
                    UPDATE operations
                    SET timestamp = ?, is_duplicate = 1, reprint_reason = ?
                    WHERE operation_hash = ?
                    """,
                    (timestamp, reprint_reason, operation_hash),
                )
                self.conn.commit()
                return cursor.lastrowid

            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    # Database locked, retry with exponential backoff
                    time.sleep(0.1 * (attempt + 1))
                else:
                    raise

        raise sqlite3.OperationalError("Failed to log operation after retries")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Cleanup database connection on deletion."""
        self.close()
