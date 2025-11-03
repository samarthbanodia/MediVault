from pipelines.components.ocr import MedicalOCR
from pipelines.components.ner import MedicalNER
from pipelines.components.prescription_parser import PrescriptionParser
from pipelines.components.anomaly_detector import AnomalyDetector
from pipelines.components.embeddings import MedicalEmbeddings
from pipelines.components.vector_store import MedicalVectorStore
from pipelines.components.response_generator import MedicalResponseGenerator
from pipelines.components.domain_classifier import MedicalDomainClassifier
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngestionPipeline:
    """Complete ingestion pipeline for medical documents"""

    def __init__(self, enable_llm: bool = True):
        """
        Initialize the ingestion pipeline

        Args:
            enable_llm: Enable OpenAI response generation (requires API key in .env)
        """
        logger.info("Initializing Ingestion Pipeline...")

        self.ocr = MedicalOCR()
        self.ner = MedicalNER()
        self.domain_classifier = MedicalDomainClassifier()
        self.prescription_parser = PrescriptionParser()
        self.anomaly_detector = AnomalyDetector()
        self.embeddings = MedicalEmbeddings()
        self.vector_store = MedicalVectorStore()

        # Initialize response generator if enabled
        self.enable_llm = enable_llm
        self.response_generator = None

        if enable_llm:
            try:
                self.response_generator = MedicalResponseGenerator()
                logger.info("OpenAI response generation enabled")
            except Exception as e:
                logger.warning(f"Could not initialize response generator: {str(e)}")
                logger.warning("Continuing without LLM response generation")
                self.enable_llm = False

        logger.info("Pipeline initialized successfully")

    def process_document(self, image_path: str, patient_info: Dict) -> Dict:
        """
        Process a medical document through the complete pipeline

        Args:
            image_path: Path to medical document image
            patient_info: Dict with patient_id, age, historical_data, etc.

        Returns:
            Processed medical record with anomaly detection results
        """
        logger.info(f"Processing document: {image_path}")

        # Step 1: OCR
        logger.info("Step 1: Extracting text via OCR...")
        ocr_result = self.ocr.extract_text(image_path)
        text = ocr_result['text']
        logger.info(f"OCR confidence: {ocr_result['confidence']:.2f}%")

        # Step 2: Medical NER
        logger.info("Step 2: Extracting medical entities...")
        entities = self.ner.extract_entities(text)
        biomarker_values = self.ner.extract_biomarker_values(text)
        logger.info(f"Found {len(entities['diseases'])} diseases, {len(entities['medications'])} medications")

        # Step 2.5: Classify medical domain
        logger.info("Step 2.5: Classifying medical domain...")
        domain_info = self.domain_classifier.classify_domain(text, entities)
        logger.info(f"Primary domain: {domain_info['primary_domain']}")

        # Step 3: Parse prescriptions
        logger.info("Step 3: Parsing prescriptions...")
        prescriptions = self.prescription_parser.parse_prescription(text)
        logger.info(f"Parsed {len(prescriptions)} prescriptions")

        # Step 4: Combine into medical record
        medical_record = {
            'record_id': f"REC_{patient_info['patient_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'patient_id': patient_info['patient_id'],
            'patient_age': patient_info.get('age', 50),
            'date': datetime.now().isoformat(),
            'domain_info': domain_info,
            'file_name': os.path.basename(image_path),
            'file_path': image_path,
            'file_type': os.path.splitext(image_path)[1],
            'ocr_text': text,
            'ocr_confidence': ocr_result['confidence'],
            'diseases': entities['diseases'],
            'medications': prescriptions,
            'biomarkers': biomarker_values,
            'symptoms': entities['symptoms'],
            'procedures': entities['procedures'],
            'historical_biomarkers': patient_info.get('historical_biomarkers', [])
        }

        # Step 5: Anomaly detection
        logger.info("Step 5: Running 7-layer anomaly detection...")
        anomaly_results = self.anomaly_detector.detect_anomalies(medical_record)
        medical_record['anomaly_detection'] = anomaly_results
        logger.info(f"Overall severity score: {anomaly_results['overall_severity']}/100")

        if anomaly_results['critical_alerts']:
            logger.warning(f"CRITICAL ALERTS: {len(anomaly_results['critical_alerts'])}")

        # Step 5.5: Generate clinical report using OpenAI (if enabled)
        if self.enable_llm and self.response_generator:
            logger.info("Step 5.5: Generating AI clinical report...")
            try:
                report_result = self.response_generator.generate_anomaly_report(medical_record)
                if report_result['success']:
                    medical_record['clinical_summary'] = report_result['report']
                    medical_record['llm_metadata'] = {
                        'tokens_used': report_result['tokens_used'],
                        'model': report_result['model'],
                        'prompt_tokens': report_result['prompt_tokens'],
                        'completion_tokens': report_result['completion_tokens']
                    }
                    logger.info(f"Clinical report generated (tokens: {report_result['tokens_used']})")
                else:
                    logger.error(f"Failed to generate clinical report: {report_result.get('error')}")
            except Exception as e:
                logger.error(f"Error generating clinical report: {str(e)}")

        # Step 6: Generate embeddings
        logger.info("Step 6: Generating embeddings...")
        embedding = self.embeddings.embed_record(medical_record)

        # Step 7: Store in vector database
        logger.info("Step 7: Storing in vector database...")
        metadata = {
            'patient_id': medical_record['patient_id'],
            'date': medical_record['date'],
            'has_anomalies': len(anomaly_results['anomalies']) > 0,
            'severity': anomaly_results['overall_severity']
        }

        document = self.embeddings.create_medical_record_text(medical_record)

        self.vector_store.add_record(
            record_id=medical_record['record_id'],
            embedding=embedding.tolist(),
            metadata=metadata,
            document=document
        )

        logger.info("Document processing complete!")

        return medical_record

    def batch_process(self, documents: List[Dict]) -> List[Dict]:
        """Process multiple documents"""
        results = []

        for doc in documents:
            try:
                result = self.process_document(
                    image_path=doc['image_path'],
                    patient_info=doc['patient_info']
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {doc['image_path']}: {str(e)}")
                results.append({'error': str(e), 'document': doc})

        return results
