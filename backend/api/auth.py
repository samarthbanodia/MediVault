"""
Authentication API Endpoints for MediVault
Handles signup, login, and OAuth
"""

from flask import Blueprint, request, jsonify
from services.auth_service import get_auth_service
from functools import wraps

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Get auth service
auth_service = get_auth_service()


# ============================================================================
# MIDDLEWARE/DECORATORS
# ============================================================================

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]

        # Verify token
        user = auth_service.get_current_user(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add user to request context
        request.user = user
        return f(*args, **kwargs)

    return decorated_function


def require_patient(f):
    """Decorator to require patient access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]

        try:
            user = auth_service.require_patient(token)
            request.user = user
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 403

    return decorated_function


def require_doctor(f):
    """Decorator to require doctor access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]

        try:
            user = auth_service.require_doctor(token)
            request.user = user
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 403

    return decorated_function


# ============================================================================
# PATIENT REGISTRATION & LOGIN
# ============================================================================

@auth_bp.route('/signup/patient', methods=['POST'])
def signup_patient():
    """
    Register a new patient

    Request body:
        {
            "email": "patient@example.com",
            "password": "securepassword",
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",  # optional
            "gender": "male",  # optional
            "phone": "+1234567890"  # optional
        }

    Returns:
        {
            "success": true,
            "user": {...},
            "token": "jwt-token-here"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Register patient
        result = auth_service.register_patient(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            phone=data.get('phone')
        )

        return jsonify({
            'success': True,
            'user': result['user'],
            'token': result['token']
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/signup/doctor', methods=['POST'])
def signup_doctor():
    """
    Register a new doctor

    Request body:
        {
            "email": "doctor@example.com",
            "password": "securepassword",
            "full_name": "Dr. Jane Smith",
            "license_number": "DOC12345",
            "specialization": "Cardiology",
            "hospital_affiliation": "City Hospital",  # optional
            "phone": "+1234567890"  # optional
        }

    Returns:
        {
            "success": true,
            "user": {...},
            "token": "jwt-token-here"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'license_number', 'specialization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Register doctor
        result = auth_service.register_doctor(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            license_number=data['license_number'],
            specialization=data['specialization'],
            hospital_affiliation=data.get('hospital_affiliation'),
            phone=data.get('phone')
        )

        return jsonify({
            'success': True,
            'user': result['user'],
            'token': result['token']
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password

    Request body:
        {
            "email": "user@example.com",
            "password": "securepassword"
        }

    Returns:
        {
            "success": true,
            "user": {...},
            "token": "jwt-token-here"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        # Login
        result = auth_service.login(
            email=data['email'],
            password=data['password']
        )

        return jsonify({
            'success': True,
            'user': result['user'],
            'token': result['token']
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


# ============================================================================
# GOOGLE OAUTH
# ============================================================================

@auth_bp.route('/google-oauth', methods=['POST'])
def google_oauth():
    """
    Login or register with Google OAuth

    Request body:
        {
            "google_id": "123456789",
            "email": "user@gmail.com",
            "full_name": "John Doe",
            "profile_picture_url": "https://...",  # optional
            "user_type": "patient"  # optional, defaults to "patient"
        }

    Returns:
        {
            "success": true,
            "user": {...},
            "token": "jwt-token-here"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['google_id', 'email', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Login with Google
        result = auth_service.login_with_google(
            google_id=data['google_id'],
            email=data['email'],
            full_name=data['full_name'],
            profile_picture_url=data.get('profile_picture_url'),
            user_type=data.get('user_type', 'patient')
        )

        return jsonify({
            'success': True,
            'user': result['user'],
            'token': result['token']
        }), 200

    except Exception as e:
        return jsonify({'error': f'OAuth login failed: {str(e)}'}), 500


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@auth_bp.route('/session', methods=['GET'])
@require_auth
def get_session():
    """
    Get current session/user information

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "user": {...}
        }
    """
    user_data = {
        'id': request.user['id'],
        'email': request.user['email'],
        'full_name': request.user['full_name'],
        'user_type': request.user['user_type'],
        'profile_picture_url': request.user.get('profile_picture_url')
    }

    # Add type-specific fields
    if request.user['user_type'] == 'patient':
        user_data.update({
            'age': request.user.get('age'),
            'gender': request.user.get('gender'),
            'date_of_birth': request.user.get('date_of_birth')
        })
    elif request.user['user_type'] == 'doctor':
        user_data.update({
            'license_number': request.user.get('license_number'),
            'specialization': request.user.get('specialization'),
            'hospital_affiliation': request.user.get('hospital_affiliation')
        })

    return jsonify({
        'success': True,
        'user': user_data
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "token": "new-jwt-token-here"
        }
    """
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]

        # Refresh token
        new_token = auth_service.refresh_token(token)
        if not new_token:
            return jsonify({'error': 'Invalid or expired token'}), 401

        return jsonify({
            'success': True,
            'token': new_token
        }), 200

    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout (client should delete token)

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    # Note: With JWT, logout is mainly client-side (delete token)
    # Server could maintain blacklist of tokens if needed
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


# ============================================================================
# PASSWORD MANAGEMENT
# ============================================================================

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    Change user password

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }

    Returns:
        {
            "success": true,
            "message": "Password changed successfully"
        }
    """
    try:
        data = request.get_json()

        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new passwords are required'}), 400

        # Verify current password
        user = request.user
        if not user.get('password_hash'):
            return jsonify({'error': 'Cannot change password for OAuth accounts'}), 400

        if not auth_service.verify_password(data['current_password'], user['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Hash new password
        new_password_hash = auth_service.hash_password(data['new_password'])

        # Update password
        from database import get_database
        db = get_database()
        db.update_user(user['id'], {'password_hash': new_password_hash})

        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500


# ============================================================================
# PROFILE MANAGEMENT
# ============================================================================

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Get user profile

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "user": {...}
        }
    """
    return jsonify({
        'success': True,
        'user': request.user
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    Update user profile

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "full_name": "New Name",  # optional
            "phone": "+1234567890",  # optional
            "gender": "male",  # optional (patients only)
            "hospital_affiliation": "New Hospital"  # optional (doctors only)
        }

    Returns:
        {
            "success": true,
            "user": {...}
        }
    """
    try:
        data = request.get_json()
        user = request.user

        # Fields that can be updated
        allowed_fields = ['full_name', 'phone', 'profile_picture_url']

        if user['user_type'] == 'patient':
            allowed_fields.extend(['gender', 'date_of_birth', 'address'])
        elif user['user_type'] == 'doctor':
            allowed_fields.extend(['specialization', 'hospital_affiliation'])

        # Build update dict
        updates = {}
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        # Update user
        from database import get_database
        db = get_database()
        updated_user = db.update_user(user['id'], updates)

        return jsonify({
            'success': True,
            'user': updated_user
        }), 200

    except Exception as e:
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'auth',
        'version': '1.0.0'
    }), 200
