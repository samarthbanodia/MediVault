"""
Doctor API Endpoints for MediVault
Handles doctor-specific operations: patient access, notes, etc.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from api.auth import require_doctor, require_auth
from database import get_database
from services.auth_service import get_auth_service

# Create blueprint
doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

# Get services
db = get_database()
auth_service = get_auth_service()


# ============================================================================
# PATIENT ACCESS MANAGEMENT
# ============================================================================

@doctor_bp.route('/patients', methods=['GET'])
@require_doctor
def get_doctor_patients():
    """
    Get all patients the doctor has access to

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "patients": [...]
        }
    """
    try:
        doctor = request.user

        # Get all accessible patients
        patients = db.get_doctor_patients(doctor['id'])

        return jsonify({
            'success': True,
            'patients': patients
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve patients: {str(e)}'}), 500


@doctor_bp.route('/patient/<patient_id>', methods=['GET'])
@require_doctor
def get_patient_details(patient_id):
    """
    Get detailed information about a specific patient

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "patient": {...},
            "recent_records": [...],
            "critical_anomalies": [...],
            "summary": {...}
        }
    """
    try:
        doctor = request.user

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403

        # Get patient info
        patient = db.get_user_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        # Get recent records
        recent_records = db.get_patient_records(
            patient_id=patient_id,
            limit=10,
            order_by='created_at'
        )

        # Get critical anomalies
        critical_anomalies = db.get_patient_anomalies(
            patient_id=patient_id,
            critical_only=True,
            unacknowledged_only=True
        )

        # Get summary
        summary = db.get_patient_summary(patient_id)

        return jsonify({
            'success': True,
            'patient': {
                'id': patient['id'],
                'full_name': patient['full_name'],
                'email': patient['email'],
                'age': patient.get('age'),
                'gender': patient.get('gender'),
                'phone': patient.get('phone')
            },
            'recent_records': recent_records,
            'critical_anomalies': critical_anomalies,
            'summary': summary
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve patient details: {str(e)}'}), 500


@doctor_bp.route('/patient/<patient_id>/records', methods=['GET'])
@require_doctor
def get_patient_records(patient_id):
    """
    Get all medical records for a specific patient

    Headers:
        Authorization: Bearer <token>

    Query params:
        limit: int (default: 20)
        offset: int (default: 0)

    Returns:
        {
            "success": true,
            "records": [...]
        }
    """
    try:
        doctor = request.user

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403

        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))

        records = db.get_patient_records(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            order_by='created_at'
        )

        return jsonify({
            'success': True,
            'records': records,
            'total': len(records),
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve records: {str(e)}'}), 500


@doctor_bp.route('/patient/<patient_id>/biomarkers/<biomarker_type>', methods=['GET'])
@require_doctor
def get_patient_biomarker_trend(patient_id, biomarker_type):
    """
    Get biomarker trend for a patient

    Headers:
        Authorization: Bearer <token>

    Query params:
        days: int (default: 90)

    Returns:
        {
            "success": true,
            "biomarker_type": "glucose",
            "data": [...]
        }
    """
    try:
        doctor = request.user

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403

        days = int(request.args.get('days', 90))

        trend_data = db.get_biomarker_trend(
            patient_id=patient_id,
            biomarker_type=biomarker_type,
            days=days
        )

        return jsonify({
            'success': True,
            'biomarker_type': biomarker_type,
            'data': trend_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve biomarker trend: {str(e)}'}), 500


# ============================================================================
# DOCTOR NOTES
# ============================================================================

@doctor_bp.route('/patient/<patient_id>/notes', methods=['GET'])
@require_doctor
def get_patient_notes(patient_id):
    """
    Get all notes for a patient

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "notes": [...]
        }
    """
    try:
        doctor = request.user

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403

        notes = db.get_patient_doctor_notes(patient_id, include_private=True)

        return jsonify({
            'success': True,
            'notes': notes
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve notes: {str(e)}'}), 500


@doctor_bp.route('/patient/<patient_id>/notes', methods=['POST'])
@require_doctor
def add_patient_note(patient_id):
    """
    Add a note for a patient

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "note_text": "Patient is responding well to treatment",
            "note_type": "follow_up",  # optional
            "visit_date": "2024-01-15",  # optional
            "is_private": false,  # optional
            "record_id": "uuid"  # optional - link to specific record
        }

    Returns:
        {
            "success": true,
            "note": {...}
        }
    """
    try:
        doctor = request.user
        data = request.get_json()

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403

        # Validate required fields
        if not data.get('note_text'):
            return jsonify({'error': 'Note text is required'}), 400

        # Create note
        note_data = {
            'patient_id': patient_id,
            'doctor_id': doctor['id'],
            'note_text': data['note_text'],
            'note_type': data.get('note_type', 'general'),
            'visit_date': data.get('visit_date', datetime.now().date().isoformat()),
            'is_private': data.get('is_private', False),
            'record_id': data.get('record_id')
        }

        note = db.create_doctor_note(note_data)

        return jsonify({
            'success': True,
            'note': note
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to create note: {str(e)}'}), 500


# ============================================================================
# ANOMALY MANAGEMENT
# ============================================================================

@doctor_bp.route('/anomaly/<anomaly_id>/acknowledge', methods=['POST'])
@require_doctor
def acknowledge_anomaly(anomaly_id):
    """
    Mark an anomaly as acknowledged

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "anomaly": {...}
        }
    """
    try:
        doctor = request.user

        # Get anomaly to check patient access
        anomaly = db.client.table('anomalies').select('*').eq('id', anomaly_id).execute()
        if not anomaly.data:
            return jsonify({'error': 'Anomaly not found'}), 404

        patient_id = anomaly.data[0]['patient_id']

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied'}), 403

        # Acknowledge anomaly
        updated_anomaly = db.acknowledge_anomaly(anomaly_id, doctor['id'])

        return jsonify({
            'success': True,
            'anomaly': updated_anomaly
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to acknowledge anomaly: {str(e)}'}), 500


@doctor_bp.route('/patient/<patient_id>/anomalies', methods=['GET'])
@require_doctor
def get_patient_anomalies(patient_id):
    """
    Get all anomalies for a patient

    Headers:
        Authorization: Bearer <token>

    Query params:
        critical_only: bool (default: false)
        unacknowledged_only: bool (default: false)

    Returns:
        {
            "success": true,
            "anomalies": [...]
        }
    """
    try:
        doctor = request.user

        # Check access
        if not db.check_doctor_access(doctor['id'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403

        critical_only = request.args.get('critical_only', 'false').lower() == 'true'
        unacknowledged_only = request.args.get('unacknowledged_only', 'false').lower() == 'true'

        anomalies = db.get_patient_anomalies(
            patient_id=patient_id,
            critical_only=critical_only,
            unacknowledged_only=unacknowledged_only
        )

        return jsonify({
            'success': True,
            'anomalies': anomalies
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve anomalies: {str(e)}'}), 500


# ============================================================================
# ACCESS SHARING
# ============================================================================

@doctor_bp.route('/request-access', methods=['POST'])
@require_doctor
def request_patient_access():
    """
    Request access to a patient's records
    (In production, this would send a notification to the patient)

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "patient_email": "patient@example.com",
            "access_level": "read",  # optional
            "message": "I'd like to review your medical history"  # optional
        }

    Returns:
        {
            "success": true,
            "message": "Access request sent to patient"
        }
    """
    try:
        doctor = request.user
        data = request.get_json()

        patient_email = data.get('patient_email')
        if not patient_email:
            return jsonify({'error': 'Patient email is required'}), 400

        # Get patient
        patient = db.get_user_by_email(patient_email)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        if patient['user_type'] != 'patient':
            return jsonify({'error': 'User is not a patient'}), 400

        # Check if access already exists
        existing_access = db.check_doctor_access(doctor['id'], patient['id'])
        if existing_access:
            return jsonify({'error': 'You already have access to this patient'}), 400

        # In production, this would send a notification/email to the patient
        # For now, we'll just return a success message

        return jsonify({
            'success': True,
            'message': 'Access request sent to patient',
            'patient_id': patient['id']
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to request access: {str(e)}'}), 500


# ============================================================================
# PATIENT SEARCH
# ============================================================================

@doctor_bp.route('/search-patients', methods=['POST'])
@require_doctor
def search_patients():
    """
    Search for patients by email or name
    (Returns only patients the doctor has access to)

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "query": "john"
        }

    Returns:
        {
            "success": true,
            "patients": [...]
        }
    """
    try:
        doctor = request.user
        data = request.get_json()

        query = data.get('query', '').lower()
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Get accessible patients
        accessible_patients = db.get_doctor_patients(doctor['id'])

        # Filter by query
        filtered_patients = [
            p for p in accessible_patients
            if query in p.get('full_name', '').lower() or
               query in p.get('email', '').lower()
        ]

        return jsonify({
            'success': True,
            'patients': filtered_patients
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to search patients: {str(e)}'}), 500


# ============================================================================
# DASHBOARD STATS
# ============================================================================

@doctor_bp.route('/dashboard', methods=['GET'])
@require_doctor
def get_dashboard_stats():
    """
    Get dashboard statistics for the doctor

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "stats": {
                "total_patients": 10,
                "critical_alerts": 3,
                "patients_with_alerts": [...],
                "recent_activity": [...]
            }
        }
    """
    try:
        doctor = request.user

        # Get accessible patients
        accessible_patients = db.get_doctor_patients(doctor['id'])
        total_patients = len(accessible_patients)

        # Get patients with critical alerts
        patients_with_alerts = []
        total_critical_alerts = 0

        for patient_access in accessible_patients:
            patient_id = patient_access.get('patient_id')
            if patient_id:
                critical_anomalies = db.get_patient_anomalies(
                    patient_id=patient_id,
                    critical_only=True,
                    unacknowledged_only=True
                )

                if critical_anomalies:
                    total_critical_alerts += len(critical_anomalies)
                    patients_with_alerts.append({
                        'patient_id': patient_id,
                        'patient_name': patient_access.get('full_name', 'Unknown'),
                        'alert_count': len(critical_anomalies),
                        'most_severe': max(critical_anomalies, key=lambda x: x.get('severity', 0))
                    })

        # Sort patients by alert count
        patients_with_alerts.sort(key=lambda x: x['alert_count'], reverse=True)

        return jsonify({
            'success': True,
            'stats': {
                'total_patients': total_patients,
                'critical_alerts': total_critical_alerts,
                'patients_with_alerts': patients_with_alerts[:10],  # Top 10
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve dashboard stats: {str(e)}'}), 500
