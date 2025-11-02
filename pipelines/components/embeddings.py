from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union, Dict

class MedicalEmbeddings:
    """Generate multilingual embeddings for medical records"""

    def __init__(self, model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
        """
        Initialize embedding model

        Options:
        - 'paraphrase-multilingual-mpnet-base-v2' (multilingual, 768 dim)
        - 'all-MiniLM-L6-v2' (English only, 384 dim, faster)
        - 'sentence-transformers/all-mpnet-base-v2' (English, 768 dim, best quality)
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def create_medical_record_text(self, record: Dict) -> str:
        """Convert structured medical record to searchable text"""
        parts = []

        # Patient info
        if 'patient_id' in record:
            parts.append(f"Patient: {record['patient_id']}")

        # Domain Info
        if 'domain_info' in record and isinstance(record['domain_info'], dict):
            primary_domain = record['domain_info'].get('primary_domain', '')
            doc_type = record['domain_info'].get('document_type', '')
            if primary_domain:
                parts.append(f"Domain: {primary_domain}")
            if doc_type:
                parts.append(f"Document Type: {doc_type}")

        # Diseases
        if 'diseases' in record:
            diseases = []
            for d in record['diseases']:
                if isinstance(d, dict):
                    diseases.append(d.get('text', ''))
                else:
                    diseases.append(str(d))
            if diseases:
                parts.append(f"Conditions: {', '.join(diseases)}")

        # Medications
        if 'medications' in record:
            meds = []
            for m in record['medications']:
                if isinstance(m, dict):
                    med_name = m.get('medication', '')
                    if med_name:
                        meds.append(med_name)
                else:
                    meds.append(str(m))
            if meds:
                parts.append(f"Medications: {', '.join(meds)}")

        # Biomarkers
        if 'biomarkers' in record:
            biomarkers = [f"{b['type']}: {b['value']}" for b in record['biomarkers']]
            if biomarkers:
                parts.append(f"Test results: {', '.join(biomarkers)}")

        # Symptoms
        if 'symptoms' in record:
            symptoms = []
            for s in record['symptoms']:
                if isinstance(s, dict):
                    symptoms.append(s.get('text', ''))
                else:
                    symptoms.append(str(s))
            if symptoms:
                parts.append(f"Symptoms: {', '.join(symptoms)}")

        # Procedures
        if 'procedures' in record:
            procedures = []
            for p in record['procedures']:
                if isinstance(p, dict):
                    procedures.append(p.get('text', ''))
                else:
                    procedures.append(str(p))
            if procedures:
                parts.append(f"Procedures: {', '.join(procedures)}")

        # Date
        if 'date' in record:
            parts.append(f"Date: {record['date']}")

        # Clinical Summary
        if 'clinical_summary' in record:
            parts.append(f"Summary: {record['clinical_summary']}")

        # Anomalies
        if 'anomaly_detection' in record and isinstance(record['anomaly_detection'], dict):
            anomalies = record['anomaly_detection'].get('anomalies', [])
            if anomalies:
                anomaly_texts = [a.get('message', '') for a in anomalies]
                parts.append(f"Anomalies: {', '.join(anomaly_texts)}")

        return ' | '.join(parts)

    def embed_record(self, record: Dict) -> np.ndarray:
        """Generate embedding for a medical record"""
        text = self.create_medical_record_text(record)
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_records(self, records: List[Dict]) -> np.ndarray:
        """Generate embeddings for multiple records (batched)"""
        texts = [self.create_medical_record_text(r) for r in records]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for search query"""
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
