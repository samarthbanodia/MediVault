"""
Patient-Focused Response Generator using OpenAI GPT
Generates patient-friendly summaries and answers for the unified medical history app
"""

from typing import Dict, List, Optional, Any
from openai import OpenAI
from config import Config
import logging
import json

logger = logging.getLogger(__name__)


class PatientResponseGenerator:
    """Generate patient-friendly medical summaries and answers using OpenAI GPT"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the patient response generator

        Args:
            api_key: OpenAI API key (defaults to Config.OPENAI_API_KEY)
            model: Model to use (defaults to Config.OPENAI_MODEL)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY in .env file or pass to constructor"
            )

        self.client = OpenAI(api_key=self.api_key)
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE

        logger.info(f"Initialized PatientResponseGenerator with model: {self.model}")

    def generate_document_summary(self, medical_record: Dict) -> Dict[str, Any]:
        """
        Generate a patient-friendly summary of a medical document

        Args:
            medical_record: Dict containing medical data from document

        Returns:
            Dict with 'success', 'summary', 'tokens_used', and optional 'error'
        """
        try:
            # Extract key information
            anomalies = medical_record.get('anomaly_detection', {})
            biomarkers = medical_record.get('biomarkers', [])
            medications = medical_record.get('medications', [])
            diseases = medical_record.get('diseases', [])
            symptoms = medical_record.get('symptoms', [])
            timestamp = medical_record.get('date', 'Unknown date')

            # Build patient-friendly context
            context_parts = []

            if diseases:
                context_parts.append("Conditions mentioned:")
                for disease in diseases:
                    context_parts.append(f"  - {disease.get('text')}")

            if biomarkers:
                context_parts.append("\nTest Results:")
                for bio in biomarkers:
                    value_str = f"{bio.get('value')} {bio.get('unit', '')}"
                    context_parts.append(f"  - {bio.get('type')}: {value_str}")

            if medications:
                context_parts.append("\nMedications:")
                for med in medications:
                    dosage = med.get('dosage', '')
                    frequency = med.get('frequency', '')
                    context_parts.append(f"  - {med.get('medication')}: {dosage} {frequency}")

            if symptoms:
                context_parts.append("\nSymptoms:")
                for symptom in symptoms:
                    context_parts.append(f"  - {symptom.get('text')}")

            if anomalies:
                severity = anomalies.get('overall_severity', 0)
                detected = anomalies.get('anomalies', [])
                if detected:
                    context_parts.append(f"\nImportant Findings (Severity: {severity}/100):")
                    for anomaly in detected[:5]:
                        context_parts.append(f"  - {anomaly.get('message')}")

            context = "\n".join(context_parts)

            # Create patient-friendly prompt
            prompt = f"""You are a helpful medical assistant explaining test results and medical documents to patients.

Generate a patient-friendly summary of this medical record in simple, easy-to-understand language.

Document Date: {timestamp}

{context}

Create a summary that:
1. Explains what was found in plain English (avoid medical jargon)
2. Highlights good news first (what's normal/healthy)
3. Points out what needs attention (if anything)
4. Compares to previous visits if improvements/changes are mentioned
5. Uses a friendly, reassuring tone

Format as:
✓ Good News: [positive findings]
⚠️ Needs Attention: [things to watch or discuss with doctor]
📊 Summary: [overall takeaway]

Keep it concise and patient-friendly!"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a caring health assistant who explains medical information to patients in simple, friendly language. Avoid medical jargon. Be reassuring but honest."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            summary_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"Generated patient-friendly document summary, tokens used: {tokens_used}")

            return {
                'success': True,
                'summary': summary_text,
                'tokens_used': tokens_used,
                'model': self.model,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }

        except Exception as e:
            logger.error(f"Error generating document summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }

    def answer_patient_question(
        self,
        question: str,
        medical_history: List[Dict],
        additional_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Answer a patient's question about their medical history

        Args:
            question: The patient's question in natural language
            medical_history: List of relevant medical records
            additional_context: Optional additional context

        Returns:
            Dict with 'success', 'answer', 'tokens_used', and optional 'error'
        """
        try:
            # Build context from medical history
            history_text = self._build_history_context(medical_history)

            # Add additional context if provided
            if additional_context:
                history_text += f"\n\nAdditional Information:\n{json.dumps(additional_context, indent=2)}"

            # Create patient-friendly prompt
            prompt = f"""You are a helpful medical assistant answering a patient's question about their health records.

Patient's Question: "{question}"

Their Medical History:
{history_text}

Provide a clear, helpful answer that:
1. Directly answers the patient's question in simple language
2. References specific dates, visits, or test results as evidence
3. Explains medical terms in plain English
4. Is reassuring and supportive
5. Suggests talking to their doctor if needed

Be conversational, like talking to a friend. Avoid medical jargon."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a caring health assistant helping patients understand their medical records. Use simple language, be supportive, and cite specific records when answering."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"Answered patient question '{question}', tokens used: {tokens_used}")

            return {
                'success': True,
                'answer': answer_text,
                'question': question,
                'tokens_used': tokens_used,
                'model': self.model,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }

        except Exception as e:
            logger.error(f"Error answering patient question: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'answer': None
            }

    def generate_health_timeline(self, medical_records: List[Dict]) -> Dict[str, Any]:
        """
        Generate a visual health timeline from medical records

        Args:
            medical_records: List of medical records sorted by date

        Returns:
            Dict with 'success', 'timeline', 'tokens_used'
        """
        try:
            # Build timeline context
            timeline_data = []
            for record in sorted(medical_records, key=lambda x: x.get('date', '')):
                date = record.get('date', 'Unknown')
                diseases = record.get('diseases', [])
                medications = record.get('medications', [])
                biomarkers = record.get('biomarkers', [])

                event = f"Date: {date}\n"
                if diseases:
                    event += f"  Conditions: {', '.join([d.get('text') for d in diseases[:3]])}\n"
                if medications:
                    event += f"  Medications: {', '.join([m.get('medication') for m in medications[:3]])}\n"
                if biomarkers:
                    tests_list = [f"{b.get('type')}: {b.get('value')}" for b in biomarkers[:3]]
                    event += f"  Tests: {', '.join(tests_list)}\n"

                timeline_data.append(event)

            context = "\n".join(timeline_data)

            # Create timeline prompt
            prompt = f"""You are helping a patient understand their health journey over time.

Create a simple, easy-to-read timeline of their medical history:

{context}

Generate a timeline that:
1. Shows key health events chronologically
2. Highlights important changes (new medications, diagnoses, test improvements)
3. Groups related events together
4. Uses simple language and emojis for clarity
5. Notes any positive trends (improvements)

Format as a clear timeline that tells the story of their health journey."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a caring health assistant creating an easy-to-understand health timeline for a patient. Make it visual and encouraging."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            timeline_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"Generated health timeline, tokens used: {tokens_used}")

            return {
                'success': True,
                'timeline': timeline_text,
                'tokens_used': tokens_used,
                'model': self.model
            }

        except Exception as e:
            logger.error(f"Error generating health timeline: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timeline': None
            }

    def _build_history_context(self, medical_history: List[Dict]) -> str:
        """Build formatted medical history context for prompts"""

        if not medical_history:
            return "No medical history available."

        context_parts = []

        for idx, record in enumerate(medical_history[:5], 1):  # Limit to 5 most relevant
            metadata = record.get('metadata', {})
            document = record.get('document', '')

            context_parts.append(f"Record {idx}:")
            context_parts.append(f"  Date: {metadata.get('date', 'Unknown')}")

            if metadata.get('has_anomalies'):
                severity = metadata.get('severity', 0)
                context_parts.append(f"  Important findings (severity: {severity}/100)")

            # Add document content (truncated)
            if document:
                content = document[:400] + "..." if len(document) > 400 else document
                context_parts.append(f"  Details: {content}")

            context_parts.append("")

        return "\n".join(context_parts)

    def enhance_user_note(self, note_text: str, visit_date: str) -> Dict[str, Any]:
        """
        Enhance a user's handwritten note from a doctor visit

        Args:
            note_text: The note the user wrote (e.g., "Dr said BP is good")
            visit_date: Date of the visit

        Returns:
            Dict with 'success', 'enhanced_note', 'tokens_used'
        """
        try:
            prompt = f"""A patient wrote this note after a doctor visit on {visit_date}:

"{note_text}"

Help enhance this note by:
1. Expanding abbreviations (BP = Blood Pressure, etc.)
2. Adding context where obvious
3. Keeping the patient's original meaning
4. Making it more searchable later

Return a brief, enhanced version that preserves what the patient meant."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You help patients organize their doctor visit notes. Enhance notes while keeping them brief and preserving the original meaning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent note enhancement
                max_tokens=200  # Keep notes concise
            )

            enhanced_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"Enhanced user note, tokens used: {tokens_used}")

            return {
                'success': True,
                'enhanced_note': enhanced_text,
                'original_note': note_text,
                'tokens_used': tokens_used,
                'model': self.model
            }

        except Exception as e:
            logger.error(f"Error enhancing user note: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'enhanced_note': note_text  # Fallback to original
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current configuration and usage information"""
        return {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'api_configured': bool(self.api_key),
            'mode': 'patient-friendly'
        }
