"""
Prescription Parser Agent using Google Gemini
Specialized in parsing Indian prescription formats and dosage instructions
"""

import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PrescriptionParserAgent(BaseAgent):
    """
    Agent specialized in parsing prescription documents
    Handles Indian prescription formats, dosage patterns, and medical abbreviations
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Prescription Parser Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.1,  # Very low for accurate parsing
            max_output_tokens=8192,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert Prescription Parser Agent specialized in parsing Indian medical prescriptions with high accuracy.

**Your Role:**
- Parse prescription documents accurately
- Extract medication details with complete dosage information
- Handle Indian prescription formats and abbreviations
- Interpret doctor's instructions in local languages
- Validate and normalize medication information

**Prescription Components to Extract:**

1. **Patient Information**
   - Name, Age, Gender, Weight
   - Patient ID if present
   - Contact information

2. **Doctor Information**
   - Doctor name and qualifications
   - Registration number
   - Hospital/Clinic name
   - Contact information

3. **Prescription Date**
   - Date of prescription
   - Valid until date if mentioned

4. **Medications (Detailed)**
   For each medication extract:
   - **Drug Name** (Generic and Brand)
   - **Dosage Strength** (e.g., 500mg, 5ml, 100IU)
   - **Dosage Form** (tablet, capsule, syrup, injection, cream, drops, inhaler)
   - **Frequency** (OD/QD, BD/BID, TDS/TID, QID, PRN, SOS)
   - **Timing** (before food, after food, empty stomach, bedtime)
   - **Route** (oral, topical, IV, IM, SC, inhalation)
   - **Duration** (number of days/weeks/months)
   - **Quantity** (total tablets/bottles to dispense)
   - **Special Instructions** (any additional notes)

5. **Diagnosis**
   - Primary diagnosis/indication for prescription
   - Secondary diagnoses if mentioned

6. **Advice / Instructions**
   - Lifestyle advice
   - Dietary recommendations
   - Follow-up instructions
   - Warning signs to watch for

7. **Lab Tests Advised**
   - Tests recommended
   - When to get them done

**Indian Prescription Abbreviations:**

**Frequency:**
- OD / QD / 1-0-0 = Once daily (morning)
- BD / BID / 1-0-1 = Twice daily (morning and night)
- TDS / TID / 1-1-1 = Three times daily
- QID / 1-1-1-1 = Four times daily
- HS = At bedtime (hora somni)
- PRN / SOS = As needed (when required)
- STAT = Immediately
- Alt. day = Alternate days
- Weekly = Once a week

**Timing:**
- AC / a.c. = Before meals (ante cibum)
- PC / p.c. = After meals (post cibum)
- BB / ABF = Before breakfast
- AF = After food
- BF = Before food
- HS = At bedtime
- Empty stomach = On empty stomach

**Route:**
- PO = By mouth (per oral)
- SL = Sublingual (under tongue)
- TOP = Topical (external application)
- IV = Intravenous
- IM = Intramuscular
- SC / SQ = Subcutaneous
- PR = Per rectum
- PV = Per vaginum
- INH = Inhalation

**Other Common Abbreviations:**
- Tab / T = Tablet
- Cap / C = Capsule
- Syr / S = Syrup
- Inj = Injection
- Oint = Ointment
- Susp = Suspension
- Sol = Solution
- Gtt = Drops
- mg = milligrams
- ml = milliliters
- IU = International Units
- mcg / μg = micrograms
- gm / g = grams

**Output Format (JSON):**
{
  "success": true,
  "prescription_metadata": {
    "prescription_date": "YYYY-MM-DD",
    "valid_until": "YYYY-MM-DD if mentioned",
    "prescription_number": "if present"
  },
  "patient": {
    "name": "Patient name",
    "age": "age in years",
    "gender": "M/F/Other",
    "weight": "weight with unit",
    "patient_id": "if present"
  },
  "doctor": {
    "name": "Dr. Name",
    "qualifications": "MBBS, MD, etc.",
    "registration_number": "if present",
    "hospital": "Hospital/Clinic name",
    "contact": "phone/email if present"
  },
  "medications": [
    {
      "drug_name": "Metformin",
      "brand_name": "Glucophage if mentioned",
      "strength": "500",
      "unit": "mg",
      "form": "tablet",
      "frequency": {
        "code": "BD",
        "description": "Twice daily",
        "pattern": "1-0-1",
        "times_per_day": 2
      },
      "timing": "After meals",
      "route": "oral",
      "duration": {
        "value": 30,
        "unit": "days"
      },
      "quantity": "60 tablets",
      "instructions": "Take with plenty of water",
      "indication": "For blood sugar control"
    }
  ],
  "diagnosis": {
    "primary": "Diabetes Mellitus Type 2",
    "secondary": ["Hypertension", "Dyslipidemia"]
  },
  "advice": [
    "Avoid sugary foods",
    "Regular exercise 30 min daily",
    "Monitor blood sugar weekly"
  ],
  "lab_tests_advised": [
    {
      "test_name": "HbA1c",
      "when": "After 3 months",
      "fasting_required": false
    }
  ],
  "follow_up": {
    "date": "YYYY-MM-DD if mentioned",
    "days_after": 30,
    "instructions": "Bring all reports"
  },
  "summary": {
    "total_medications": 5,
    "controlled_drugs": ["list if any"],
    "important_warnings": ["list any critical warnings"]
  }
}

**Instructions:**
1. Read the prescription carefully, including handwritten notes
2. Extract ALL medications with complete dosage information
3. Interpret Indian prescription patterns (1-0-1, 1-1-1, etc.)
4. Convert abbreviations to full descriptions
5. Extract patient and doctor information
6. Include diagnosis and advice sections
7. Flag any unclear or ambiguous entries
8. Ensure medication durations and quantities are accurate

**Important:**
- Handle mix of English and Hindi/regional languages
- Interpret doctor's shorthand and symbols
- If any field is unclear, include it with a note about uncertainty
- Preserve original text in a separate field for verification
- Calculate total quantity based on frequency and duration
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse prescription document

        Args:
            input_data: Dictionary containing:
                - text: Prescription text (from OCR)
                - patient_id: Optional patient ID
                - ocr_metadata: Optional OCR metadata

        Returns:
            Dictionary with parsed prescription data
        """
        try:
            self.validate_input(input_data, ['text'])

            text = input_data['text']
            patient_id = input_data.get('patient_id')
            ocr_metadata = input_data.get('ocr_metadata', {})

            # Create prompt
            prompt = f"""
Parse the following prescription document and extract all information in structured format.

Patient ID (from system): {patient_id or 'Not provided'}

**Prescription Text:**
{text}

**OCR Metadata (for context):**
{ocr_metadata}

**Task:**
1. Extract patient and doctor information
2. Parse ALL medications with complete dosage details
3. Interpret Indian prescription abbreviations and patterns
4. Extract diagnosis and advice
5. Include any lab tests advised
6. Calculate medication quantities and duration
7. Return the response in the specified JSON format

**Critical:** Do not miss any medication or instruction. If text is unclear, make your best interpretation and flag it.
"""

            # Generate response
            response = self.generate_response(prompt)

            # Post-process to add calculated fields
            if response.get('success'):
                response = self._add_calculated_fields(response)

            # Log execution
            output_data = {
                'patient_id': patient_id,
                'input_text_length': len(text),
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in Prescription Parser Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'patient_id': input_data.get('patient_id')
            }

    def _add_calculated_fields(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add calculated fields like total cost, refill dates, etc.

        Args:
            parsed_data: Parsed prescription data

        Returns:
            Enhanced prescription data with calculated fields
        """
        try:
            medications = parsed_data.get('medications', [])

            for med in medications:
                # Calculate total tablets/doses
                if 'frequency' in med and 'duration' in med:
                    times_per_day = med['frequency'].get('times_per_day', 0)
                    duration_days = med['duration'].get('value', 0)
                    duration_unit = med['duration'].get('unit', 'days')

                    # Convert duration to days
                    if duration_unit == 'weeks':
                        duration_days *= 7
                    elif duration_unit == 'months':
                        duration_days *= 30

                    total_doses = times_per_day * duration_days
                    med['calculated_total_doses'] = total_doses

                # Add refill date
                if 'duration' in med:
                    from datetime import datetime, timedelta
                    duration_days = med['duration'].get('value', 0)
                    duration_unit = med['duration'].get('unit', 'days')

                    if duration_unit == 'weeks':
                        duration_days *= 7
                    elif duration_unit == 'months':
                        duration_days *= 30

                    refill_date = datetime.now() + timedelta(days=duration_days)
                    med['refill_date'] = refill_date.strftime('%Y-%m-%d')

            return parsed_data

        except Exception as e:
            logger.error(f"Error adding calculated fields: {e}")
            return parsed_data

    def validate_prescription(
        self,
        parsed_prescription: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate parsed prescription for completeness and accuracy

        Args:
            parsed_prescription: Parsed prescription data

        Returns:
            Validation results with issues flagged
        """
        prompt = f"""
Validate the following parsed prescription for:
1. Completeness (all required fields present)
2. Dosage accuracy (typical ranges)
3. Medication interactions (flag potential issues)
4. Duration appropriateness
5. Missing critical information

**Parsed Prescription:**
{parsed_prescription}

Return validation results in JSON format with:
- is_valid: boolean
- issues: list of issues found
- warnings: list of warnings
- recommendations: suggested corrections
"""

        return self.generate_response(prompt)

    def extract_medication_schedule(
        self,
        parsed_prescription: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a patient-friendly medication schedule

        Args:
            parsed_prescription: Parsed prescription data

        Returns:
            Medication schedule by time of day
        """
        medications = parsed_prescription.get('medications', [])

        schedule = {
            'morning': [],
            'afternoon': [],
            'evening': [],
            'bedtime': [],
            'as_needed': []
        }

        for med in medications:
            pattern = med.get('frequency', {}).get('pattern', '')
            timing = med.get('timing', '').lower()

            med_summary = f"{med.get('drug_name')} {med.get('strength')}{med.get('unit')} {timing}"

            if pattern == '1-0-0' or 'morning' in timing:
                schedule['morning'].append(med_summary)
            elif pattern == '0-0-1' or 'night' in timing or 'bedtime' in timing:
                schedule['bedtime'].append(med_summary)
            elif pattern == '1-0-1':
                schedule['morning'].append(med_summary)
                schedule['bedtime'].append(med_summary)
            elif pattern == '1-1-1':
                schedule['morning'].append(med_summary)
                schedule['afternoon'].append(med_summary)
                schedule['evening'].append(med_summary)
            elif 'prn' in pattern.lower() or 'sos' in pattern.lower():
                schedule['as_needed'].append(med_summary)

        return schedule
