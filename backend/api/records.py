"""
Medical Records API Endpoints for MediVault
Handles patient record operations: upload, retrieve, search
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from pathlib import Path

from api.auth import require_auth
from database import get_database
from services.cache import get_cache_service
from pipelines.ingestion import IngestionPipeline
from pipelines.search import SearchPipeline
from config import Config

# Create blueprint
records_bp = Blueprint('records', __name__, url_prefix='/api/records')

# Get services
db = get_database()
cache = get_cache_service()

# Initialize pipelines
try:
    ingestion_pipeline = IngestionPipeline(enable_llm=True)
    search_pipeline = SearchPipeline(enable_llm=True)
except Exception as e:
    print(f"Warning: Could not initialize pipelines with LLM: {e}")
    ingestion_pipeline = IngestionPipeline(enable_llm=False)
    search_pipeline = SearchPipeline(enable_llm=False)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file, patient_id):
    """Save uploaded file and return file path"""
    if not file or file.filename == '':
        raise ValueError("No file provided")

    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}")

    # Create patient-specific upload directory
    upload_dir = Path(Config.UPLOAD_FOLDER) / patient_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = upload_dir / filename

    # Save file
    file.save(str(filepath))

    return str(filepath), filename, file.content_length


# ============================================================================
# UPLOAD ENDPOINTS
# ============================================================================

@records_bp.route('/upload', methods=['POST'])
@require_auth
def upload_record():
    """
    Upload and process a medical record

    Headers:
        Authorization: Bearer <token>

    Form data:
        file: File (required)
        document_type: str (optional) - prescription, lab_report, etc.
        document_date: str (optional) - YYYY-MM-DD
        issuing_hospital: str (optional)
        issuing_doctor: str (optional)

    Returns:
        {
            "success": true,
            "record_id": "uuid",
            "record": {...},
            "processing_result": {...}
        }
    """
    try:
        # Get file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        user = request.user

        # Save file
        filepath, filename, file_size = save_uploaded_file(file, user['id'])

        # Get metadata from form
        document_type = request.form.get('document_type')
        document_date = request.form.get('document_date')
        issuing_hospital = request.form.get('issuing_hospital')
        issuing_doctor = request.form.get('issuing_doctor')

        # Generate record ID
        record_id = f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create medical record entry
        record_data = {
            'record_id': record_id,
            'patient_id': user['id'],
            'file_name': filename,
            'file_path': filepath,
            'file_type': filename.rsplit('.', 1)[1].lower(),
            'file_size': file_size,
            'document_type': document_type,
            'document_date': document_date,
            'issuing_hospital': issuing_hospital,
            'issuing_doctor': issuing_doctor,
            'processing_status': 'processing'
        }

        medical_record = db.create_medical_record(record_data)

        # Process document with ingestion pipeline
        try:
            patient_info = {
                'patient_id': user['id'],
                'age': user.get('age', 30),
                'historical_biomarkers': []  # TODO: Fetch from database
            }

            processing_result = ingestion_pipeline.process_document(filepath, patient_info)

            import logging
            logging.info(f"Processing result: {processing_result}")

            # Update medical record with processing results
            updates = {
                'ocr_text': processing_result.get('ocr_text', ''),
                'ocr_confidence': processing_result.get('ocr_confidence', 0.0),
                'clinical_summary': processing_result.get('clinical_summary', ''),
                'overall_severity': processing_result.get('anomaly_detection', {}).get('overall_severity', 0),
                'has_critical_alerts': len(processing_result.get('anomaly_detection', {}).get('critical_alerts', [])) > 0,
                'processing_status': 'completed'
            }

            medical_record = db.update_medical_record(medical_record['id'], updates)

            # Save biomarkers
            biomarkers = processing_result.get('biomarkers', [])
            if biomarkers:
                biomarker_records = []
                for biomarker in biomarkers:
                    biomarker_records.append({
                        'record_id': medical_record['id'],
                        'patient_id': user['id'],
                        'biomarker_type': biomarker.get('type', 'unknown'),
                        'value': biomarker.get('value', 0),
                        'unit': biomarker.get('unit', ''),
                        'normal_min': biomarker.get('normal_min'),
                        'normal_max': biomarker.get('normal_max'),
                        'is_abnormal': biomarker.get('is_abnormal', False),
                        'measurement_date': document_date or datetime.now().date().isoformat(),
                        'extracted_text': biomarker.get('extracted_text', ''),
                        'confidence': biomarker.get('confidence', 0.0)
                    })

                if biomarker_records:
                    db.create_biomarkers_bulk(biomarker_records)

            # Save medications
            medications = processing_result.get('medications', [])
            if medications:
                medication_records = []
                for med in medications:
                    medication_records.append({
                        'record_id': medical_record['id'],
                        'patient_id': user['id'],
                        'medication_name': med.get('name', 'Unknown'),
                        'dosage': med.get('dosage', ''),
                        'frequency': med.get('frequency', ''),
                        'duration': med.get('duration', ''),
                        'prescribed_date': document_date or datetime.now().date().isoformat(),
                        'extracted_text': med.get('extracted_text', ''),
                        'confidence': med.get('confidence', 0.0)
                    })

                if medication_records:
                    db.create_medications_bulk(medication_records)

            # Save diseases
            diseases = processing_result.get('diseases', [])
            if diseases:
                disease_records = []
                for disease in diseases:
                    disease_records.append({
                        'record_id': medical_record['id'],
                        'patient_id': user['id'],
                        'disease_name': disease.get('name', 'Unknown'),
                        'diagnosed_date': document_date or datetime.now().date().isoformat(),
                        'status': 'active',
                        'extracted_text': disease.get('extracted_text', ''),
                        'confidence': disease.get('confidence', 0.0)
                    })

                if disease_records:
                    db.create_diseases_bulk(disease_records)

            # Save anomalies
            anomaly_detection = processing_result.get('anomaly_detection', {})
            anomalies = anomaly_detection.get('anomalies', [])
            if anomalies:
                anomaly_records = []
                for anomaly in anomalies:
                    anomaly_records.append({
                        'record_id': medical_record['id'],
                        'patient_id': user['id'],
                        'anomaly_type': anomaly.get('type', 'unknown'),
                        'layer': anomaly.get('layer', 'unknown'),
                        'severity': anomaly.get('severity', 0),
                        'is_critical': anomaly.get('severity', 0) >= 80,
                        'title': anomaly.get('title', ''),
                        'message': anomaly.get('message', ''),
                        'recommendation': anomaly.get('recommendation', ''),
                        'affected_biomarker': anomaly.get('biomarker')
                    })

                if anomaly_records:
                    db.create_anomalies_bulk(anomaly_records)

            # Invalidate patient cache
            cache.invalidate_patient_cache(user['id'])

        except Exception as e:
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
            db.update_medical_record(medical_record['id'], {
                'processing_status': 'failed',
                'error_message': str(e)
            })
            processing_result = {'error': str(e)}

        return jsonify({
            'success': True,
            'record_id': medical_record['id'],
            'record': medical_record,
            'processing_result': processing_result
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


# ============================================================================
# RETRIEVE RECORDS
# ============================================================================

@records_bp.route('/all', methods=['GET'])
@require_auth
def get_all_records():
    """
    Get all medical records for the current patient with pagination

    Headers:
        Authorization: Bearer <token>

    Query params:
        limit: int (default: 20)
        offset: int (default: 0)
        order_by: str (default: created_at)

    Returns:
        {
            "success": true,
            "records": [...],
            "total": 100,
            "limit": 20,
            "offset": 0
        }
    """
    try:
        user = request.user
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        order_by = request.args.get('order_by', 'created_at')

        # Try cache first
        cache_key = f"patient:{user['id']}:records:{limit}:{offset}"
        cached_records = cache.get(cache_key)
        if cached_records:
            return jsonify(cached_records), 200

        # Get records from database
        records = db.get_patient_records(
            patient_id=user['id'],
            limit=limit,
            offset=offset,
            order_by=order_by
        )

        # Get total count (for pagination)
        # In production, use a separate count query
        total = len(records) + offset

        result = {
            'success': True,
            'records': records,
            'total': total,
            'limit': limit,
            'offset': offset
        }

        # Cache result
        cache.set(cache_key, result, expire_seconds=300)  # 5 minutes

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve records: {str(e)}'}), 500


@records_bp.route('/<record_id>', methods=['GET'])
@require_auth
def get_record(record_id):
    """
    Get a specific medical record by ID

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "record": {...},
            "biomarkers": [...],
            "medications": [...],
            "diseases": [...],
            "anomalies": [...]
        }
    """
    try:
        user = request.user

        # Get record
        record = db.get_record_by_id(record_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404

        # Check access permissions - user must own this record
        if record['patient_id'] != user['id']:
            return jsonify({'error': 'Access denied'}), 403

        # Get related data using SQLite methods
        biomarkers = db.get_record_biomarkers(record_id)
        medications = db.get_record_medications(record_id)
        anomalies = db.get_record_anomalies(record_id)

        return jsonify({
            'success': True,
            'record': record,
            'biomarkers': biomarkers,
            'medications': medications,
            'anomalies': anomalies
        }), 200

    except Exception as e:
        print(f"Error in get_record: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to retrieve record: {str(e)}'}), 500


@records_bp.route('/download/<record_id>', methods=['GET'])
@require_auth
def download_record(record_id):
    """
    Download the original file for a record

    Headers:
        Authorization: Bearer <token>

    Returns:
        File download
    """
    try:
        user = request.user

        # Get record
        record = db.get_record_by_id(record_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404

        # Check access permissions - user must own this record
        if record['patient_id'] != user['id']:
            return jsonify({'error': 'Access denied'}), 403

        # Send file
        file_path = record['file_path']
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=record['file_name']
        )

    except Exception as e:
        print(f"Error in download_record: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@records_bp.route('/search', methods=['POST'])
@require_auth
def search_records():
    """
    Search medical records

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "query": "diabetes medication",
            "search_type": "hybrid",  # semantic, keyword, or hybrid
            "generate_summary": true,
            "n_results": 10
        }

    Returns:
        {
            "success": true,
            "total_results": 10,
            "results": [...],
            "ai_summary": "...",
            "tokens_used": 123
        }
    """
    try:
        user = request.user
        data = request.get_json()

        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        search_type = data.get('search_type', 'hybrid')
        generate_summary = data.get('generate_summary', True)
        n_results = min(int(data.get('n_results', 10)), 50)  # Max 50

        # Try cache first
        cache_key = f"search:{query}:patient:{user['id']}:{search_type}:{n_results}"
        cached_results = cache.get(cache_key)
        if cached_results and not generate_summary:
            return jsonify(cached_results), 200

        # Perform search
        results = search_pipeline.search(
            query=query,
            patient_id=user['id'],
            search_type=search_type,
            generate_summary=generate_summary,
            n_results=n_results
        )

        response = {
            'success': True,
            'total_results': results.get('total_results', 0),
            'results': results.get('results', []),
            'ai_summary': results.get('ai_summary'),
            'tokens_used': results.get('llm_metadata', {}).get('tokens_used', 0)
        }

        # Cache results
        cache.set(cache_key, response, expire_seconds=600)  # 10 minutes

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@records_bp.route('/ask', methods=['POST'])
@require_auth
def ask_question():
    """
    Ask a question about medical history

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "question": "Why is my glucose level high?"
        }

    Returns:
        {
            "success": true,
            "answer": "...",
            "question": "...",
            "tokens_used": 123
        }
    """
    try:
        user = request.user
        data = request.get_json()

        question = data.get('question', '')
        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Answer question
        result = search_pipeline.answer_question(
            question=question,
            patient_id=user['id']
        )

        if result.get('success'):
            return jsonify({
                'success': True,
                'answer': result.get('answer'),
                'question': question,
                'tokens_used': result.get('llm_metadata', {}).get('tokens_used', 0)
            }), 200
        else:
            return jsonify({'error': result.get('error')}), 500

    except Exception as e:
        return jsonify({'error': f'Question answering failed: {str(e)}'}), 500


# ============================================================================
# ANOMALIES ENDPOINTS
# ============================================================================

@records_bp.route('/anomalies/all', methods=['GET'])
@require_auth
def get_anomalies():
    """
    Get all anomalies for the current patient

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
        user = request.user
        critical_only = request.args.get('critical_only', 'false').lower() == 'true'
        unacknowledged_only = request.args.get('unacknowledged_only', 'false').lower() == 'true'

        anomalies = db.get_patient_anomalies(
            patient_id=user['id'],
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
# BIOMARKERS ENDPOINTS
# ============================================================================

@records_bp.route('/biomarkers', methods=['GET'])
@require_auth
def get_biomarkers():
    """
    Get biomarkers for the current patient

    Headers:
        Authorization: Bearer <token>

    Query params:
        type: str (optional) - Filter by biomarker type
        limit: int (default: 50)

    Returns:
        {
            "success": true,
            "biomarkers": [...]
        }
    """
    try:
        user = request.user
        biomarker_type = request.args.get('type')
        limit = min(int(request.args.get('limit', 50)), 100)

        biomarkers = db.get_patient_biomarkers(
            patient_id=user['id'],
            biomarker_type=biomarker_type,
            limit=limit
        )

        return jsonify({
            'success': True,
            'biomarkers': biomarkers
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve biomarkers: {str(e)}'}), 500


@records_bp.route('/biomarkers/trend/<biomarker_type>', methods=['GET'])
@require_auth
def get_biomarker_trend(biomarker_type):
    """
    Get biomarker trend over time

    Headers:
        Authorization: Bearer <token>

    Query params:
        days: int (default: 90) - Number of days to look back

    Returns:
        {
            "success": true,
            "biomarker_type": "glucose",
            "data": [...]
        }
    """
    try:
        user = request.user
        days = int(request.args.get('days', 90))

        # Try cache first
        cached_trend = cache.get_biomarker_trend(user['id'], biomarker_type)
        if cached_trend:
            return jsonify({
                'success': True,
                'biomarker_type': biomarker_type,
                'data': cached_trend
            }), 200

        # Get trend data
        trend_data = db.get_biomarker_trend(
            patient_id=user['id'],
            biomarker_type=biomarker_type,
            days=days
        )

        # Cache result
        cache.cache_biomarker_trend(user['id'], biomarker_type, trend_data, expire_minutes=30)

        return jsonify({
            'success': True,
            'biomarker_type': biomarker_type,
            'data': trend_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve biomarker trend: {str(e)}'}), 500


# ============================================================================
# SUMMARY ENDPOINTS
# ============================================================================

@records_bp.route('/summary', methods=['GET'])
@require_auth
def get_summary():
    """
    Get summary statistics for the current patient

    Headers:
        Authorization: Bearer <token>

    Returns:
        {
            "success": true,
            "summary": {
                "total_records": 25,
                "critical_records": 2,
                "unacknowledged_anomalies": 5,
                "last_upload": "2024-01-15T10:30:00"
            }
        }
    """
    try:
        user = request.user

        summary = db.get_patient_summary(user['id'])

        return jsonify({
            'success': True,
            'summary': summary
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve summary: {str(e)}'}), 500
