"""
MediVault Web Application
Flask backend with Supabase database and comprehensive API endpoints
"""

import sys
import io

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

# Import API blueprints
from api.auth import auth_bp
from api.records import records_bp
from api.doctor import doctor_bp

# Configuration
from config import Config

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins for development
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Setup directories
Path(Config.UPLOAD_FOLDER).mkdir(exist_ok=True)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(records_bp)
app.register_blueprint(doctor_bp)


# ============================================================================
# ROOT ROUTES
# ============================================================================

@app.route('/')
def index():
    """API information"""
    return jsonify({
        'name': 'MediVault API',
        'version': '2.0.0',
        'description': 'Medical records management with AI-powered insights',
        'endpoints': {
            'auth': '/api/auth',
            'records': '/api/records',
            'doctor': '/api/doctor'
        },
        'documentation': '/api/docs'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        # Test database connection
        from database import get_database
        db = get_database()
        db.client.table('users').select('count', count='exact').limit(1).execute()

        # Test cache connection
        from services.cache import get_cache_service
        cache = get_cache_service()

        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'database': 'connected',
            'cache': 'connected' if cache.enabled else 'disabled',
            'services': {
                'auth': 'operational',
                'records': 'operational',
                'doctor': 'operational'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer <token>',
            'endpoints': {
                'POST /api/auth/signup/patient': 'Register new patient',
                'POST /api/auth/signup/doctor': 'Register new doctor',
                'POST /api/auth/login': 'Login with email/password',
                'POST /api/auth/google-oauth': 'Login with Google',
                'GET /api/auth/session': 'Get current user session',
                'POST /api/auth/refresh': 'Refresh access token',
                'POST /api/auth/logout': 'Logout',
                'GET /api/auth/profile': 'Get user profile',
                'PUT /api/auth/profile': 'Update user profile'
            }
        },
        'patient_records': {
            'description': 'Patient medical record operations',
            'endpoints': {
                'POST /api/records/upload': 'Upload medical document',
                'GET /api/records/all': 'Get all records (paginated)',
                'GET /api/records/<id>': 'Get specific record',
                'GET /api/records/download/<id>': 'Download original file',
                'POST /api/records/search': 'Search records',
                'POST /api/records/ask': 'Ask question about medical history',
                'GET /api/records/anomalies/all': 'Get all anomalies',
                'GET /api/records/biomarkers': 'Get biomarkers',
                'GET /api/records/biomarkers/trend/<type>': 'Get biomarker trend',
                'GET /api/records/summary': 'Get patient summary'
            }
        },
        'doctor': {
            'description': 'Doctor-specific operations',
            'endpoints': {
                'GET /api/doctor/patients': 'Get accessible patients',
                'GET /api/doctor/patient/<id>': 'Get patient details',
                'GET /api/doctor/patient/<id>/records': 'Get patient records',
                'GET /api/doctor/patient/<id>/biomarkers/<type>': 'Get patient biomarker trend',
                'GET /api/doctor/patient/<id>/notes': 'Get patient notes',
                'POST /api/doctor/patient/<id>/notes': 'Add patient note',
                'POST /api/doctor/anomaly/<id>/acknowledge': 'Acknowledge anomaly',
                'GET /api/doctor/patient/<id>/anomalies': 'Get patient anomalies',
                'POST /api/doctor/request-access': 'Request patient access',
                'POST /api/doctor/search-patients': 'Search patients',
                'GET /api/doctor/dashboard': 'Get dashboard statistics'
            }
        },
        'response_formats': {
            'success': {
                'success': True,
                'data': '...'
            },
            'error': {
                'error': 'Error message here'
            }
        }
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(e):
    """Handle 400 errors"""
    return jsonify({'error': 'Bad request', 'message': str(e)}), 400


@app.errorhandler(401)
def unauthorized(e):
    """Handle 401 errors"""
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401


@app.errorhandler(403)
def forbidden(e):
    """Handle 403 errors"""
    return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found', 'message': str(e)}), 404


@app.errorhandler(413)
def request_entity_too_large(e):
    """Handle 413 errors (file too large)"""
    return jsonify({
        'error': 'File too large',
        'message': f'Maximum file size is {Config.MAX_FILE_SIZE_MB}MB'
    }), 413


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  MediVault - Your Medical Records, Organized & Intelligent")
    print("="*70)
    print(f"\n✓ Server starting...")

    # Validate configuration
    try:
        # Check if we can validate (won't fail if Supabase not configured yet)
        if Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:
            print(f"✓ Supabase configured")
        else:
            print(f"⚠ Supabase not configured - add credentials to .env")

        if Config.OPENAI_API_KEY:
            print(f"✓ OpenAI enabled")
        else:
            print(f"⚠ OpenAI not configured")

        if Config.REDIS_ENABLED:
            print(f"✓ Redis caching enabled")
        else:
            print(f"ℹ Redis caching disabled (optional)")

    except Exception as e:
        print(f"⚠ Configuration warning: {e}")

    print(f"\n🌐 API Base URL: http://localhost:5000/api")
    print(f"📚 API Documentation: http://localhost:5000/api/docs")
    print(f"❤️  Health Check: http://localhost:5000/api/health")
    print("\n" + "="*70)
    print("\nAPI Endpoints:")
    print("  Authentication:  /api/auth/*")
    print("  Patient Records: /api/records/*")
    print("  Doctor Portal:   /api/doctor/*")
    print("\n" + "="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
