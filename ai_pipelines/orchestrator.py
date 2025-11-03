"""
Agent Orchestrator for MediSense
Coordinates the multi-agent workflow according to the architecture diagram
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import chromadb
from chromadb.config import Settings

from .ocr_agent import OCRAgent
from .medical_ner_agent import MedicalNERAgent
from .prescription_parser_agent import PrescriptionParserAgent
from .anomaly_detection_agent import AnomalyDetectionAgent
from .normalizer_agent import MedicalRecordsNormalizerAgent
from .embedding_agent import EmbeddingAgent
from .search_agent import SearchAgent
from .ai_analyser_agent import AIAnalyserAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow for MediSense
    Implements the architecture shown in architecture.png

    Two main flows:
    1. Patient Flow: Upload → OCR → NER → Prescription Parser → Anomaly Detection → Normalizer → Embedding → Vector DB
    2. Smart Search: Query → Embedding → Semantic Search → AI Analyser → Response
    """

    def __init__(
        self,
        vector_db_path: str = "./chroma_db",
        collection_name: str = "medical_records",
        **agent_kwargs
    ):
        """
        Initialize orchestrator and all agents

        Args:
            vector_db_path: Path to ChromaDB storage
            collection_name: Name of ChromaDB collection
            agent_kwargs: Additional arguments for agents (e.g., api_key)
        """
        logger.info("Initializing Agent Orchestrator...")

        # Initialize all agents
        self.ocr_agent = OCRAgent(**agent_kwargs)
        self.ner_agent = MedicalNERAgent(**agent_kwargs)
        self.prescription_agent = PrescriptionParserAgent(**agent_kwargs)
        self.anomaly_agent = AnomalyDetectionAgent(**agent_kwargs)
        self.normalizer_agent = MedicalRecordsNormalizerAgent(**agent_kwargs)
        self.embedding_agent = EmbeddingAgent(**agent_kwargs)

        # Initialize vector database
        self.vector_db_client = chromadb.PersistentClient(
            path=vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.vector_db_client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.vector_db_client.create_collection(
                name=collection_name,
                metadata={"description": "MediSense medical records embeddings"}
            )
            logger.info(f"Created new collection: {collection_name}")

        # Initialize search and analyser agents with vector DB
        self.search_agent = SearchAgent(vector_db=self.collection, **agent_kwargs)
        self.analyser_agent = AIAnalyserAgent(**agent_kwargs)

        logger.info("Agent Orchestrator initialized successfully")

    def process_patient_document(
        self,
        file_path: str,
        patient_id: str,
        document_type: Optional[str] = None,
        patient_metadata: Optional[Dict[str, Any]] = None,
        historical_records: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        **PATIENT FLOW: Complete document processing pipeline**

        Flow: Upload → OCR → NER → Prescription Parser → Anomaly Detection → Normalizer → Embedding → Vector DB

        Args:
            file_path: Path to uploaded document image
            patient_id: Patient identifier
            document_type: Optional document type hint
            patient_metadata: Patient age, gender, conditions, medications
            historical_records: Previous records for trend analysis

        Returns:
            Complete processing result with all agent outputs
        """
        logger.info(f"Starting patient document processing for patient {patient_id}")

        processing_result = {
            'success': True,
            'patient_id': patient_id,
            'file_path': file_path,
            'pipeline_stages': {},
            'errors': []
        }

        try:
            # ===== STAGE 1: OCR - Text Extraction =====
            logger.info("Stage 1: OCR Text Extraction")
            ocr_result = self.ocr_agent.process({
                'file_path': file_path,
                'patient_id': patient_id
            })

            processing_result['pipeline_stages']['ocr'] = ocr_result

            if not ocr_result.get('success'):
                processing_result['success'] = False
                processing_result['errors'].append('OCR failed')
                return processing_result

            extracted_text = ocr_result.get('extracted_text', '')
            detected_document_type = ocr_result.get('document_type', document_type or 'unknown')

            # ===== STAGE 2: Medical NER - Entity Extraction =====
            logger.info("Stage 2: Medical NER Entity Extraction")
            ner_result = self.ner_agent.process({
                'text': extracted_text,
                'patient_id': patient_id,
                'document_type': detected_document_type
            })

            processing_result['pipeline_stages']['ner'] = ner_result

            # ===== STAGE 3: Prescription Parser (if applicable) =====
            prescription_result = None
            if detected_document_type in ['prescription', 'rx']:
                logger.info("Stage 3: Prescription Parsing")
                prescription_result = self.prescription_agent.process({
                    'text': extracted_text,
                    'patient_id': patient_id,
                    'ocr_metadata': ocr_result.get('metadata', {})
                })
                processing_result['pipeline_stages']['prescription'] = prescription_result

            # ===== STAGE 4: 7-Layer Anomaly Detection =====
            logger.info("Stage 4: 7-Layer Anomaly Detection")

            # Prepare current record data from NER and prescription results
            current_record_data = {
                'document_type': detected_document_type,
                'extracted_text': extracted_text,
                'entities': ner_result.get('entities', {}),
                'medications': prescription_result.get('medications', []) if prescription_result else [],
                'biomarkers': ner_result.get('entities', {}).get('biomarkers', []),
                'diseases': ner_result.get('entities', {}).get('diseases', [])
            }

            anomaly_result = self.anomaly_agent.process({
                'patient_id': patient_id,
                'current_record': current_record_data,
                'historical_records': historical_records or [],
                'patient_metadata': patient_metadata or {}
            })

            processing_result['pipeline_stages']['anomaly_detection'] = anomaly_result

            # ===== STAGE 5: Medical Records Normalizer =====
            logger.info("Stage 5: Medical Records Normalization")
            normalizer_result = self.normalizer_agent.process({
                'patient_id': patient_id,
                'ocr_output': ocr_result,
                'ner_output': ner_result,
                'prescription_output': prescription_result,
                'anomaly_output': anomaly_result,
                'document_type': detected_document_type
            })

            processing_result['pipeline_stages']['normalization'] = normalizer_result

            if not normalizer_result.get('success'):
                processing_result['errors'].append('Normalization failed')

            # ===== STAGE 6: Embedding Generation =====
            logger.info("Stage 6: Embedding Generation")

            # Prepare text for embedding (combine relevant fields)
            embedding_text = self._prepare_embedding_text(
                extracted_text,
                ner_result,
                prescription_result,
                detected_document_type
            )

            record_id = normalizer_result.get('normalized_record', {}).get('record_metadata', {}).get('record_id')

            embedding_result = self.embedding_agent.process({
                'text': embedding_text,
                'record_id': record_id,
                'patient_id': patient_id,
                'metadata': {
                    'document_type': detected_document_type,
                    'document_date': ocr_result.get('metadata', {}).get('document_date'),
                    'has_critical_alerts': anomaly_result.get('has_critical_alerts', False),
                    'overall_severity': anomaly_result.get('overall_severity', 0),
                    'text': embedding_text[:500]  # Store snippet for display
                }
            })

            processing_result['pipeline_stages']['embedding'] = embedding_result

            # ===== STAGE 7: Store in Vector Database =====
            logger.info("Stage 7: Storing in Vector Database")
            if embedding_result.get('success') and record_id:
                try:
                    self.collection.add(
                        ids=[record_id],
                        embeddings=[embedding_result['embedding']],
                        metadatas=[embedding_result['metadata']],
                        documents=[embedding_text]
                    )
                    processing_result['pipeline_stages']['vector_db'] = {
                        'success': True,
                        'record_id': record_id,
                        'stored': True
                    }
                    logger.info(f"Stored embedding for record {record_id}")
                except Exception as e:
                    logger.error(f"Error storing in vector DB: {e}")
                    processing_result['errors'].append(f'Vector DB storage failed: {str(e)}')

            # ===== FINAL RESULT =====
            processing_result['record_id'] = record_id
            processing_result['document_type'] = detected_document_type
            processing_result['has_critical_alerts'] = anomaly_result.get('has_critical_alerts', False)
            processing_result['overall_severity'] = anomaly_result.get('overall_severity', 0)
            processing_result['clinical_summary'] = normalizer_result.get('normalized_record', {}).get('clinical_summary', {})

            logger.info(f"Patient document processing completed successfully for {patient_id}")
            return processing_result

        except Exception as e:
            logger.error(f"Error in patient document processing: {e}")
            processing_result['success'] = False
            processing_result['errors'].append(str(e))
            return processing_result

    def smart_search(
        self,
        query: str,
        patient_id: Optional[str] = None,
        top_k: int = 5,
        include_entire_history: bool = False
    ) -> Dict[str, Any]:
        """
        **SMART SEARCH FLOW: Intelligent search and response generation**

        Flow: Query → Embedding → Semantic Search (3-5 results) → AI Analyser → Response

        Args:
            query: Natural language search query
            patient_id: Optional patient ID to limit search scope
            top_k: Number of top results to return (default 5)
            include_entire_history: Include full patient history in analysis

        Returns:
            Search results with AI-generated response
        """
        logger.info(f"Starting smart search for query: {query}")

        search_result = {
            'success': True,
            'query': query,
            'patient_id': patient_id,
            'stages': {},
            'errors': []
        }

        try:
            # ===== STAGE 1: Search with Embedding =====
            logger.info("Stage 1: Semantic Search")

            search_output = self.search_agent.process({
                'query': query,
                'patient_id': patient_id,
                'top_k': top_k,
                'search_mode': 'hybrid'  # Combines semantic + keyword
            })

            search_result['stages']['search'] = search_output

            if not search_output.get('success'):
                search_result['success'] = False
                search_result['errors'].append('Search failed')
                return search_result

            ranked_results = search_output.get('ranked_results', [])

            # ===== STAGE 2: Get Full Records for Top Results =====
            logger.info("Stage 2: Retrieving full record details")

            # In real implementation, fetch full records from database
            # For now, use search results directly
            top_matches = ranked_results[:top_k]

            # ===== STAGE 3: Optional - Get Entire Patient History =====
            entire_history = []
            if include_entire_history and patient_id:
                logger.info("Stage 3: Fetching entire patient history")
                # This would query database for all patient records
                # Placeholder for now
                entire_history = []

            # ===== STAGE 4: AI Analyser - Generate Response =====
            logger.info("Stage 4: AI Analysis and Response Generation")

            analyser_output = self.analyser_agent.process({
                'query': query,
                'search_results': top_matches,
                'patient_metadata': {},  # Would fetch from database
                'entire_history': entire_history,
                'response_mode': 'patient'  # or 'provider'
            })

            search_result['stages']['analysis'] = analyser_output

            # ===== FINAL RESULT =====
            search_result['response'] = analyser_output.get('answer', '')
            search_result['evidence'] = analyser_output.get('evidence', [])
            search_result['recommendations'] = analyser_output.get('recommendations', [])
            search_result['related_queries'] = analyser_output.get('related_queries', [])
            search_result['confidence_score'] = analyser_output.get('confidence_score', 0.0)
            search_result['disclaimer'] = analyser_output.get('disclaimer', '')

            logger.info("Smart search completed successfully")
            return search_result

        except Exception as e:
            logger.error(f"Error in smart search: {e}")
            search_result['success'] = False
            search_result['errors'].append(str(e))
            return search_result

    def _prepare_embedding_text(
        self,
        extracted_text: str,
        ner_result: Dict[str, Any],
        prescription_result: Optional[Dict[str, Any]],
        document_type: str
    ) -> str:
        """
        Prepare optimized text for embedding

        Args:
            extracted_text: Raw OCR text
            ner_result: NER extraction results
            prescription_result: Prescription parsing results
            document_type: Document type

        Returns:
            Optimized text for embedding
        """
        # Start with document type
        parts = [f"Document Type: {document_type}"]

        # Add extracted entities
        entities = ner_result.get('entities', {})

        if entities.get('diseases'):
            diseases = [d.get('name', '') for d in entities['diseases']]
            parts.append(f"Diseases: {', '.join(diseases)}")

        if entities.get('medications'):
            meds = [f"{m.get('name', '')} {m.get('dosage', '')}{m.get('unit', '')}"
                   for m in entities['medications']]
            parts.append(f"Medications: {', '.join(meds)}")

        if entities.get('biomarkers'):
            biomarkers = [f"{b.get('name', '')}: {b.get('value', '')} {b.get('unit', '')}"
                         for b in entities['biomarkers']]
            parts.append(f"Lab Values: {', '.join(biomarkers)}")

        # Add prescription info if available
        if prescription_result and prescription_result.get('success'):
            diagnosis = prescription_result.get('diagnosis', {})
            if diagnosis.get('primary'):
                parts.append(f"Diagnosis: {diagnosis['primary']}")

        # Add original text (truncated)
        parts.append(f"Content: {extracted_text[:1000]}")

        return "\n".join(parts)

    def get_patient_summary(
        self,
        patient_id: str,
        patient_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive patient summary

        Args:
            patient_id: Patient identifier
            patient_metadata: Patient demographic and clinical data

        Returns:
            Comprehensive summary
        """
        # Search for all patient records
        results = self.collection.get(
            where={"patient_id": patient_id}
        )

        # Use AI Analyser to generate summary
        return self.analyser_agent.process({
            'query': 'Provide a comprehensive summary of my health records',
            'search_results': results.get('metadatas', []),
            'patient_metadata': patient_metadata or {},
            'response_mode': 'patient'
        })

    def get_critical_alerts(
        self,
        patient_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all critical alerts across patients or for specific patient

        Args:
            patient_id: Optional patient ID filter

        Returns:
            List of critical alerts
        """
        where_filter = {"patient_id": patient_id, "has_critical_alerts": True} if patient_id else {"has_critical_alerts": True}

        try:
            results = self.collection.get(
                where=where_filter
            )

            return results.get('metadatas', [])
        except Exception as e:
            logger.error(f"Error getting critical alerts: {e}")
            return []

    def batch_process_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple documents in batch

        Args:
            documents: List of dicts with file_path, patient_id, etc.

        Returns:
            List of processing results
        """
        results = []

        for doc in documents:
            result = self.process_patient_document(
                file_path=doc['file_path'],
                patient_id=doc['patient_id'],
                document_type=doc.get('document_type'),
                patient_metadata=doc.get('patient_metadata'),
                historical_records=doc.get('historical_records')
            )
            results.append(result)

        return results
