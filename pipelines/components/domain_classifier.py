"""
Medical Domain Classifier
Classifies medical documents into medical specialties/domains
"""

import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MedicalDomainClassifier:
    """Classify medical documents into medical domains/specialties"""

    def __init__(self):
        # Define keywords for each medical domain
        self.domain_keywords = {
            'radiology': [
                'x-ray', 'xray', 'ct scan', 'mri', 'ultrasound', 'sonography',
                'mammography', 'radiograph', 'imaging', 'pet scan', 'bone scan',
                'contrast', 'radiologist', 'fluoroscopy', 'doppler'
            ],
            'pathology': [
                'biopsy', 'histopathology', 'cytology', 'lab test', 'laboratory',
                'culture', 'microscopy', 'specimen', 'pathologist', 'tissue',
                'blood test', 'serum', 'plasma', 'urine test', 'stool test'
            ],
            'cardiology': [
                'ecg', 'ekg', 'echo', 'echocardiogram', 'stress test', 'angiography',
                'cardiac', 'heart', 'cardiologist', 'coronary', 'myocardial',
                'atrial', 'ventricular', 'arrhythmia', 'pacemaker', 'stent'
            ],
            'orthopedics': [
                'fracture', 'bone', 'joint', 'orthopedic', 'spine', 'vertebra',
                'arthritis', 'ligament', 'tendon', 'cartilage', 'orthopedist',
                'prosthesis', 'dislocation', 'sprain', 'osteo'
            ],
            'neurology': [
                'brain', 'neurolog', 'seizure', 'stroke', 'cerebral', 'neural',
                'eeg', 'spinal cord', 'nerve', 'dementia', 'alzheimer', 'parkinson',
                'epilepsy', 'migraine', 'neuropathy'
            ],
            'gastroenterology': [
                'gastro', 'endoscopy', 'colonoscopy', 'intestine', 'stomach',
                'liver', 'pancreas', 'colon', 'digestive', 'bowel', 'ulcer',
                'hepatitis', 'cirrhosis', 'gallbladder'
            ],
            'pulmonology': [
                'lung', 'pulmonary', 'respiratory', 'chest', 'bronch',
                'asthma', 'copd', 'pneumonia', 'tuberculosis', 'spirometry',
                'oxygen saturation', 'ventilation'
            ],
            'nephrology': [
                'kidney', 'renal', 'dialysis', 'creatinine', 'urea', 'nephr',
                'urinary', 'bladder', 'urolog'
            ],
            'endocrinology': [
                'diabetes', 'thyroid', 'hormone', 'insulin', 'glucose',
                'endocrine', 'metabolic', 'gland', 'hba1c', 'tsh', 'cortisol'
            ],
            'oncology': [
                'cancer', 'tumor', 'oncolog', 'chemotherapy', 'radiation therapy',
                'malignant', 'benign', 'metastasis', 'carcinoma', 'lymphoma',
                'leukemia', 'neoplasm'
            ],
            'dermatology': [
                'skin', 'derma', 'rash', 'lesion', 'melanoma', 'eczema',
                'psoriasis', 'acne', 'dermatitis', 'fungal'
            ],
            'ophthalmology': [
                'eye', 'vision', 'ophthalm', 'retina', 'cornea', 'cataract',
                'glaucoma', 'visual acuity', 'lens', 'optometry'
            ],
            'ent': [
                'ear', 'nose', 'throat', 'ent', 'otolaryngology', 'tonsil',
                'sinus', 'hearing', 'vertigo', 'nasal'
            ],
            'gynecology': [
                'gynecolog', 'obstetric', 'pregnancy', 'uterus', 'ovary',
                'menstrual', 'cervix', 'prenatal', 'pap smear', 'mammogram'
            ],
            'pediatrics': [
                'pediatric', 'child', 'infant', 'vaccination', 'growth chart',
                'neonatal', 'immunization'
            ],
            'psychiatry': [
                'mental health', 'psychiatric', 'depression', 'anxiety',
                'psychosis', 'bipolar', 'therapy', 'counseling', 'antidepressant'
            ]
        }

        # Document type indicators
        self.document_types = {
            'lab_report': [
                'lab report', 'laboratory report', 'blood test', 'test results',
                'pathology report', 'biochemistry', 'hematology'
            ],
            'prescription': [
                'prescription', 'rx:', 'medication', 'dosage', 'tablet',
                'capsule', 'syrup', 'ointment', 'prescribed'
            ],
            'discharge_summary': [
                'discharge summary', 'discharge note', 'hospital discharge',
                'admission', 'final diagnosis'
            ],
            'consultation_note': [
                'consultation', 'clinic note', 'clinical note', 'visit note',
                'examination', 'assessment'
            ],
            'imaging_report': [
                'radiology report', 'imaging report', 'scan report',
                'radiological findings', 'impression'
            ],
            'operative_note': [
                'operative note', 'surgery', 'surgical procedure', 'operation',
                'pre-operative', 'post-operative'
            ]
        }

    def classify_domain(self, text: str, entities: Dict = None) -> Dict:
        """
        Classify medical domain based on text content and extracted entities

        Args:
            text: OCR extracted text
            entities: Dict of extracted entities (diseases, medications, etc.)

        Returns:
            Dict with:
            - primary_domain: Main medical specialty
            - secondary_domains: List of other relevant domains
            - confidence: Confidence score
            - document_type: Type of document (lab report, prescription, etc.)
        """
        try:
            text_lower = text.lower()

            # Count keyword matches for each domain
            domain_scores = {}

            for domain, keywords in self.domain_keywords.items():
                score = 0
                for keyword in keywords:
                    # Count occurrences
                    pattern = r'\b' + re.escape(keyword) + r'\w*'
                    matches = len(re.findall(pattern, text_lower))
                    score += matches

                if score > 0:
                    domain_scores[domain] = score

            # Classify document type
            document_type = self._classify_document_type(text_lower)

            # If no domains detected, use general medicine
            if not domain_scores:
                return {
                    'primary_domain': 'general_medicine',
                    'secondary_domains': [],
                    'confidence': 0.5,
                    'document_type': document_type,
                    'domain_scores': {}
                }

            # Sort domains by score
            sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

            # Primary domain is highest scoring
            primary_domain = sorted_domains[0][0]
            primary_score = sorted_domains[0][1]

            # Secondary domains (within 50% of primary score)
            threshold = primary_score * 0.5
            secondary_domains = [
                domain for domain, score in sorted_domains[1:]
                if score >= threshold
            ]

            # Calculate confidence (normalized score)
            total_words = len(text_lower.split())
            confidence = min(primary_score / max(total_words, 1) * 100, 99.0)

            logger.info(f"Classified as {primary_domain} (confidence: {confidence:.1f}%)")

            return {
                'primary_domain': primary_domain,
                'secondary_domains': secondary_domains[:3],  # Top 3 secondary
                'confidence': confidence,
                'document_type': document_type,
                'domain_scores': dict(sorted_domains[:5])  # Top 5 for debugging
            }

        except Exception as e:
            logger.error(f"Error classifying domain: {e}")
            return {
                'primary_domain': 'general_medicine',
                'secondary_domains': [],
                'confidence': 0.0,
                'document_type': 'unknown',
                'error': str(e)
            }

    def _classify_document_type(self, text_lower: str) -> str:
        """Classify the type of medical document"""
        type_scores = {}

        for doc_type, keywords in self.document_types.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                type_scores[doc_type] = score

        if not type_scores:
            return 'general_record'

        # Return highest scoring type
        return max(type_scores.items(), key=lambda x: x[1])[0]

    def get_domain_display_name(self, domain: str) -> str:
        """Get human-friendly display name for domain"""
        display_names = {
            'radiology': 'Radiology & Imaging',
            'pathology': 'Pathology & Lab Tests',
            'cardiology': 'Cardiology',
            'orthopedics': 'Orthopedics',
            'neurology': 'Neurology',
            'gastroenterology': 'Gastroenterology',
            'pulmonology': 'Pulmonology & Respiratory',
            'nephrology': 'Nephrology & Urology',
            'endocrinology': 'Endocrinology & Metabolism',
            'oncology': 'Oncology',
            'dermatology': 'Dermatology',
            'ophthalmology': 'Ophthalmology',
            'ent': 'ENT',
            'gynecology': 'Gynecology & Obstetrics',
            'pediatrics': 'Pediatrics',
            'psychiatry': 'Psychiatry',
            'general_medicine': 'General Medicine'
        }
        return display_names.get(domain, domain.title())
