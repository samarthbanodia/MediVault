from pipelines.components.search_engine import SmartSearchEngine
from pipelines.components.response_generator import MedicalResponseGenerator
import logging
from typing import Optional, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchPipeline:
    """Complete search pipeline for medical records"""

    def __init__(self, enable_llm: bool = True):
        """
        Initialize the search pipeline

        Args:
            enable_llm: Enable OpenAI response generation (requires API key in .env)
        """
        logger.info("Initializing Search Pipeline...")
        self.search_engine = SmartSearchEngine()

        # Initialize response generator if enabled
        self.enable_llm = enable_llm
        self.response_generator = None

        if enable_llm:
            try:
                self.response_generator = MedicalResponseGenerator()
                logger.info("OpenAI response generation enabled")
            except Exception as e:
                logger.warning(f"Could not initialize response generator: {str(e)}")
                logger.warning("Continuing without LLM response generation")
                self.enable_llm = False

        logger.info("Search Pipeline initialized")

    def search(self, query: str, patient_id: Optional[str] = None,
               search_type: str = 'hybrid', n_results: int = 10,
               generate_summary: bool = False) -> Dict:
        """
        Execute search query

        Args:
            query: Natural language search query (EN/HI/multilingual)
            patient_id: Optional patient filter
            search_type: 'semantic' | 'hybrid' (default)
            n_results: Number of results
            generate_summary: Generate AI summary of search results

        Returns:
            Search results with context and optional AI summary
        """
        logger.info(f"Executing {search_type} search: '{query}'")

        if search_type == 'hybrid':
            results = self.search_engine.hybrid_search(query, patient_id, n_results)
        else:
            results = self.search_engine.search(query, patient_id, n_results)

        logger.info(f"Found {results['total_results']} results")

        # Generate AI summary if requested and LLM is enabled
        if generate_summary and self.enable_llm and self.response_generator:
            logger.info("Generating AI summary of search results...")
            try:
                summary_result = self.response_generator.generate_search_summary(
                    results['results'],
                    query
                )
                if summary_result.get('success'):
                    results['ai_summary'] = summary_result.get('summary', '')
                    results['llm_metadata'] = {
                        'tokens_used': summary_result.get('tokens_used', 0),
                        'model': summary_result.get('model', 'unknown'),
                        'prompt_tokens': summary_result.get('prompt_tokens', 0),
                        'completion_tokens': summary_result.get('completion_tokens', 0)
                    }
                    logger.info(f"AI summary generated (tokens: {summary_result.get('tokens_used', 0)})")
                else:
                    logger.error(f"Failed to generate summary: {summary_result.get('error')}")
            except Exception as e:
                logger.error(f"Error generating summary: {str(e)}")

        return results

    def search_with_context(self, query: str, patient_id: str,
                           generate_summary: bool = True) -> Dict:
        """
        Search with full patient context and AI summary

        Args:
            query: Search query
            patient_id: Patient ID to filter by
            generate_summary: Generate AI summary (default: True)

        Returns:
            Search results with context and AI summary
        """
        # Get search results with AI summary
        results = self.search(query, patient_id, generate_summary=generate_summary)

        # Add patient context (could fetch from patient DB)
        results['patient_context'] = {
            'patient_id': patient_id,
            'total_records': self.search_engine.vector_store.count()
        }

        return results

    def answer_question(self, question: str, patient_id: Optional[str] = None,
                       n_context_results: int = 5) -> Dict:
        """
        Answer a clinical question using medical records and AI

        Args:
            question: Clinical question to answer
            patient_id: Optional patient filter
            n_context_results: Number of relevant records to use as context

        Returns:
            Dict with 'question', 'answer', 'context_records', and metadata
        """
        if not self.enable_llm or not self.response_generator:
            return {
                'success': False,
                'error': 'LLM is not enabled. Set OPENAI_API_KEY in .env file.'
            }

        logger.info(f"Answering clinical question: '{question}'")

        # Search for relevant records
        search_results = self.search(question, patient_id, n_results=n_context_results)

        # Generate answer using AI
        try:
            answer_result = self.response_generator.answer_clinical_query(
                query=question,
                search_results=search_results['results']
            )

            if answer_result['success']:
                logger.info(f"Answer generated (tokens: {answer_result['tokens_used']})")
                return {
                    'success': True,
                    'question': question,
                    'answer': answer_result['answer'],
                    'context_records': search_results['results'],
                    'total_context_records': search_results['total_results'],
                    'llm_metadata': {
                        'tokens_used': answer_result['tokens_used'],
                        'model': answer_result['model'],
                        'prompt_tokens': answer_result['prompt_tokens'],
                        'completion_tokens': answer_result['completion_tokens']
                    }
                }
            else:
                logger.error(f"Failed to generate answer: {answer_result.get('error')}")
                return {
                    'success': False,
                    'error': answer_result.get('error')
                }

        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
