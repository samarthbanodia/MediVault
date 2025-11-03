"""
Authentication Service for MediVault
Handles user authentication, JWT tokens, and password management
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import Config
from database import get_database


class AuthService:
    """
    Handles user authentication and authorization
    """

    def __init__(self):
        self.db = get_database()
        self.jwt_secret = Config.JWT_SECRET_KEY
        self.jwt_algorithm = Config.JWT_ALGORITHM
        self.jwt_expiry_hours = Config.JWT_EXPIRY_HOURS

    # ============================================================================
    # PASSWORD MANAGEMENT
    # ============================================================================

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    # ============================================================================
    # JWT TOKEN MANAGEMENT
    # ============================================================================

    def create_access_token(
        self,
        user_id: str,
        email: str,
        user_type: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            user_id: User's unique identifier
            email: User's email
            user_type: 'patient' or 'doctor'
            expires_delta: Custom expiration time

        Returns:
            JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=self.jwt_expiry_hours)

        expire = datetime.utcnow() + expires_delta

        payload = {
            'user_id': user_id,
            'email': email,
            'user_type': user_type,
            'exp': expire,
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh an existing token

        Args:
            token: Current JWT token

        Returns:
            New token or None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        # Create new token with same user data
        return self.create_access_token(
            user_id=payload['user_id'],
            email=payload['email'],
            user_type=payload['user_type']
        )

    # ============================================================================
    # USER REGISTRATION
    # ============================================================================

    def register_patient(
        self,
        email: str,
        password: str,
        full_name: str,
        date_of_birth: Optional[str] = None,
        gender: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new patient

        Args:
            email: User's email
            password: User's password
            full_name: User's full name
            date_of_birth: Date of birth (YYYY-MM-DD)
            gender: Gender
            phone: Phone number

        Returns:
            Dictionary with user data and token
        """
        # Check if user already exists
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Calculate age from date of birth
        age = None
        if date_of_birth:
            try:
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except ValueError:
                pass

        # Hash password
        password_hash = self.hash_password(password)

        # Create user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'user_type': 'patient',
            'date_of_birth': date_of_birth,
            'age': age,
            'gender': gender,
            'phone': phone
        }

        user = self.db.create_user(user_data)

        # Create access token
        token = self.create_access_token(
            user_id=user['id'],
            email=user['email'],
            user_type=user['user_type']
        )

        return {
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'user_type': user['user_type'],
                'age': user.get('age'),
                'gender': user.get('gender')
            },
            'token': token
        }

    def register_doctor(
        self,
        email: str,
        password: str,
        full_name: str,
        license_number: str,
        specialization: str,
        hospital_affiliation: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new doctor

        Args:
            email: Doctor's email
            password: Doctor's password
            full_name: Doctor's full name
            license_number: Medical license number
            specialization: Doctor's specialization
            hospital_affiliation: Hospital affiliation
            phone: Phone number

        Returns:
            Dictionary with user data and token
        """
        # Check if user already exists
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        password_hash = self.hash_password(password)

        # Create doctor
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'user_type': 'doctor',
            'license_number': license_number,
            'specialization': specialization,
            'hospital_affiliation': hospital_affiliation,
            'phone': phone
        }

        user = self.db.create_user(user_data)

        # Create access token
        token = self.create_access_token(
            user_id=user['id'],
            email=user['email'],
            user_type=user['user_type']
        )

        return {
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'user_type': user['user_type'],
                'license_number': user.get('license_number'),
                'specialization': user.get('specialization')
            },
            'token': token
        }

    # ============================================================================
    # USER LOGIN
    # ============================================================================

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and create session

        Args:
            email: User's email
            password: User's password

        Returns:
            Dictionary with user data and token

        Raises:
            ValueError: If credentials are invalid
        """
        # Get user
        user = self.db.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.get('is_active', True):
            raise ValueError("Account has been deactivated")

        # Verify password
        if not user.get('password_hash'):
            raise ValueError("Please login with Google OAuth")

        if not self.verify_password(password, user['password_hash']):
            raise ValueError("Invalid email or password")

        # Update last login
        self.db.update_last_login(user['id'])

        # Create access token
        token = self.create_access_token(
            user_id=user['id'],
            email=user['email'],
            user_type=user['user_type']
        )

        # Return user data and token
        user_response = {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'user_type': user['user_type'],
            'profile_picture_url': user.get('profile_picture_url')
        }

        # Add type-specific fields
        if user['user_type'] == 'patient':
            user_response.update({
                'age': user.get('age'),
                'gender': user.get('gender'),
                'date_of_birth': user.get('date_of_birth')
            })
        elif user['user_type'] == 'doctor':
            user_response.update({
                'license_number': user.get('license_number'),
                'specialization': user.get('specialization'),
                'hospital_affiliation': user.get('hospital_affiliation')
            })

        return {
            'user': user_response,
            'token': token
        }

    # ============================================================================
    # GOOGLE OAUTH
    # ============================================================================

    def login_with_google(
        self,
        google_id: str,
        email: str,
        full_name: str,
        profile_picture_url: Optional[str] = None,
        user_type: str = 'patient'
    ) -> Dict[str, Any]:
        """
        Login or register user with Google OAuth

        Args:
            google_id: Google user ID
            email: User's email from Google
            full_name: User's name from Google
            profile_picture_url: Profile picture URL
            user_type: 'patient' or 'doctor' (default: patient)

        Returns:
            Dictionary with user data and token
        """
        # Check if user exists by Google ID
        user = None
        try:
            response = self.db.client.table('users').select('*').eq('google_id', google_id).execute()
            if response.data:
                user = response.data[0]
        except Exception:
            pass

        # If not found by Google ID, check by email
        if not user:
            user = self.db.get_user_by_email(email)

        # Create new user if doesn't exist
        if not user:
            user_data = {
                'email': email,
                'google_id': google_id,
                'full_name': full_name,
                'user_type': user_type,
                'profile_picture_url': profile_picture_url,
                'is_verified': True  # Google accounts are pre-verified
            }
            user = self.db.create_user(user_data)
        else:
            # Update Google ID if not set
            if not user.get('google_id'):
                self.db.update_user(user['id'], {
                    'google_id': google_id,
                    'is_verified': True
                })

        # Update last login
        self.db.update_last_login(user['id'])

        # Create access token
        token = self.create_access_token(
            user_id=user['id'],
            email=user['email'],
            user_type=user['user_type']
        )

        return {
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'user_type': user['user_type'],
                'profile_picture_url': user.get('profile_picture_url')
            },
            'token': token
        }

    # ============================================================================
    # AUTHORIZATION
    # ============================================================================

    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get current user from token

        Args:
            token: JWT token

        Returns:
            User data or None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        user = self.db.get_user_by_id(payload['user_id'])
        return user

    def require_patient(self, token: str) -> Dict[str, Any]:
        """
        Verify token belongs to a patient

        Args:
            token: JWT token

        Returns:
            User data

        Raises:
            ValueError: If not a patient
        """
        user = self.get_current_user(token)
        if not user:
            raise ValueError("Invalid or expired token")

        if user['user_type'] != 'patient':
            raise ValueError("This endpoint requires patient access")

        return user

    def require_doctor(self, token: str) -> Dict[str, Any]:
        """
        Verify token belongs to a doctor

        Args:
            token: JWT token

        Returns:
            User data

        Raises:
            ValueError: If not a doctor
        """
        user = self.get_current_user(token)
        if not user:
            raise ValueError("Invalid or expired token")

        if user['user_type'] != 'doctor':
            raise ValueError("This endpoint requires doctor access")

        return user

    def check_patient_access(
        self,
        token: str,
        patient_id: str
    ) -> bool:
        """
        Check if user has access to patient's records

        Args:
            token: JWT token
            patient_id: Patient's user ID

        Returns:
            True if user has access, False otherwise
        """
        user = self.get_current_user(token)
        if not user:
            return False

        # Patients can access their own records
        if user['id'] == patient_id:
            return True

        # Doctors can access if they have permission
        if user['user_type'] == 'doctor':
            return self.db.check_doctor_access(user['id'], patient_id)

        return False


# Singleton instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get or create auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
