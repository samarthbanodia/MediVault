"""
Medical Response Generator using OpenAI GPT
Converts structured medical data into natural language clinical reports
"""

from typing import Dict, List, Optional, Any
from openai import OpenAI
from config import Config
import logging
import json

logger = logging.getLogger(__name__)


class MedicalResponseGenerator:
    """Generate natural language medical reports using OpenAI GPT models"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the response generator

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

        logger.info(f"Initialized MedicalResponseGenerator with model: {self.model}")

    def generate_anomaly_report(self, medical_record: Dict) -> Dict[str, Any]:
        """
        Generate a clinical report from medical record with anomaly detection results

        Args:
            medical_record: Dict containing medical data including anomaly_detection

        Returns:
            Dict with 'success', 'report', 'tokens_used', and optional 'error'
        """
        try:
            # Extract key information
            anomalies = medical_record.get('anomaly_detection', {})
            biomarkers = medical_record.get('biomarkers', [])
            medications = medical_record.get('medications', [])
            diseases = medical_record.get('diseases', [])
            symptoms = medical_record.get('symptoms', [])
            domain_info = medical_record.get('domain_info', {})
            patient_id = medical_record.get('patient_id', 'Unknown')
            timestamp = medical_record.get('timestamp', 'Unknown date')

            # Build structured context
            context = self._build_clinical_context(
                patient_id, timestamp, domain_info, diseases, biomarkers,
                medications, symptoms, anomalies
            )

            # Create prompt
            prompt = f"""You are an expert clinical AI assistant. Generate a concise, professional clinical report based on the following medical data.

{context}

Generate a clinical summary that includes:
1. Patient overview and key diagnoses, considering the medical domain context.
2. Analysis of biomarker findings, NER-extracted entities, and their clinical significance.
3. A detailed breakdown of detected anomalies, their severity, and potential impact.
4. Actionable, evidence-based recommendations for the treating physician, tailored to the domain.
5. A clear priority level for follow-up actions (e.g., Urgent, High, Medium, Low).

Keep the report concise, medically accurate, and actionable. Use professional medical terminology."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert clinical decision support AI. Generate professional, accurate medical reports for healthcare providers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            report_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"Generated anomaly report for {patient_id}, tokens used: {tokens_used}")

            return {
                'success': True,
                'report': report_text,
                'tokens_used': tokens_used,
                'model': self.model,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }

        except Exception as e:
            logger.error(f"Error generating anomaly report: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'report': None
            }

    def generate_search_summary(self, search_results: List[Dict], query: str) -> Dict[str, Any]:
        """
        Generate an executive summary of search results

        Args:
            search_results: List of search result dicts
            query: Original search query

        Returns:
            Dict with 'success', 'summary', 'tokens_used', and optional 'error'
        """
        try:
            if not search_results:
                return {
                    'success': True,
                    'summary': 'No matching records found for the query.',
                    'tokens_used': 0
                }

            # Build search results context
            results_context = self._build_search_context(search_results, query)

            # Create prompt
            prompt = f"""You are an expert clinical data analyst. Synthesize the following search results into a cohesive executive summary.

Query: "{query}"

{results_context}

Generate a synthesis that:
1. Summarizes key patterns across all matching records
2. Highlights the most clinically significant findings
3. Identifies trends or commonalities
4. Prioritizes patients by severity/urgency
5. Provides actionable next steps

Keep the summary concise and focused on clinical decision-making."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical data analyst. Synthesize search results into actionable clinical insights."
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

            logger.info(f"Generated search summary for query '{query}', tokens used: {tokens_used}")

            return {
                'success': True,
                'summary': summary_text,
                'tokens_used': tokens_used,
                'model': self.model,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }

        except Exception as e:
            logger.error(f"Error generating search summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }

    def answer_clinical_query(
        self,
        query: str,
        search_results: List[Dict],
        additional_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Answer a specific clinical question using search results and context

        Args:
            query: The clinical question to answer
            search_results: Relevant medical records
            additional_context: Optional additional context (patient history, etc.)

        Returns:
            Dict with 'success', 'answer', 'tokens_used', and optional 'error'
        """
        try:
            # Build context from search results
            context = self._build_search_context(search_results, query)

            # Add additional context if provided
            if additional_context:
                context += f"\n\nAdditional Context:\n{json.dumps(additional_context, indent=2)}"

            # Create prompt
            prompt = f"""You are an expert clinical AI assistant. Answer the following clinical question using the provided medical records.

Question: "{query}"

{context}

Provide a comprehensive, evidence-based answer that:
1. Directly addresses the question
2. Cites specific findings from the medical records
3. Explains clinical significance
4. Provides recommendations if appropriate
5. Notes any limitations or missing data

Be precise, medically accurate, and reference specific data points."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert clinical AI assistant. Provide accurate, evidence-based answers to clinical questions using medical record data."
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

            logger.info(f"Answered clinical query '{query}', tokens used: {tokens_used}")

            return {
                'success': True,
                'answer': answer_text,
                'tokens_used': tokens_used,
                'model': self.model,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }

        except Exception as e:
            logger.error(f"Error answering clinical query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'answer': None
            }

    def _build_clinical_context(
        self,
        patient_id: str,
        timestamp: str,
        domain_info: Dict,
        diseases: List[Dict],
        biomarkers: List[Dict],
        medications: List[Dict],
        symptoms: List[Dict],
        anomalies: Dict
    ) -> str:
        """Build formatted clinical context for prompts"""

        context_parts = [
            f"Patient ID: {patient_id}",
            f"Date: {timestamp}",
            f"Medical Domain: {domain_info.get('primary_domain', 'Unknown')}",
            f"Document Type: {domain_info.get('document_type', 'Unknown')}",
            ""
        ]

        # Diseases/Diagnoses
        if diseases:
            context_parts.append("Diagnoses:")
            for disease in diseases:
                confidence = disease.get('confidence', 0) * 100
                context_parts.append(f"  - {disease.get('text')} (confidence: {confidence:.1f}%)")
            context_parts.append("")

        # Biomarkers
        if biomarkers:
            context_parts.append("Biomarker Findings:")
            for biomarker in biomarkers:
                value_str = f"{biomarker.get('value')} {biomarker.get('unit', '')}"
                context_parts.append(f"  - {biomarker.get('type')}: {value_str}")
            context_parts.append("")

        # Medications
        if medications:
            context_parts.append("Current Medications:")
            for med in medications:
                dosage = med.get('dosage', 'Unknown dosage')
                frequency = med.get('frequency', '')
                context_parts.append(f"  - {med.get('medication')}: {dosage} {frequency}")
            context_parts.append("")

        # Symptoms
        if symptoms:
            context_parts.append("Reported Symptoms:")
            for symptom in symptoms:
                confidence = symptom.get('confidence', 0) * 100
                context_parts.append(f"  - {symptom.get('text')} (confidence: {confidence:.1f}%)")
            context_parts.append("")

        # Anomaly Detection Results
        if anomalies:
            overall_severity = anomalies.get('overall_severity', 0)
            context_parts.append(f"Anomaly Detection Analysis:")
            context_parts.append(f"Overall Severity Score: {overall_severity}/100")
            context_parts.append("")

            detected_anomalies = anomalies.get('anomalies', [])
            if detected_anomalies:
                context_parts.append("Detected Anomalies:")
                for anomaly in detected_anomalies:
                    severity = anomaly.get('severity', 0)
                    anomaly_type = anomaly.get('type', 'Unknown')
                    message = anomaly.get('message', '')
                    context_parts.append(f"  - [{anomaly_type}] {message} (severity: {severity})")
                context_parts.append("")

            critical_alerts = anomalies.get('critical_alerts', [])
            if critical_alerts:
                context_parts.append("CRITICAL ALERTS:")
                for alert in critical_alerts:
                    context_parts.append(f"  - {alert}")
                context_parts.append("")

            recommendations = anomalies.get('recommendations', [])
            if recommendations:
                context_parts.append("System Recommendations:")
                for rec in recommendations:
                    context_parts.append(f"  - {rec}")
                context_parts.append("")

        return "\n".join(context_parts)

    def _build_search_context(self, search_results: List[Dict], query: str) -> str:
        """Build formatted search results context for prompts"""

        context_parts = [
            f"Total Results: {len(search_results)}",
            ""
        ]

        for idx, result in enumerate(search_results[:10], 1):  # Limit to top 10 results
            metadata = result.get('metadata', {})
            document = result.get('document', '')
            relevance = result.get('final_score', result.get('relevance_score', 0))

            context_parts.append(f"Result {idx} (Relevance: {relevance:.2f}):")
            context_parts.append(f"Patient: {metadata.get('patient_id', 'Unknown')}")
            context_parts.append(f"Date: {metadata.get('date', 'Unknown')}")

            if metadata.get('has_anomalies'):
                severity = metadata.get('severity', 0)
                context_parts.append(f"Severity: {severity}/100")

            context_parts.append(f"Content: {document[:500]}")  # Limit content length
            context_parts.append("")

        return "\n".join(context_parts)

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current configuration and usage information"""
        return {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'api_configured': bool(self.api_key)
        }
