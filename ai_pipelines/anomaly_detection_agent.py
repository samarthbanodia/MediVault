"""
7-Layer Anomaly Detection Agent using Google Gemini
Advanced medical anomaly detection with severity scoring
"""

import logging
from typing import Dict, Any, List
import json

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AnomalyDetectionAgent(BaseAgent):
    """
    Agent for 7-layer medical anomaly detection
    Provides comprehensive analysis of medical records for critical findings
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="7-Layer Anomaly Detection Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.2,
            max_output_tokens=8192,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert 7-Layer Medical Anomaly Detection Agent specialized in identifying health risks and critical medical findings.

**Your Role:**
- Analyze medical records through 7 comprehensive layers
- Detect anomalies, critical values, and health risks
- Provide severity scoring (0-100) for each finding
- Generate actionable recommendations for healthcare providers
- Prioritize life-threatening conditions

**7-Layer Anomaly Detection System:**

### **Layer 1: Range Check Against Normal Values**
- Compare biomarker values against standard normal ranges
- Flag values outside normal range
- Consider age and gender-specific ranges
- Examples:
  - Glucose: Normal 70-100 mg/dL (fasting)
  - HbA1c: Normal <5.7%
  - Blood Pressure: Normal <120/80 mmHg
  - Hemoglobin: Normal 13.5-17.5 g/dL (male), 12.0-15.5 g/dL (female)

### **Layer 2: Critical Value Detection (Emergency Alerts)**
- Identify life-threatening values requiring immediate action
- Flag values that need urgent medical attention
- Examples:
  - Glucose <50 or >400 mg/dL (hypoglycemia/hyperglycemia crisis)
  - Systolic BP >180 or <90 mmHg (hypertensive crisis/shock)
  - Hemoglobin <7 g/dL (severe anemia)
  - Creatinine >3.0 mg/dL (kidney failure)
  - Potassium <2.5 or >6.0 mEq/L (cardiac risk)

### **Layer 3: Age-Adjusted Reference Ranges**
- Apply age-specific normal ranges
- Consider pediatric vs adult vs geriatric populations
- Adjust thresholds based on patient age
- Examples:
  - Blood pressure norms vary by age
  - Cholesterol targets differ for elderly
  - Kidney function decline is normal with aging

### **Layer 4: Medication Context Analysis**
- Analyze medication-biomarker interactions
- Detect drug-drug interactions
- Flag medication side effects
- Identify over-medication or under-medication
- Check contraindications
- Examples:
  - Statins + high creatinine = kidney risk
  - Beta blockers + low heart rate = bradycardia risk
  - NSAIDs + anticoagulants = bleeding risk
  - Multiple antihypertensives + low BP = hypotension

### **Layer 5: Trend Analysis on Historical Data**
- Compare current values with previous readings
- Detect concerning trends (declining/increasing)
- Calculate rate of change
- Flag rapid deterioration
- Examples:
  - HbA1c increasing from 6.5% → 7.2% → 8.1% (worsening diabetes)
  - Creatinine trending up = declining kidney function
  - Weight loss >5% in 1 month = concerning
  - Hemoglobin declining = possible bleeding

### **Layer 6: Comorbidity Pattern Detection**
- Identify disease combinations that increase risk
- Detect metabolic syndrome patterns
- Flag high-risk disease combinations
- Examples:
  - Diabetes + Hypertension + High Cholesterol = Cardiovascular risk
  - COPD + Heart Failure = Poor prognosis
  - Diabetes + Kidney Disease = Accelerated decline
  - Multiple chronic conditions = Polypharmacy risk

### **Layer 7: Comprehensive Risk Scoring (0-100)**
- Aggregate findings from all layers
- Calculate overall health risk score
- Provide severity classification
- Generate priority ranking for interventions
- Risk Categories:
  - 0-20: Minimal risk (routine follow-up)
  - 21-40: Low risk (monitor)
  - 41-60: Moderate risk (intervention needed)
  - 61-80: High risk (urgent attention)
  - 81-100: Critical risk (immediate action)

**Output Format (JSON):**
{
  "success": true,
  "overall_severity": 65,
  "risk_category": "high",
  "has_critical_alerts": true,
  "anomalies": [
    {
      "anomaly_id": "ANO_001",
      "layer": "Layer 2: Critical Value Detection",
      "layer_number": 2,
      "type": "critical_biomarker",
      "severity": 85,
      "is_critical": true,
      "title": "Severe Hyperglycemia",
      "description": "Blood glucose 425 mg/dL - Critical hyperglycemia requiring immediate medical attention",
      "affected_biomarker": {
        "name": "Glucose",
        "value": 425,
        "unit": "mg/dL",
        "normal_range": "70-100 mg/dL",
        "deviation": "+325%"
      },
      "recommendation": "Immediate emergency department visit. Risk of diabetic ketoacidosis. Check ketones, start insulin protocol.",
      "urgency": "immediate",
      "clinical_impact": "Life-threatening if untreated. Risk of DKA, coma, organ damage."
    }
  ],
  "layer_summaries": {
    "layer_1_range_check": {
      "abnormal_count": 5,
      "findings": ["High HbA1c", "Elevated cholesterol", "Low vitamin D"]
    },
    "layer_2_critical_values": {
      "critical_count": 1,
      "findings": ["Critical hyperglycemia"]
    },
    "layer_3_age_adjusted": {
      "patient_age": 65,
      "age_specific_concerns": ["Kidney function decline expected with age"]
    },
    "layer_4_medication_analysis": {
      "interactions_found": 2,
      "findings": ["Metformin dose may be too high for current kidney function"]
    },
    "layer_5_trend_analysis": {
      "concerning_trends": 3,
      "findings": ["HbA1c increasing over 6 months", "Creatinine trending up"]
    },
    "layer_6_comorbidity_patterns": {
      "patterns_detected": 1,
      "findings": ["Metabolic syndrome: Diabetes + HTN + Dyslipidemia"]
    },
    "layer_7_risk_scoring": {
      "overall_risk": 65,
      "category": "high",
      "factors": ["Uncontrolled diabetes", "Declining kidney function"]
    }
  },
  "priority_actions": [
    {
      "priority": 1,
      "action": "Emergency evaluation for hyperglycemia",
      "timeline": "Immediate (within 1 hour)"
    },
    {
      "priority": 2,
      "action": "Review and adjust diabetes medications",
      "timeline": "Urgent (within 24 hours)"
    }
  ],
  "patient_summary": {
    "total_anomalies": 8,
    "critical_count": 1,
    "high_severity_count": 3,
    "moderate_severity_count": 4,
    "key_concerns": [
      "Uncontrolled diabetes with critical hyperglycemia",
      "Declining kidney function",
      "Suboptimal medication management"
    ]
  }
}

**Instructions:**
1. Analyze ALL provided medical data through each of the 7 layers
2. Assign accurate severity scores (0-100) based on clinical significance
3. Flag critical findings that require immediate attention
4. Provide specific, actionable recommendations
5. Consider patient context (age, existing conditions, medications)
6. Prioritize findings by urgency
7. Use clinical judgment to assess overall risk

**Severity Scoring Guidelines:**
- 0-20: Normal variation, routine monitoring
- 21-40: Mild abnormality, lifestyle modification recommended
- 41-60: Moderate concern, medical intervention recommended
- 61-80: Serious concern, urgent medical attention needed
- 81-100: Life-threatening, emergency intervention required

**Urgency Levels:**
- Immediate: Within 1 hour (emergency)
- Urgent: Within 24 hours
- Soon: Within 1 week
- Routine: Within 1 month
- Monitoring: Regular follow-up

**Important:**
- Do NOT downplay critical findings
- Be specific about risks and recommendations
- Consider drug interactions carefully
- Factor in patient's complete medical history
- Prioritize patient safety above all
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze medical records through 7-layer anomaly detection

        Args:
            input_data: Dictionary containing:
                - patient_id: Patient identifier
                - current_record: Current medical record data
                - historical_records: List of previous records for trend analysis
                - patient_metadata: Age, gender, existing conditions
                - reference_data: Normal ranges and thresholds

        Returns:
            Dictionary with anomaly detection results
        """
        try:
            self.validate_input(input_data, ['patient_id', 'current_record'])

            patient_id = input_data['patient_id']
            current_record = input_data['current_record']
            historical_records = input_data.get('historical_records', [])
            patient_metadata = input_data.get('patient_metadata', {})
            reference_data = input_data.get('reference_data', {})

            # Load reference data if not provided
            if not reference_data:
                reference_data = self._load_reference_data()

            # Create comprehensive prompt
            prompt = f"""
Perform 7-layer anomaly detection on this patient's medical records.

**Patient Information:**
- Patient ID: {patient_id}
- Age: {patient_metadata.get('age', 'Unknown')}
- Gender: {patient_metadata.get('gender', 'Unknown')}
- Existing Conditions: {patient_metadata.get('conditions', [])}
- Current Medications: {patient_metadata.get('medications', [])}

**Current Medical Record:**
{json.dumps(current_record, indent=2)}

**Historical Records (for trend analysis):**
{json.dumps(historical_records[:5], indent=2) if historical_records else 'No historical data available'}

**Reference Data (Normal Ranges):**
{json.dumps(reference_data, indent=2)}

**Task:**
Analyze this patient's data through ALL 7 layers:
1. Range Check - Compare biomarkers against normal values
2. Critical Value Detection - Identify life-threatening values
3. Age-Adjusted Analysis - Apply age-specific ranges
4. Medication Context - Check drug interactions and side effects
5. Trend Analysis - Compare with historical data
6. Comorbidity Patterns - Identify high-risk disease combinations
7. Risk Scoring - Calculate overall risk (0-100)

Return comprehensive anomaly detection results in the specified JSON format.

**Critical:** Do not miss any concerning findings. Patient safety is paramount.
"""

            # Generate response
            response = self.generate_response(prompt)

            # Post-process to ensure critical fields
            if response.get('success'):
                response = self._ensure_critical_fields(response)

            # Log execution
            output_data = {
                'patient_id': patient_id,
                'analysis_timestamp': self._get_timestamp(),
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in Anomaly Detection Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'patient_id': input_data.get('patient_id')
            }

    def _load_reference_data(self) -> Dict[str, Any]:
        """Load reference data for normal ranges"""
        try:
            import os
            reference_file = os.path.join('data', 'biomarker_ranges.json')
            if os.path.exists(reference_file):
                with open(reference_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load reference data: {e}")

        # Default reference ranges
        return {
            "glucose_fasting": {"min": 70, "max": 100, "unit": "mg/dL", "critical_low": 50, "critical_high": 400},
            "hba1c": {"min": 0, "max": 5.6, "unit": "%", "critical_high": 9.0},
            "blood_pressure_systolic": {"min": 90, "max": 120, "unit": "mmHg", "critical_low": 90, "critical_high": 180},
            "blood_pressure_diastolic": {"min": 60, "max": 80, "unit": "mmHg", "critical_low": 60, "critical_high": 110},
            "cholesterol_total": {"min": 0, "max": 200, "unit": "mg/dL"},
            "cholesterol_ldl": {"min": 0, "max": 100, "unit": "mg/dL"},
            "cholesterol_hdl": {"min": 40, "max": 200, "unit": "mg/dL"},
            "triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
            "hemoglobin_male": {"min": 13.5, "max": 17.5, "unit": "g/dL", "critical_low": 7.0},
            "hemoglobin_female": {"min": 12.0, "max": 15.5, "unit": "g/dL", "critical_low": 7.0},
            "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "critical_high": 3.0}
        }

    def _ensure_critical_fields(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all critical fields are present in response"""
        if 'overall_severity' not in response:
            response['overall_severity'] = 0

        if 'has_critical_alerts' not in response:
            critical_anomalies = [
                a for a in response.get('anomalies', [])
                if a.get('is_critical', False) or a.get('severity', 0) > 80
            ]
            response['has_critical_alerts'] = len(critical_anomalies) > 0

        if 'risk_category' not in response:
            severity = response.get('overall_severity', 0)
            if severity >= 81:
                response['risk_category'] = 'critical'
            elif severity >= 61:
                response['risk_category'] = 'high'
            elif severity >= 41:
                response['risk_category'] = 'moderate'
            elif severity >= 21:
                response['risk_category'] = 'low'
            else:
                response['risk_category'] = 'minimal'

        return response

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def analyze_single_biomarker(
        self,
        biomarker: Dict[str, Any],
        patient_age: int,
        patient_gender: str
    ) -> Dict[str, Any]:
        """
        Analyze a single biomarker value

        Args:
            biomarker: Biomarker data with name, value, unit
            patient_age: Patient age in years
            patient_gender: Patient gender (M/F/Other)

        Returns:
            Analysis results for this biomarker
        """
        prompt = f"""
Analyze this single biomarker value using the 7-layer approach:

**Biomarker:** {biomarker.get('name')}
**Value:** {biomarker.get('value')} {biomarker.get('unit')}
**Patient Age:** {patient_age}
**Patient Gender:** {patient_gender}

Provide:
1. Normal range for this patient
2. Severity assessment (0-100)
3. Clinical significance
4. Recommendations

Return results in JSON format.
"""

        return self.generate_response(prompt)

    def compare_with_guidelines(
        self,
        detected_anomalies: List[Dict[str, Any]],
        clinical_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate detected anomalies against clinical guidelines

        Args:
            detected_anomalies: List of detected anomalies
            clinical_guidelines: Clinical practice guidelines

        Returns:
            Validation results with guideline compliance
        """
        prompt = f"""
Validate these detected anomalies against clinical guidelines:

**Detected Anomalies:**
{json.dumps(detected_anomalies, indent=2)}

**Clinical Guidelines:**
{json.dumps(clinical_guidelines, indent=2)}

Check:
1. Are severity assessments aligned with guidelines?
2. Are recommendations evidence-based?
3. Any missed risk factors per guidelines?
4. Guideline compliance score (0-100)

Return validation in JSON format.
"""

        return self.generate_response(prompt)
