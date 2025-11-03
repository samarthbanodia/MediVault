"""
MediSense Flask Application with Google ADK Agents
Integrated multi-agent system for medical document processing
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
from datetime import datetime

# Import agent orchestrator
from agents.orchestrator import AgentOrchestrator
from agents.config import AgentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app_agents.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Validate agent configuration
try:
    AgentConfig.validate()
    logger.info("Agent configuration validated successfully")
except Exception as e:
    logger.error(f"Agent configuration validation failed: {e}")
    raise

# Initialize Agent Orchestrator (singleton)
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        logger.info("Initializing Agent Orchestrator...")
        orchestrator = AgentOrchestrator(
            vector_db_path=AgentConfig.VECTOR_DB_PATH,
            collection_name=AgentConfig.VECTOR_DB_COLLECTION,
            api_key=AgentConfig.GOOGLE_API_KEY
        )
        logger.info("Agent Orchestrator initialized")
    return orchestrator


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# PATIENT FLOW ENDPOINTS
# ============================================================================

@app.route('/api/agents/upload', methods=['POST'])
def upload_document():
    """
    Upload and process medical document using agent pipeline

    Flow: OCR → NER → Prescription Parser → Anomaly Detection → Normalizer → Embedding → Vector DB
    """
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400

        # Get additional parameters
        patient_id = request.form.get('patient_id')
        if not patient_id:
            return jsonify({'success': False, 'error': 'patient_id required'}), 400

        document_type = request.form.get('document_type')  # Optional hint

        # Parse patient metadata if provided
        patient_metadata = {}
        if request.form.get('patient_metadata'):
            try:
                patient_metadata = json.loads(request.form.get('patient_metadata'))
            except json.JSONDecodeError:
                logger.warning("Invalid patient_metadata JSON, using empty dict")

        # Parse historical records if provided
        historical_records = []
        if request.form.get('historical_records'):
            try:
                historical_records = json.loads(request.form.get('historical_records'))
            except json.JSONDecodeError:
                logger.warning("Invalid historical_records JSON, using empty list")

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{patient_id}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        logger.info(f"File uploaded: {file_path}")

        # Process document through agent pipeline
        orch = get_orchestrator()
        result = orch.process_patient_document(
            file_path=file_path,
            patient_id=patient_id,
            document_type=document_type,
            patient_metadata=patient_metadata,
            historical_records=historical_records
        )

        # Return result
        if result.get('success'):
            return jsonify({
                'success': True,
                'record_id': result.get('record_id'),
                'document_type': result.get('document_type'),
                'has_critical_alerts': result.get('has_critical_alerts', False),
                'overall_severity': result.get('overall_severity', 0),
                'clinical_summary': result.get('clinical_summary', {}),
                'anomalies': result.get('pipeline_stages', {}).get('anomaly_detection', {}).get('anomalies', []),
                'message': 'Document processed successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Processing failed',
                'details': result.get('errors', [])
            }), 500

    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/agents/batch-upload', methods=['POST'])
def batch_upload():
    """
    Batch upload multiple documents
    """
    try:
        files = request.files.getlist('files')
        patient_id = request.form.get('patient_id')

        if not files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400

        if not patient_id:
            return jsonify({'success': False, 'error': 'patient_id required'}), 400

        # Save all files and prepare for batch processing
        documents = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{patient_id}_{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                documents.append({
                    'file_path': file_path,
                    'patient_id': patient_id
                })

        # Process batch
        orch = get_orchestrator()
        results = orch.batch_process_documents(documents)

        return jsonify({
            'success': True,
            'total_processed': len(results),
            'results': results
        }), 200

    except Exception as e:
        logger.error(f"Error in batch upload: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# SMART SEARCH ENDPOINTS
# ============================================================================

@app.route('/api/agents/search', methods=['GET', 'POST'])
def smart_search():
    """
    Smart search using semantic + keyword search

    Flow: Query → Embedding → Semantic Search → Ranking
    """
    try:
        if request.method == 'POST':
            data = request.json
        else:
            data = request.args

        query = data.get('query')
        if not query:
            return jsonify({'success': False, 'error': 'query parameter required'}), 400

        patient_id = data.get('patient_id')  # Optional: limit to specific patient
        top_k = int(data.get('top_k', 5))

        # Perform search
        orch = get_orchestrator()
        result = orch.search_agent.process({
            'query': query,
            'patient_id': patient_id,
            'top_k': top_k,
            'search_mode': 'hybrid'
        })

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in search endpoint: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/agents/ask', methods=['POST'])
def ask_question():
    """
    Ask a question and get AI-generated answer with evidence

    Flow: Query → Search → AI Analyser → Response
    """
    try:
        data = request.json

        query = data.get('query')
        if not query:
            return jsonify({'success': False, 'error': 'query required'}), 400

        patient_id = data.get('patient_id')
        top_k = int(data.get('top_k', 5))
        include_history = data.get('include_entire_history', False)

        # Perform smart search with AI analysis
        orch = get_orchestrator()
        result = orch.smart_search(
            query=query,
            patient_id=patient_id,
            top_k=top_k,
            include_entire_history=include_history
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in ask endpoint: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PATIENT SUMMARY & ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/agents/patient/<patient_id>/summary', methods=['GET'])
def get_patient_summary(patient_id):
    """
    Get comprehensive patient summary
    """
    try:
        orch = get_orchestrator()
        result = orch.get_patient_summary(patient_id)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting patient summary: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/agents/patient/<patient_id>/alerts', methods=['GET'])
def get_patient_alerts(patient_id):
    """
    Get critical alerts for patient
    """
    try:
        orch = get_orchestrator()
        alerts = orch.get_critical_alerts(patient_id)

        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'total_alerts': len(alerts),
            'alerts': alerts
        }), 200

    except Exception as e:
        logger.error(f"Error getting alerts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/agents/alerts', methods=['GET'])
def get_all_alerts():
    """
    Get all critical alerts across all patients
    """
    try:
        orch = get_orchestrator()
        alerts = orch.get_critical_alerts()

        return jsonify({
            'success': True,
            'total_alerts': len(alerts),
            'alerts': alerts
        }), 200

    except Exception as e:
        logger.error(f"Error getting all alerts: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/agents/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    try:
        orch = get_orchestrator()

        return jsonify({
            'success': True,
            'status': 'healthy',
            'agents': {
                'ocr': 'ready',
                'ner': 'ready',
                'prescription_parser': 'ready',
                'anomaly_detection': 'ready',
                'normalizer': 'ready',
                'embedding': 'ready',
                'search': 'ready',
                'analyser': 'ready'
            },
            'vector_db': {
                'connected': True,
                'collection': AgentConfig.VECTOR_DB_COLLECTION,
                'count': orch.collection.count()
            }
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint
    """
    return jsonify({
        'name': 'MediSense Agent API',
        'version': '1.0.0',
        'description': 'Multi-agent system for medical document processing',
        'endpoints': {
            'upload': '/api/agents/upload',
            'batch_upload': '/api/agents/batch-upload',
            'search': '/api/agents/search',
            'ask': '/api/agents/ask',
            'patient_summary': '/api/agents/patient/<patient_id>/summary',
            'patient_alerts': '/api/agents/patient/<patient_id>/alerts',
            'all_alerts': '/api/agents/alerts',
            'health': '/api/agents/health'
        }
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB'
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting MediSense Agent API...")

    # Initialize orchestrator at startup
    get_orchestrator()

    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
