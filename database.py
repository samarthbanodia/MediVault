"""
Local SQLite Database Interface for MediSense
Simple authentication-focused implementation
"""

import os
import sqlite3
import uuid
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

class Database:
    """
    SQLite database interface for MediSense
    """

    def __init__(self):
        """Initialize SQLite database"""
        # Create database directory if it doesn't exist
        db_dir = Path("data")
        db_dir.mkdir(exist_ok=True)

        self.db_path = db_dir / "medisense.db"
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        # Initialize tables
        self._init_tables()

    def _init_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                user_type TEXT NOT NULL CHECK (user_type IN ('patient', 'doctor')),
                date_of_birth TEXT,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                address TEXT,
                license_number TEXT UNIQUE,
                specialization TEXT,
                hospital_affiliation TEXT,
                google_id TEXT UNIQUE,
                profile_picture_url TEXT,
                is_verified INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            )
        """)

        # Create medical_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id TEXT PRIMARY KEY,
                record_id TEXT UNIQUE NOT NULL,
                patient_id TEXT NOT NULL,
                patient_age INTEGER,
                date TEXT,
                domain_info TEXT,
                diseases TEXT,
                medications TEXT,
                biomarkers TEXT,
                symptoms TEXT,
                procedures TEXT,
                anomaly_detection TEXT,
                ocr_confidence REAL,
                llm_metadata TEXT,
                historical_biomarkers TEXT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                document_type TEXT,
                document_date TEXT,
                issuing_hospital TEXT,
                issuing_doctor TEXT,
                ocr_text TEXT,
                ocr_confidence REAL,
                processing_status TEXT DEFAULT 'pending',
                clinical_summary TEXT,
                overall_severity INTEGER DEFAULT 0,
                has_critical_alerts INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create biomarkers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS biomarkers (
                id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                biomarker_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                normal_min REAL,
                normal_max REAL,
                is_abnormal INTEGER DEFAULT 0,
                measurement_date TEXT,
                extracted_text TEXT,
                confidence REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES medical_records(id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create medications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                medication_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                duration TEXT,
                route TEXT,
                prescribed_by TEXT,
                prescribed_date TEXT,
                start_date TEXT,
                end_date TEXT,
                extracted_text TEXT,
                confidence REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES medical_records(id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create anomalies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                layer TEXT NOT NULL,
                severity INTEGER NOT NULL,
                is_critical INTEGER DEFAULT 0,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                recommendation TEXT,
                affected_biomarker TEXT,
                detection_date TEXT DEFAULT CURRENT_TIMESTAMP,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES medical_records(id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()
        self._add_patient_age_column()
        self._add_date_column()
        self._add_domain_info_column()
        self._add_diseases_column()
        self._add_medications_column()
        self._add_biomarkers_column()
        self._add_symptoms_column()
        self._add_procedures_column()
        self._add_anomaly_detection_column()
        self._add_ocr_confidence_column()
        self._add_llm_metadata_column()
        self._add_historical_biomarkers_column()
        print("✓ Local SQLite database initialized with all tables")

    def _add_patient_age_column(self):
        """Add patient_age column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'patient_age' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN patient_age INTEGER")
                self.conn.commit()
                print("✓ Added 'patient_age' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding patient_age column: {e}")

    def _add_date_column(self):
        """Add date column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'date' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN date TEXT")
                self.conn.commit()
                print("✓ Added 'date' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding date column: {e}")

    def _add_domain_info_column(self):
        """Add domain_info column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'domain_info' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN domain_info TEXT")
                self.conn.commit()
                print("✓ Added 'domain_info' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding domain_info column: {e}")

    def _add_diseases_column(self):
        """Add diseases column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'diseases' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN diseases TEXT")
                self.conn.commit()
                print("✓ Added 'diseases' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding diseases column: {e}")

    def _add_medications_column(self):
        """Add medications column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'medications' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN medications TEXT")
                self.conn.commit()
                print("✓ Added 'medications' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding medications column: {e}")

    def _add_biomarkers_column(self):
        """Add biomarkers column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'biomarkers' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN biomarkers TEXT")
                self.conn.commit()
                print("✓ Added 'biomarkers' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding biomarkers column: {e}")

    def _add_symptoms_column(self):
        """Add symptoms column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'symptoms' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN symptoms TEXT")
                self.conn.commit()
                print("✓ Added 'symptoms' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding symptoms column: {e}")

    def _add_procedures_column(self):
        """Add procedures column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'procedures' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN procedures TEXT")
                self.conn.commit()
                print("✓ Added 'procedures' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding procedures column: {e}")

    def _add_anomaly_detection_column(self):
        """Add anomaly_detection column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'anomaly_detection' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN anomaly_detection TEXT")
                self.conn.commit()
                print("✓ Added 'anomaly_detection' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding anomaly_detection column: {e}")

    def _add_ocr_confidence_column(self):
        """Add ocr_confidence column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'ocr_confidence' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN ocr_confidence REAL")
                self.conn.commit()
                print("✓ Added 'ocr_confidence' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding ocr_confidence column: {e}")

    def _add_llm_metadata_column(self):
        """Add llm_metadata column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'llm_metadata' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN llm_metadata TEXT")
                self.conn.commit()
                print("✓ Added 'llm_metadata' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding llm_metadata column: {e}")

    def _add_historical_biomarkers_column(self):
        """Add historical_biomarkers column to medical_records table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(medical_records)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'historical_biomarkers' not in columns:
                cursor.execute("ALTER TABLE medical_records ADD COLUMN historical_biomarkers TEXT")
                self.conn.commit()
                print("✓ Added 'historical_biomarkers' column to 'medical_records' table.")
        except Exception as e:
            print(f"Error checking/adding historical_biomarkers column: {e}")

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite Row to dictionary"""
        if row is None:
            return None
        return dict(row)

    # ============================================================================
    # USER OPERATIONS
    # ============================================================================

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user (patient or doctor)

        Args:
            user_data: Dictionary containing user information

        Returns:
            Created user record
        """
        try:
            cursor = self.conn.cursor()

            # Generate UUID if not provided
            if 'id' not in user_data:
                user_data['id'] = str(uuid.uuid4())

            # Set timestamps
            user_data['created_at'] = datetime.now().isoformat()
            user_data['updated_at'] = datetime.now().isoformat()

            # Build SQL query
            columns = ', '.join(user_data.keys())
            placeholders = ', '.join(['?' for _ in user_data.keys()])
            query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"

            cursor.execute(query, list(user_data.values()))
            self.conn.commit()

            # Return the created user
            return self.get_user_by_id(user_data['id'])
        except Exception as e:
            print(f"Error creating user: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            cursor = self.conn.cursor()
            updates['updated_at'] = datetime.now().isoformat()

            # Build SQL query
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            values = list(updates.values()) + [user_id]

            cursor.execute(query, values)
            self.conn.commit()

            return self.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error updating user: {e}")
            raise

    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(), user_id)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error updating last login: {e}")

    # ============================================================================
    # MEDICAL RECORDS OPERATIONS
    # ============================================================================

    def create_medical_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new medical record"""
        try:
            cursor = self.conn.cursor()

            # Generate UUID if not provided
            if 'id' not in record_data:
                record_data['id'] = str(uuid.uuid4())

            # Set timestamps
            record_data['created_at'] = datetime.now().isoformat()
            record_data['updated_at'] = datetime.now().isoformat()
            # Convert complex types to JSON strings
            for key, value in record_data.items():
                if isinstance(value, (dict, list)):
                    record_data[key] = json.dumps(value, cls=NpEncoder)

            # Build SQL query
            columns = ', '.join(record_data.keys())
            placeholders = ', '.join(['?' for _ in record_data.keys()])
            query = f"INSERT INTO medical_records ({columns}) VALUES ({placeholders})"

            cursor.execute(query, list(record_data.values()))
            self.conn.commit()

            # Return the created record
            return self.get_record_by_id(record_data['id'])
        except Exception as e:
            print(f"Error creating medical record: {e}")
            raise

    def get_patient_records(self, patient_id: str, limit: int = 20, offset: int = 0, order_by: str = 'created_at') -> List[Dict[str, Any]]:
        """Get medical records for a patient with pagination"""
        try:
            cursor = self.conn.cursor()
            query = f"SELECT * FROM medical_records WHERE patient_id = ? ORDER BY {order_by} DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (patient_id, limit, offset))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting patient records: {e}")
            return []

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a medical record by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM medical_records WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            record = self._row_to_dict(row)

            if record:
                # Parse JSON strings back to complex types
                for key, value in record.items():
                    if isinstance(value, str) and value.startswith(('{', '[')):
                        try:
                            record[key] = json.loads(value)
                        except json.JSONDecodeError:
                            pass # Not a valid JSON string

            return record
        except Exception as e:
            print(f"Error getting record: {e}")
            return None

    def update_medical_record(self, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a medical record"""
        try:
            cursor = self.conn.cursor()
            updates['updated_at'] = datetime.now().isoformat()

            # Build SQL query
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE medical_records SET {set_clause} WHERE id = ?"
            values = list(updates.values()) + [record_id]

            cursor.execute(query, values)
            self.conn.commit()

            return self.get_record_by_id(record_id)
        except Exception as e:
            print(f"Error updating medical record: {e}")
            raise

    def get_critical_records(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get records with critical alerts for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM medical_records WHERE patient_id = ? AND has_critical_alerts = 1 ORDER BY created_at DESC",
                (patient_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting critical records: {e}")
            return []

    def create_biomarker(self, biomarker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new biomarker entry"""
        try:
            cursor = self.conn.cursor()

            if 'id' not in biomarker_data:
                biomarker_data['id'] = str(uuid.uuid4())
            biomarker_data['created_at'] = datetime.now().isoformat()

            columns = ', '.join(biomarker_data.keys())
            placeholders = ', '.join(['?' for _ in biomarker_data.keys()])
            query = f"INSERT INTO biomarkers ({columns}) VALUES ({placeholders})"

            cursor.execute(query, list(biomarker_data.values()))
            self.conn.commit()

            cursor.execute("SELECT * FROM biomarkers WHERE id = ?", (biomarker_data['id'],))
            return self._row_to_dict(cursor.fetchone())
        except Exception as e:
            print(f"Error creating biomarker: {e}")
            raise

    def create_biomarkers_bulk(self, biomarkers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple biomarkers at once"""
        created = []
        for biomarker in biomarkers:
            try:
                created.append(self.create_biomarker(biomarker))
            except Exception as e:
                print(f"Error creating biomarker: {e}")
        return created

    def get_patient_biomarkers(self, patient_id: str, biomarker_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get biomarkers for a patient, optionally filtered by type"""
        try:
            cursor = self.conn.cursor()
            if biomarker_type:
                cursor.execute(
                    "SELECT * FROM biomarkers WHERE patient_id = ? AND biomarker_type = ? ORDER BY measurement_date DESC LIMIT ?",
                    (patient_id, biomarker_type, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM biomarkers WHERE patient_id = ? ORDER BY measurement_date DESC LIMIT ?",
                    (patient_id, limit)
                )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting biomarkers: {e}")
            return []

    def get_biomarker_trend(self, patient_id: str, biomarker_type: str, days: int = 90) -> List[Dict[str, Any]]:
        """Get biomarker values over time for trend analysis"""
        try:
            cursor = self.conn.cursor()
            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            cursor.execute(
                "SELECT * FROM biomarkers WHERE patient_id = ? AND biomarker_type = ? AND measurement_date >= ? ORDER BY measurement_date ASC",
                (patient_id, biomarker_type, cutoff_date)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting biomarker trend: {e}")
            return []

    def create_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new anomaly entry"""
        try:
            cursor = self.conn.cursor()

            if 'id' not in anomaly_data:
                anomaly_data['id'] = str(uuid.uuid4())
            anomaly_data['created_at'] = datetime.now().isoformat()
            anomaly_data['detection_date'] = datetime.now().isoformat()

            columns = ', '.join(anomaly_data.keys())
            placeholders = ', '.join(['?' for _ in anomaly_data.keys()])
            query = f"INSERT INTO anomalies ({columns}) VALUES ({placeholders})"

            cursor.execute(query, list(anomaly_data.values()))
            self.conn.commit()

            cursor.execute("SELECT * FROM anomalies WHERE id = ?", (anomaly_data['id'],))
            return self._row_to_dict(cursor.fetchone())
        except Exception as e:
            print(f"Error creating anomaly: {e}")
            raise

    def create_anomalies_bulk(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple anomalies at once"""
        created = []
        for anomaly in anomalies:
            try:
                created.append(self.create_anomaly(anomaly))
            except Exception as e:
                print(f"Error creating anomaly: {e}")
        return created

    def get_patient_anomalies(self, patient_id: str, critical_only: bool = False, unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
        """Get anomalies for a patient"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM anomalies WHERE patient_id = ?"
            params = [patient_id]

            if critical_only:
                query += " AND is_critical = 1"
            if unacknowledged_only:
                query += " AND acknowledged = 0"

            query += " ORDER BY detection_date DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting anomalies: {e}")
            return []

    def acknowledge_anomaly(self, anomaly_id: str, doctor_id: str) -> Dict[str, Any]:
        """Mark an anomaly as acknowledged"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE anomalies SET acknowledged = 1, acknowledged_by = ?, acknowledged_at = ? WHERE id = ?",
                (doctor_id, datetime.now().isoformat(), anomaly_id)
            )
            self.conn.commit()
            cursor.execute("SELECT * FROM anomalies WHERE id = ?", (anomaly_id,))
            return self._row_to_dict(cursor.fetchone())
        except Exception as e:
            print(f"Error acknowledging anomaly: {e}")
            raise

    def create_medication(self, medication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new medication entry"""
        try:
            cursor = self.conn.cursor()

            if 'id' not in medication_data:
                medication_data['id'] = str(uuid.uuid4())
            medication_data['created_at'] = datetime.now().isoformat()

            columns = ', '.join(medication_data.keys())
            placeholders = ', '.join(['?' for _ in medication_data.keys()])
            query = f"INSERT INTO medications ({columns}) VALUES ({placeholders})"

            cursor.execute(query, list(medication_data.values()))
            self.conn.commit()

            cursor.execute("SELECT * FROM medications WHERE id = ?", (medication_data['id'],))
            return self._row_to_dict(cursor.fetchone())
        except Exception as e:
            print(f"Error creating medication: {e}")
            raise

    def create_medications_bulk(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple medications at once"""
        created = []
        for medication in medications:
            try:
                created.append(self.create_medication(medication))
            except Exception as e:
                print(f"Error creating medication: {e}")
        return created

    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all medications for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM medications WHERE patient_id = ? ORDER BY prescribed_date DESC",
                (patient_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting medications: {e}")
            return []

    def get_record_biomarkers(self, record_id: str) -> List[Dict[str, Any]]:
        """Get all biomarkers for a specific record"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM biomarkers WHERE record_id = ? ORDER BY measurement_date DESC",
                (record_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting biomarkers for record: {e}")
            return []

    def get_record_medications(self, record_id: str) -> List[Dict[str, Any]]:
        """Get all medications for a specific record"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM medications WHERE record_id = ? ORDER BY prescribed_date DESC",
                (record_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting medications for record: {e}")
            return []

    def get_record_anomalies(self, record_id: str) -> List[Dict[str, Any]]:
        """Get all anomalies for a specific record"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM anomalies WHERE record_id = ? ORDER BY severity DESC, detected_at DESC",
                (record_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting anomalies for record: {e}")
            return []

    # ============================================================================
    # STUB METHODS - Additional features not yet implemented
    # ============================================================================

    def create_disease(self, disease_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def create_diseases_bulk(self, diseases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return []

    def get_patient_diseases(self, patient_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        return []

    def grant_doctor_access(self, access_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def check_doctor_access(self, doctor_id: str, patient_id: str) -> bool:
        return False

    def get_doctor_patients(self, doctor_id: str) -> List[Dict[str, Any]]:
        return []

    def revoke_doctor_access(self, access_id: str, revoked_by: str) -> Dict[str, Any]:
        return None

    def create_doctor_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def get_patient_doctor_notes(self, patient_id: str, include_private: bool = False) -> List[Dict[str, Any]]:
        return []

    def create_embedding(self, embedding_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def get_record_embeddings(self, record_id: str) -> List[Dict[str, Any]]:
        return []

    def search_records(self, patient_id: Optional[str] = None, search_text: Optional[str] = None,
                      document_type: Optional[str] = None, start_date: Optional[str] = None,
                      end_date: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search medical records with various filters"""
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM medical_records WHERE 1=1"
            params = []

            if patient_id:
                query += " AND patient_id = ?"
                params.append(patient_id)

            if document_type:
                query += " AND document_type = ?"
                params.append(document_type)

            if start_date:
                query += " AND document_date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND document_date <= ?"
                params.append(end_date)

            if search_text:
                query += " AND ocr_text LIKE ?"
                params.append(f"%{search_text}%")

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching records: {e}")
            return []

    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get summary statistics for a patient"""
        try:
            cursor = self.conn.cursor()

            # Get total records
            cursor.execute("SELECT COUNT(*) as count FROM medical_records WHERE patient_id = ?", (patient_id,))
            total_records = cursor.fetchone()['count']

            # Get critical records
            cursor.execute("SELECT COUNT(*) as count FROM medical_records WHERE patient_id = ? AND has_critical_alerts = 1", (patient_id,))
            critical_records = cursor.fetchone()['count']

            # Get unacknowledged anomalies
            cursor.execute("SELECT COUNT(*) as count FROM anomalies WHERE patient_id = ? AND acknowledged = 0", (patient_id,))
            unacknowledged_anomalies = cursor.fetchone()['count']

            # Get last upload date
            cursor.execute("SELECT MAX(created_at) as last_upload FROM medical_records WHERE patient_id = ?", (patient_id,))
            result = cursor.fetchone()
            last_upload = result['last_upload'] if result else None

            return {
                'total_records': total_records,
                'critical_records': critical_records,
                'unacknowledged_anomalies': unacknowledged_anomalies,
                'last_upload': last_upload
            }
        except Exception as e:
            print(f"Error getting patient summary: {e}")
            return {
                'total_records': 0,
                'critical_records': 0,
                'unacknowledged_anomalies': 0,
                'last_upload': None
            }


# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
