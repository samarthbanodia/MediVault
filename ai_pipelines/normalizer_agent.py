"""
Medical Records Normalizer Agent using Google Gemini
Normalizes and structures medical data for storage and analysis
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MedicalRecordsNormalizerAgent(BaseAgent):
    """
    Agent for normalizing and structuring medical records
    Converts unstructured data into standardized format for database storage
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Medical Records Normalizer Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_output_tokens=8192,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert Medical Records Normalizer Agent specialized in structuring and standardizing medical data.

**Your Role:**
- Transform unstructured medical data into standardized format
- Normalize medical terminology and codes
- Ensure data consistency and completeness
- Prepare data for database storage and analysis
- Create structured summaries for clinical use

**Normalization Tasks:**

1. **Terminology Standardization**
   - Map to standard medical terminologies (ICD-10, SNOMED CT, LOINC, RxNorm)
   - Normalize drug names (generic and brand)
   - Standardize disease names
   - Unify measurement units

2. **Data Structuring**
   - Convert free text into structured fields
   - Extract discrete data points
   - Organize into logical sections
   - Create relationships between entities

3. **Date/Time Normalization**
   - Convert all dates to ISO 8601 format (YYYY-MM-DD)
   - Extract timestamps where available
   - Infer missing dates from context

4. **Unit Standardization**
   - Convert all units to standard medical units
   - Ensure consistency (mg/dL, mmHg, g/dL, etc.)
   - Handle unit conversions when needed

5. **Completeness Validation**
   - Identify missing critical fields
   - Flag incomplete data
   - Suggest data enrichment

**Output Format (JSON):**
{
  "success": true,
  "normalized_record": {
    "record_metadata": {
      "record_id": "REC_20240115_123456",
      "patient_id": "patient UUID",
      "document_type": "prescription | lab_report | discharge_summary | etc.",
      "document_date": "YYYY-MM-DD",
      "created_at": "ISO timestamp",
      "source": "OCR | Manual Entry | EHR Import",
      "completeness_score": 0.0-1.0
    },
    "patient_information": {
      "name": "Normalized full name",
      "age": 45,
      "date_of_birth": "YYYY-MM-DD if available",
      "gender": "M | F | Other",
      "contact": {
        "phone": "normalized phone",
        "email": "email if present"
      }
    },
    "clinical_data": {
      "diagnoses": [
        {
          "name": "Diabetes Mellitus Type 2",
          "icd10_code": "E11",
          "snomed_code": "44054006",
          "status": "active | resolved | chronic",
          "onset_date": "YYYY-MM-DD",
          "severity": "mild | moderate | severe"
        }
      ],
      "medications": [
        {
          "generic_name": "Metformin",
          "brand_names": ["Glucophage"],
          "rxnorm_code": "6809",
          "dosage": {
            "strength": 500,
            "unit": "mg",
            "form": "tablet",
            "frequency": {
              "times_per_day": 2,
              "pattern": "1-0-1",
              "description": "Twice daily"
            },
            "route": "oral",
            "timing": "after meals"
          },
          "duration": {
            "value": 30,
            "unit": "days"
          },
          "start_date": "YYYY-MM-DD",
          "end_date": "YYYY-MM-DD",
          "status": "active | discontinued | completed"
        }
      ],
      "biomarkers": [
        {
          "name": "Hemoglobin A1c",
          "loinc_code": "4548-4",
          "value": 7.2,
          "unit": "%",
          "reference_range": {
            "min": 4.0,
            "max": 5.6,
            "unit": "%"
          },
          "interpretation": "high | normal | low",
          "test_date": "YYYY-MM-DD",
          "lab_name": "Lab name if available"
        }
      ],
      "vital_signs": [
        {
          "type": "blood_pressure",
          "systolic": 140,
          "diastolic": 90,
          "unit": "mmHg",
          "measurement_date": "YYYY-MM-DD",
          "measurement_time": "HH:MM if available"
        }
      ],
      "procedures": [
        {
          "name": "Electrocardiogram",
          "cpt_code": "93000",
          "procedure_date": "YYYY-MM-DD",
          "provider": "Doctor name",
          "findings": "Normal sinus rhythm"
        }
      ],
      "allergies": [
        {
          "allergen": "Penicillin",
          "type": "drug | food | environmental",
          "reaction": "Rash, hives",
          "severity": "mild | moderate | severe",
          "onset_date": "YYYY-MM-DD if known"
        }
      ]
    },
    "provider_information": {
      "doctor_name": "Dr. Full Name",
      "qualifications": "MBBS, MD",
      "registration_number": "if present",
      "specialty": "specialty if mentioned",
      "hospital": {
        "name": "Hospital name",
        "address": "if present",
        "contact": "phone/email"
      }
    },
    "clinical_summary": {
      "chief_complaint": "Main reason for visit",
      "assessment": "Clinical assessment",
      "plan": "Treatment plan",
      "follow_up": {
        "date": "YYYY-MM-DD",
        "instructions": "Follow-up instructions"
      }
    },
    "extracted_text": {
      "raw_text": "Original OCR text",
      "sections": {
        "header": "Header text",
        "body": "Body text",
        "footer": "Footer text"
      }
    }
  },
  "data_quality": {
    "completeness_score": 0.85,
    "confidence_score": 0.92,
    "missing_fields": ["date_of_birth", "patient_phone"],
    "data_quality_issues": ["Handwritten dosage unclear"],
    "validation_passed": true
  },
  "standardization_notes": [
    "Converted 'Sugar' to 'Glucose'",
    "Normalized date format from DD/MM/YYYY to YYYY-MM-DD",
    "Mapped 'DM' to 'Diabetes Mellitus Type 2' with ICD-10 E11"
  ]
}

**Standardization Rules:**

1. **Drug Name Normalization:**
   - Always provide generic name as primary
   - Include brand names in array
   - Use RxNorm codes when possible
   - Normalize dosage units (mg, mcg, ml, units)

2. **Disease Name Normalization:**
   - Use full medical terms (not abbreviations)
   - Provide ICD-10 codes
   - Include SNOMED codes if applicable
   - Example: "DM2" → "Diabetes Mellitus Type 2" (ICD-10: E11)

3. **Biomarker Normalization:**
   - Use standard lab test names
   - Provide LOINC codes when possible
   - Standardize units
   - Include reference ranges
   - Example: "Sugar" → "Glucose (Fasting)" with LOINC code

4. **Date Normalization:**
   - Always use YYYY-MM-DD format
   - Convert from any input format
   - Extract from various formats: 15/01/2024, Jan 15 2024, 15-01-24

5. **Unit Conversions:**
   - mg/dL (milligrams per deciliter) for glucose, cholesterol
   - mmHg (millimeters of mercury) for blood pressure
   - g/dL (grams per deciliter) for hemoglobin
   - % (percentage) for HbA1c
   - Convert between units when needed

**Instructions:**
1. Read all input data (OCR text, NER entities, parsed prescriptions)
2. Normalize all medical terms to standard terminology
3. Structure data according to output schema
4. Add appropriate medical codes (ICD-10, LOINC, RxNorm, CPT)
5. Validate data completeness and quality
6. Flag missing or questionable data
7. Create clinical summary
8. Return structured JSON response

**Important:**
- Preserve original extracted text for reference
- Do not invent data - mark fields as null if unknown
- Flag low-confidence fields
- Ensure all dates are in ISO format
- Maintain relationships between entities (e.g., which medication for which condition)
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and structure medical record data

        Args:
            input_data: Dictionary containing:
                - patient_id: Patient UUID
                - ocr_output: OCR extraction results
                - ner_output: NER entity extraction results
                - prescription_output: Parsed prescription (if applicable)
                - anomaly_output: Anomaly detection results
                - document_type: Type of document

        Returns:
            Dictionary with normalized medical record
        """
        try:
            self.validate_input(input_data, ['patient_id'])

            patient_id = input_data['patient_id']
            ocr_output = input_data.get('ocr_output', {})
            ner_output = input_data.get('ner_output', {})
            prescription_output = input_data.get('prescription_output', {})
            anomaly_output = input_data.get('anomaly_output', {})
            document_type = input_data.get('document_type', 'unknown')

            # Generate unique record ID
            record_id = self._generate_record_id()

            # Create comprehensive prompt
            prompt = f"""
Normalize and structure the following medical record data into standardized format.

**Record ID:** {record_id}
**Patient ID:** {patient_id}
**Document Type:** {document_type}

**OCR Output:**
{json.dumps(ocr_output, indent=2)}

**NER Output (Extracted Entities):**
{json.dumps(ner_output, indent=2)}

**Prescription Parse Output:**
{json.dumps(prescription_output, indent=2) if prescription_output else 'Not applicable'}

**Anomaly Detection Output:**
{json.dumps(anomaly_output, indent=2) if anomaly_output else 'Not yet analyzed'}

**Task:**
1. Combine all extracted information
2. Normalize medical terminology and codes
3. Structure according to output schema
4. Add ICD-10, LOINC, RxNorm codes where applicable
5. Standardize dates to YYYY-MM-DD format
6. Normalize units
7. Assess data completeness and quality
8. Create clinical summary
9. Return normalized record in specified JSON format

**Critical:** Ensure all data is properly structured and standardized for database storage.
"""

            # Generate response
            response = self.generate_response(prompt)

            # Add record metadata
            if response.get('success'):
                if 'normalized_record' in response:
                    response['normalized_record']['record_metadata']['record_id'] = record_id
                    response['normalized_record']['record_metadata']['patient_id'] = patient_id
                    response['normalized_record']['record_metadata']['created_at'] = datetime.utcnow().isoformat()

            # Log execution
            output_data = {
                'record_id': record_id,
                'patient_id': patient_id,
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in Normalizer Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'patient_id': input_data.get('patient_id')
            }

    def _generate_record_id(self) -> str:
        """Generate unique record ID"""
        from datetime import datetime
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        short_uuid = str(uuid.uuid4())[:8]
        return f"REC_{timestamp}_{short_uuid}"

    def validate_normalized_data(
        self,
        normalized_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate normalized data for completeness and accuracy

        Args:
            normalized_record: Normalized medical record

        Returns:
            Validation results
        """
        prompt = f"""
Validate the following normalized medical record for:
1. Data completeness (all critical fields present)
2. Data consistency (no contradictions)
3. Coding accuracy (ICD-10, LOINC, RxNorm)
4. Unit standardization
5. Date format compliance

**Normalized Record:**
{json.dumps(normalized_record, indent=2)}

Return validation results in JSON format with:
- is_valid: boolean
- validation_score: 0-100
- issues: list of issues found
- recommendations: suggested fixes
"""

        return self.generate_response(prompt)

    def merge_multiple_records(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple normalized records for the same patient

        Args:
            records: List of normalized medical records

        Returns:
            Merged comprehensive record
        """
        prompt = f"""
Merge the following medical records for the same patient into a comprehensive unified record.

**Records to Merge:**
{json.dumps(records, indent=2)}

**Task:**
1. Combine all diagnoses (remove duplicates)
2. Merge medication lists (mark discontinued ones)
3. Compile biomarker history
4. Create comprehensive timeline
5. Identify and resolve conflicts
6. Maintain data provenance (which record each data point came from)

Return merged record in normalized format.
"""

        return self.generate_response(prompt)

    def extract_for_database(
        self,
        normalized_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract data formatted specifically for database insertion

        Args:
            normalized_record: Normalized medical record

        Returns:
            Database-ready structured data
        """
        try:
            # Extract for relational database tables
            db_data = {
                'medical_records_table': {
                    'record_id': normalized_record['normalized_record']['record_metadata']['record_id'],
                    'patient_id': normalized_record['normalized_record']['record_metadata']['patient_id'],
                    'document_type': normalized_record['normalized_record']['record_metadata']['document_type'],
                    'document_date': normalized_record['normalized_record']['record_metadata']['document_date'],
                    'ocr_text': normalized_record['normalized_record']['extracted_text']['raw_text'],
                    'clinical_summary': json.dumps(normalized_record['normalized_record']['clinical_summary']),
                    'overall_severity': normalized_record.get('anomaly_output', {}).get('overall_severity', 0),
                    'created_at': normalized_record['normalized_record']['record_metadata']['created_at']
                },
                'biomarkers_table': [],
                'medications_table': [],
                'diagnoses_table': []
            }

            # Extract biomarkers
            for biomarker in normalized_record['normalized_record']['clinical_data'].get('biomarkers', []):
                db_data['biomarkers_table'].append({
                    'record_id': normalized_record['normalized_record']['record_metadata']['record_id'],
                    'patient_id': normalized_record['normalized_record']['record_metadata']['patient_id'],
                    'biomarker_type': biomarker['name'],
                    'value': biomarker['value'],
                    'unit': biomarker['unit'],
                    'normal_min': biomarker.get('reference_range', {}).get('min'),
                    'normal_max': biomarker.get('reference_range', {}).get('max'),
                    'is_abnormal': biomarker.get('interpretation') != 'normal',
                    'measurement_date': biomarker.get('test_date'),
                    'loinc_code': biomarker.get('loinc_code')
                })

            return db_data

        except Exception as e:
            logger.error(f"Error extracting database data: {e}")
            return {}
