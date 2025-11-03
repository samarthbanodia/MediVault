"""
Medical NER Agent using Google Gemini
Extracts medical entities (diseases, medications, biomarkers) from text
"""

import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MedicalNERAgent(BaseAgent):
    """
    Agent for Named Entity Recognition in medical text
    Extracts diseases, medications, biomarkers, symptoms, and procedures
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Medical NER Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.2,
            max_output_tokens=8192,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert Medical Named Entity Recognition (NER) Agent specialized in extracting medical entities from clinical text.

**Your Role:**
- Extract ALL medical entities from the provided text
- Categorize entities accurately
- Normalize medical terminology
- Extract contextual information (severity, dosage, frequency)
- Handle abbreviations and medical shorthand
- Support multiple languages (English, Hindi, regional languages)

**Entity Categories to Extract:**

1. **DISEASES / CONDITIONS**
   - Diagnoses, diseases, medical conditions
   - Include ICD codes if mentioned
   - Examples: Diabetes Mellitus Type 2, Hypertension, COVID-19

2. **MEDICATIONS**
   - Drug names (generic and brand)
   - Dosage (mg, ml, units)
   - Frequency (OD, BD, TDS, QID, PRN)
   - Route (oral, IV, topical, etc.)
   - Duration (days, weeks, months)
   - Examples: Metformin 500mg BD, Aspirin 75mg OD

3. **BIOMARKERS / LAB VALUES**
   - Lab test names
   - Measured values with units
   - Normal ranges if provided
   - Examples: HbA1c: 7.2%, Glucose: 145 mg/dL

4. **SYMPTOMS**
   - Patient complaints and symptoms
   - Severity indicators
   - Duration
   - Examples: Fever (3 days), Severe headache

5. **PROCEDURES**
   - Medical procedures, surgeries, tests ordered
   - Examples: ECG, CT Scan, Appendectomy

6. **VITAL SIGNS**
   - Blood pressure, heart rate, temperature, etc.
   - Examples: BP: 140/90 mmHg, Pulse: 82 bpm

7. **ALLERGIES**
   - Drug allergies, food allergies
   - Examples: Allergic to Penicillin

**Output Format (JSON):**
{
  "success": true,
  "entities": {
    "diseases": [
      {
        "name": "Diabetes Mellitus Type 2",
        "normalized_name": "Type 2 Diabetes",
        "code": "E11" (ICD-10 if identifiable),
        "severity": "moderate|severe|mild",
        "status": "active|resolved|chronic",
        "mentioned_text": "exact text from document"
      }
    ],
    "medications": [
      {
        "name": "Metformin",
        "brand_name": "Glucophage if mentioned",
        "dosage": "500",
        "unit": "mg",
        "frequency": "BD (twice daily)",
        "route": "oral",
        "duration": "30 days",
        "instructions": "after meals",
        "mentioned_text": "exact text from document"
      }
    ],
    "biomarkers": [
      {
        "name": "HbA1c",
        "value": "7.2",
        "unit": "%",
        "normal_range": "4.0-5.6",
        "is_abnormal": true,
        "test_date": "YYYY-MM-DD if available",
        "mentioned_text": "exact text from document"
      }
    ],
    "symptoms": [
      {
        "name": "Fever",
        "severity": "mild|moderate|severe",
        "duration": "3 days",
        "mentioned_text": "exact text from document"
      }
    ],
    "procedures": [
      {
        "name": "ECG",
        "date": "YYYY-MM-DD if available",
        "findings": "any findings mentioned",
        "mentioned_text": "exact text from document"
      }
    ],
    "vital_signs": [
      {
        "type": "blood_pressure",
        "systolic": 140,
        "diastolic": 90,
        "unit": "mmHg",
        "mentioned_text": "exact text from document"
      }
    ],
    "allergies": [
      {
        "allergen": "Penicillin",
        "type": "drug|food|environmental",
        "reaction": "rash, anaphylaxis, etc.",
        "mentioned_text": "exact text from document"
      }
    ]
  },
  "summary": {
    "total_entities": 25,
    "entity_counts": {
      "diseases": 3,
      "medications": 5,
      "biomarkers": 8,
      "symptoms": 4,
      "procedures": 2,
      "vital_signs": 2,
      "allergies": 1
    },
    "primary_diagnosis": "Main diagnosis if identifiable",
    "critical_findings": ["List of critical or urgent findings"]
  },
  "confidence": 0.0-1.0
}

**Instructions:**
1. Read the entire text carefully
2. Extract ALL medical entities, even ambiguous ones
3. Normalize names to standard medical terminology
4. Preserve exact dosages, values, and units
5. Extract contextual information (frequency, severity, duration)
6. Identify relationships between entities
7. Flag critical or abnormal findings
8. Handle abbreviations (e.g., OD = once daily, BD = twice daily, HTN = Hypertension)

**Common Abbreviations:**
- OD/QD: Once daily
- BD/BID: Twice daily
- TDS/TID: Three times daily
- QID: Four times daily
- PRN: As needed
- HTN: Hypertension
- DM: Diabetes Mellitus
- MI: Myocardial Infarction
- COPD: Chronic Obstructive Pulmonary Disease
- BP: Blood Pressure
- HR: Heart Rate
- RR: Respiratory Rate

**Important:**
- Do NOT skip any medical entity
- If unsure about an entity, include it with lower confidence
- Preserve original units and values exactly
- Extract dates in ISO format (YYYY-MM-DD) when possible
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract medical entities from text

        Args:
            input_data: Dictionary containing:
                - text: Medical text to analyze
                - patient_id: Optional patient ID
                - document_type: Optional document type for context

        Returns:
            Dictionary with extracted entities
        """
        try:
            self.validate_input(input_data, ['text'])

            text = input_data['text']
            patient_id = input_data.get('patient_id')
            document_type = input_data.get('document_type', 'unknown')

            # Create prompt
            prompt = f"""
Extract all medical entities from the following {document_type} text.

Patient ID: {patient_id or 'Not provided'}

**Text to Analyze:**
{text}

**Task:**
1. Extract all diseases, medications, biomarkers, symptoms, procedures, vital signs, and allergies
2. Normalize entity names to standard medical terminology
3. Extract contextual information (dosages, frequencies, values, units)
4. Identify critical or abnormal findings
5. Return the response in the specified JSON format

**Important:** Be thorough and extract ALL medical entities, even if confidence is not 100%.
"""

            # Generate response
            response = self.generate_response(prompt)

            # Log execution
            output_data = {
                'patient_id': patient_id,
                'document_type': document_type,
                'input_text_length': len(text),
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in Medical NER Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'patient_id': input_data.get('patient_id')
            }

    def extract_specific_entity_type(
        self,
        text: str,
        entity_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extract only specific type of entities

        Args:
            text: Medical text
            entity_type: Type of entity (diseases, medications, biomarkers, etc.)

        Returns:
            List of extracted entities of specified type
        """
        result = self.process({'text': text})

        if result.get('success'):
            entities = result.get('entities', {})
            return entities.get(entity_type, [])

        return []

    def validate_entities(
        self,
        entities: Dict[str, Any],
        reference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate extracted entities against reference data

        Args:
            entities: Extracted entities
            reference_data: Reference medical data for validation

        Returns:
            Validation results with corrections
        """
        prompt = f"""
Validate and correct the following extracted medical entities against the provided reference data.

**Extracted Entities:**
{entities}

**Reference Data:**
{reference_data}

**Task:**
1. Check if entity names are correctly spelled
2. Verify units and normal ranges for biomarkers
3. Validate medication dosages against typical ranges
4. Flag any suspicious or incorrect values
5. Suggest corrections if needed

Return validated entities with corrections in JSON format.
"""

        return self.generate_response(prompt, context={'entities': entities})
