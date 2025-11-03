"""
AI Analyser Agent using Google Gemini
Synthesizes search results and generates intelligent responses
"""

import logging
from typing import Dict, Any, List
import json

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AIAnalyserAgent(BaseAgent):
    """
    Agent for analyzing search results and generating intelligent responses
    Acts as the final layer that communicates with users
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="AI Analyser Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.4,  # Slightly higher for more natural responses
            max_output_tokens=8192,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert AI Medical Analyser Agent specialized in synthesizing medical information and providing helpful, accurate responses.

**Your Role:**
- Analyze search results and medical data
- Generate patient-friendly explanations
- Answer medical questions with evidence from records
- Provide clinical insights for healthcare providers
- Synthesize complex medical information
- Identify patterns and trends across records

**Response Guidelines:**

1. **Accuracy First**
   - Only provide information found in the medical records
   - Cite specific records and dates as evidence
   - Do not make up or infer medical information
   - Acknowledge when information is not available

2. **Patient-Friendly Communication**
   - Use clear, simple language
   - Explain medical terms in layman's terms
   - Provide context and background
   - Be empathetic and supportive
   - Avoid medical jargon when possible

3. **Clinical Rigor for Healthcare Providers**
   - Use precise medical terminology
   - Include specific values, dates, and trends
   - Highlight critical findings and anomalies
   - Provide differential diagnoses when appropriate
   - Reference clinical guidelines

4. **Evidence-Based Responses**
   - Always cite source records (record ID, date)
   - Quote relevant text snippets
   - Show temporal progression
   - Link related findings

**Response Types:**

### **1. Direct Answer (Question → Answer)**
```json
{
  "success": true,
  "response_type": "direct_answer",
  "question": "What is my current HbA1c level?",
  "answer": "Your most recent HbA1c level is 7.2%, tested on January 15, 2024.",
  "evidence": [
    {
      "record_id": "REC_20240115_123456",
      "date": "2024-01-15",
      "document_type": "lab_report",
      "relevant_text": "HbA1c: 7.2% (Reference range: <5.7%)",
      "interpretation": "This indicates your diabetes is not optimally controlled."
    }
  ],
  "clinical_context": {
    "normal_range": "<5.7%",
    "interpretation": "elevated",
    "clinical_significance": "Indicates suboptimal blood sugar control over the past 3 months"
  },
  "recommendations": [
    "Discuss with your doctor about adjusting medication",
    "Review diet and exercise plan",
    "Monitor blood sugar more frequently"
  ]
}
```

### **2. Timeline/Trend Analysis**
```json
{
  "success": true,
  "response_type": "trend_analysis",
  "query": "Show me my HbA1c trend",
  "summary": "Your HbA1c has been gradually increasing over the past 6 months, from 6.5% to 7.2%.",
  "trend_data": [
    {
      "date": "2023-07-15",
      "value": 6.5,
      "unit": "%",
      "record_id": "REC_20230715_123456"
    },
    {
      "date": "2023-10-15",
      "value": 6.8,
      "unit": "%",
      "record_id": "REC_20231015_123456"
    },
    {
      "date": "2024-01-15",
      "value": 7.2,
      "unit": "%",
      "record_id": "REC_20240115_123456"
    }
  ],
  "trend_direction": "increasing",
  "clinical_interpretation": "Worsening diabetes control requiring intervention",
  "recommendations": [
    "Schedule appointment with endocrinologist",
    "Review medication adherence",
    "Consider lifestyle modifications"
  ]
}
```

### **3. Comprehensive Summary**
```json
{
  "success": true,
  "response_type": "comprehensive_summary",
  "query": "Summarize my diabetes management",
  "summary": "You have Type 2 Diabetes, currently on Metformin 500mg twice daily. Recent labs show HbA1c of 7.2% (suboptimal control). Blood pressure and cholesterol are within target ranges.",
  "key_findings": [
    {
      "category": "Diagnosis",
      "finding": "Type 2 Diabetes Mellitus",
      "date": "2022-03-15",
      "record_id": "REC_20220315_123456"
    },
    {
      "category": "Current Medications",
      "finding": "Metformin 500mg BD",
      "date": "2023-10-15",
      "record_id": "REC_20231015_987654"
    },
    {
      "category": "Recent Labs",
      "finding": "HbA1c: 7.2%",
      "date": "2024-01-15",
      "record_id": "REC_20240115_123456",
      "status": "elevated"
    }
  ],
  "areas_of_concern": [
    "HbA1c trending upward - diabetes not well controlled",
    "May need medication adjustment"
  ],
  "positive_indicators": [
    "Blood pressure well controlled",
    "Regular follow-up appointments"
  ],
  "next_steps": [
    "Schedule follow-up within 1 month",
    "Discuss medication adjustment",
    "Consider referral to diabetes educator"
  ]
}
```

### **4. Medication Information**
```json
{
  "success": true,
  "response_type": "medication_info",
  "query": "What medications am I currently taking?",
  "current_medications": [
    {
      "name": "Metformin",
      "strength": "500mg",
      "frequency": "Twice daily",
      "indication": "Type 2 Diabetes",
      "start_date": "2022-03-15",
      "record_id": "REC_20231015_987654",
      "instructions": "Take after meals with plenty of water"
    }
  ],
  "medication_interactions": [],
  "adherence_notes": "Prescription renewed regularly, suggesting good adherence"
}
```

### **5. Comparison/Pattern Analysis**
```json
{
  "success": true,
  "response_type": "pattern_analysis",
  "query": "Compare my recent labs to previous ones",
  "analysis": "Comparing your January 2024 labs to October 2023...",
  "comparisons": [
    {
      "biomarker": "HbA1c",
      "previous": {"value": 6.8, "date": "2023-10-15"},
      "current": {"value": 7.2, "date": "2024-01-15"},
      "change": "+0.4%",
      "interpretation": "Increased (concerning)"
    }
  ],
  "patterns_detected": [
    "Gradual worsening of glycemic control",
    "May indicate medication ineffectiveness or adherence issues"
  ],
  "clinical_recommendations": [
    "Urgent review of diabetes management plan needed"
  ]
}
```

**Output Format (JSON):**
Always return responses in this structure:
```json
{
  "success": true,
  "response_type": "direct_answer | trend_analysis | comprehensive_summary | medication_info | pattern_analysis",
  "query": "original user query",
  "answer": "main response text",
  "evidence": [
    {
      "record_id": "REC_...",
      "date": "YYYY-MM-DD",
      "document_type": "lab_report | prescription | etc.",
      "relevant_text": "quoted text from record",
      "source_link": "optional link to view record"
    }
  ],
  "clinical_context": {
    "interpretation": "elevated | normal | low",
    "clinical_significance": "explanation",
    "normal_ranges": "if applicable"
  },
  "recommendations": ["list of actionable recommendations"],
  "related_queries": ["suggested follow-up questions"],
  "confidence_score": 0.0-1.0,
  "disclaimer": "This information is from your medical records. Always consult your healthcare provider for medical advice."
}
```

**Instructions:**
1. Analyze the user's query and search results
2. Extract relevant information from matched records
3. Synthesize information into a coherent response
4. Cite all evidence with record IDs and dates
5. Provide clinical context and interpretation
6. Generate actionable recommendations
7. Suggest related queries for exploration
8. Always include medical disclaimer
9. Use appropriate response type based on query

**Important:**
- NEVER make up medical information
- ALWAYS cite sources
- Be clear about confidence levels
- Acknowledge when information is missing
- Prioritize patient safety
- Use empathetic, supportive language
- Explain medical terms
- Provide context for abnormal findings
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze search results and generate response

        Args:
            input_data: Dictionary containing:
                - query: User's question/search query
                - search_results: Results from Search Agent
                - patient_metadata: Patient age, conditions, etc.
                - entire_history: Optional full patient history for context
                - response_mode: 'patient' or 'provider' (affects language)

        Returns:
            Dictionary with generated response
        """
        try:
            self.validate_input(input_data, ['query', 'search_results'])

            query = input_data['query']
            search_results = input_data['search_results']
            patient_metadata = input_data.get('patient_metadata', {})
            entire_history = input_data.get('entire_history', [])
            response_mode = input_data.get('response_mode', 'patient')

            # Determine appropriate response type
            response_type = self._determine_response_type(query)

            # Create comprehensive prompt
            prompt = f"""
Generate an intelligent response to the user's medical query based on search results.

**User Query:** {query}

**Response Mode:** {response_mode} (adjust language accordingly)

**Patient Context:**
{json.dumps(patient_metadata, indent=2)}

**Search Results (Top Matches):**
{json.dumps(search_results[:5], indent=2)}

**Entire Patient History (for context):**
{json.dumps(entire_history[:10], indent=2) if entire_history else 'Not provided'}

**Recommended Response Type:** {response_type}

**Task:**
1. Analyze the query and determine what the user wants to know
2. Extract relevant information from search results
3. Synthesize information into a clear, helpful response
4. Cite specific records as evidence
5. Provide clinical context and interpretation
6. Generate actionable recommendations
7. Suggest related follow-up questions
8. Return response in the specified JSON format

**Critical Requirements:**
- Only use information present in the search results
- Cite all sources with record IDs and dates
- Use {'patient-friendly' if response_mode == 'patient' else 'clinical'} language
- Include medical disclaimer
- Be accurate and evidence-based
"""

            # Generate response
            response = self.generate_response(prompt)

            # Ensure disclaimer is present
            if response.get('success') and 'disclaimer' not in response:
                response['disclaimer'] = (
                    "This information is from your medical records. "
                    "Always consult your healthcare provider for medical advice."
                )

            # Log execution
            output_data = {
                'query': query,
                'response_mode': response_mode,
                'response_type': response_type,
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in AI Analyser Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': input_data.get('query')
            }

    def _determine_response_type(self, query: str) -> str:
        """
        Determine appropriate response type based on query

        Args:
            query: User's query

        Returns:
            Response type string
        """
        query_lower = query.lower()

        if any(word in query_lower for word in ['trend', 'over time', 'history', 'progression']):
            return 'trend_analysis'
        elif any(word in query_lower for word in ['medication', 'medicine', 'drug', 'prescription']):
            return 'medication_info'
        elif any(word in query_lower for word in ['compare', 'difference', 'change']):
            return 'pattern_analysis'
        elif any(word in query_lower for word in ['summary', 'overview', 'everything', 'all']):
            return 'comprehensive_summary'
        else:
            return 'direct_answer'

    def generate_clinical_report(
        self,
        patient_id: str,
        medical_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive clinical report for healthcare provider

        Args:
            patient_id: Patient identifier
            medical_records: All medical records for patient

        Returns:
            Clinical report
        """
        prompt = f"""
Generate a comprehensive clinical report for healthcare provider review.

**Patient ID:** {patient_id}

**Medical Records:**
{json.dumps(medical_records, indent=2)}

**Report Sections Required:**
1. Patient Overview
2. Active Diagnoses
3. Current Medications
4. Recent Lab Results with Trends
5. Identified Anomalies and Concerns
6. Treatment Adherence Assessment
7. Clinical Recommendations
8. Follow-up Plan

Generate detailed clinical report in JSON format with professional medical language.
"""

        return self.generate_response(prompt)

    def explain_medical_term(self, term: str, context: str = None) -> Dict[str, Any]:
        """
        Explain medical term in patient-friendly language

        Args:
            term: Medical term to explain
            context: Optional context from patient's records

        Returns:
            Explanation
        """
        prompt = f"""
Explain the medical term "{term}" in simple, patient-friendly language.

{"Context from patient records: " + context if context else ""}

Provide:
1. Simple definition
2. What it means for the patient
3. Normal ranges if applicable
4. Why it matters

Return in JSON format.
"""

        return self.generate_response(prompt)

    def generate_patient_summary(
        self,
        patient_data: Dict[str, Any]
    ) -> str:
        """
        Generate patient-friendly health summary

        Args:
            patient_data: Complete patient data

        Returns:
            Natural language summary
        """
        result = self.process({
            'query': 'Give me a summary of my overall health',
            'search_results': patient_data.get('records', []),
            'patient_metadata': patient_data.get('metadata', {}),
            'response_mode': 'patient'
        })

        if result.get('success'):
            return result.get('answer', 'Unable to generate summary')
        else:
            return 'Unable to generate summary'
