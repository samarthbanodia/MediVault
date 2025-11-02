from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import re
from typing import List, Dict

class MedicalNER:
    """Medical Named Entity Recognition using HuggingFace models"""

    def __init__(self):
        # Use Medical-NER model from HuggingFace
        model_name = "blaze999/Medical-NER"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.ner_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )

    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """Extract medical entities from text"""
        entities = self.ner_pipeline(text)

        # Categorize entities
        categorized = {
            'diseases': [],
            'medications': [],
            'biomarkers': [],
            'symptoms': [],
            'procedures': []
        }

        for entity in entities:
            entity_type = entity['entity_group'].upper()

            entity_data = {
                'text': entity['word'],
                'confidence': entity['score'],
                'start': entity['start'],
                'end': entity['end']
            }

            # Map entity types to categories
            if 'DISEASE' in entity_type or 'PROBLEM' in entity_type:
                categorized['diseases'].append(entity_data)
            elif 'DRUG' in entity_type or 'MEDICATION' in entity_type:
                categorized['medications'].append(entity_data)
            elif 'TEST' in entity_type or 'LAB' in entity_type:
                categorized['biomarkers'].append(entity_data)
            elif 'SYMPTOM' in entity_type:
                categorized['symptoms'].append(entity_data)
            elif 'PROCEDURE' in entity_type or 'TREATMENT' in entity_type:
                categorized['procedures'].append(entity_data)

        return categorized

    def extract_biomarker_values(self, text: str) -> List[Dict]:
        """Extract biomarker values using regex patterns"""
        patterns = {
            'glucose': r'(?:glucose|sugar|FBS|PPBS|RBS)[\s:]+(\d+\.?\d*)\s*(mg/dL|mmol/L)?',
            'hba1c': r'(?:HbA1c|A1C)[\s:]+(\d+\.?\d*)%?',
            'bp': r'(?:BP|blood pressure)[\s:]+(\d{2,3})/(\d{2,3})',
            'cholesterol': r'(?:cholesterol|LDL|HDL|triglycerides)[\s:]+(\d+\.?\d*)\s*(mg/dL)?',
            'hemoglobin': r'(?:hemoglobin|Hb|HGB)[\s:]+(\d+\.?\d*)\s*(g/dL)?',
            'creatinine': r'(?:creatinine)[\s:]+(\d+\.?\d*)\s*(mg/dL)?',
        }

        biomarkers = []

        for biomarker_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if biomarker_type == 'bp':
                    biomarkers.append({
                        'type': 'systolic_bp',
                        'value': float(match.group(1)),
                        'unit': 'mmHg'
                    })
                    biomarkers.append({
                        'type': 'diastolic_bp',
                        'value': float(match.group(2)),
                        'unit': 'mmHg'
                    })
                else:
                    biomarkers.append({
                        'type': biomarker_type,
                        'value': float(match.group(1)),
                        'unit': match.group(2) if match.lastindex > 1 else 'unknown'
                    })

        return biomarkers
