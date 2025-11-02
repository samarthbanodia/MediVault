"""
Local SQLite Database Interface for MediSense
Simple authentication-focused implementation
"""

import os
import sqlite3
import uuid
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

        self.conn.commit()
        print("✓ Local SQLite database initialized")

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
    # STUB METHODS - Not implemented for local auth-only mode
    # ============================================================================

    def create_medical_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def get_patient_records(self, patient_id: str, limit: int = 20, offset: int = 0, order_by: str = 'created_at') -> List[Dict[str, Any]]:
        return []

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        return None

    def update_medical_record(self, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def get_critical_records(self, patient_id: str) -> List[Dict[str, Any]]:
        return []

    def create_biomarker(self, biomarker_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def create_biomarkers_bulk(self, biomarkers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return []

    def get_patient_biomarkers(self, patient_id: str, biomarker_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        return []

    def get_biomarker_trend(self, patient_id: str, biomarker_type: str, days: int = 90) -> List[Dict[str, Any]]:
        return []

    def create_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def create_anomalies_bulk(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return []

    def get_patient_anomalies(self, patient_id: str, critical_only: bool = False, unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
        return []

    def acknowledge_anomaly(self, anomaly_id: str, doctor_id: str) -> Dict[str, Any]:
        return None

    def create_medication(self, medication_data: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def create_medications_bulk(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return []

    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        return []

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
        return []

    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
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
