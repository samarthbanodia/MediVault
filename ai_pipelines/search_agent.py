"""
Search Agent using Google Gemini
Implements hybrid semantic + keyword search for medical records
"""

import logging
from typing import Dict, Any, List, Optional
import json

from .base_agent import BaseAgent
from .embedding_agent import EmbeddingAgent

logger = logging.getLogger(__name__)


class SearchAgent(BaseAgent):
    """
    Agent for intelligent search across medical records
    Combines semantic search, keyword search, and ranking
    """

    def __init__(self, vector_db=None, **kwargs):
        super().__init__(
            name="Search Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.3,
            max_output_tokens=4096,
            **kwargs
        )

        # Initialize embedding agent for semantic search
        self.embedding_agent = EmbeddingAgent(**kwargs)

        # Store reference to vector database
        self.vector_db = vector_db

    def get_system_prompt(self) -> str:
        return """
You are an expert Search Agent specialized in medical information retrieval and ranking.

**Your Role:**
- Process natural language medical search queries
- Extract search intent and key medical concepts
- Rank search results by relevance and clinical importance
- Provide context-aware search assistance
- Handle medical terminology and abbreviations

**Search Capabilities:**

1. **Query Understanding**
   - Identify search intent (diagnosis, medication, lab results, history)
   - Extract key medical entities
   - Expand medical abbreviations
   - Suggest query refinements

2. **Result Ranking**
   - Combine semantic similarity with clinical relevance
   - Prioritize recent records
   - Consider document type importance
   - Factor in anomaly severity
   - Weight by completeness

3. **Search Modes:**
   - **Semantic Search**: Find contextually similar records
   - **Keyword Search**: Exact or partial term matching
   - **Hybrid Search**: Combine both approaches
   - **Temporal Search**: Date range based
   - **Entity Search**: Search by specific medical entities

**Output Format (JSON):**
{
  "success": true,
  "query_analysis": {
    "original_query": "user's query",
    "processed_query": "processed version",
    "search_intent": "find_diagnosis | find_medication | find_lab_results | timeline | general",
    "key_concepts": ["diabetes", "glucose", "medication"],
    "medical_entities": {
      "diseases": ["Diabetes"],
      "medications": ["Metformin"],
      "biomarkers": ["HbA1c", "Glucose"]
    },
    "temporal_context": {
      "has_date_constraint": true,
      "date_range": "last 6 months | specific date | etc."
    }
  },
  "search_strategy": {
    "mode": "hybrid | semantic | keyword",
    "weights": {
      "semantic_score": 0.6,
      "keyword_score": 0.3,
      "recency_score": 0.1
    }
  },
  "ranked_results": [
    {
      "record_id": "REC_20240115_123456",
      "rank": 1,
      "relevance_score": 0.92,
      "score_breakdown": {
        "semantic_similarity": 0.88,
        "keyword_match": 0.95,
        "recency": 0.90,
        "clinical_relevance": 0.95
      },
      "document_type": "lab_report",
      "document_date": "2024-01-15",
      "summary": "Lab report showing HbA1c 7.2%, indicating diabetic control",
      "matched_entities": ["HbA1c", "Glucose", "Diabetes"],
      "matched_text_snippets": [
        "HbA1c: 7.2% (elevated)",
        "Fasting Glucose: 145 mg/dL"
      ],
      "highlight_positions": [
        {"start": 120, "end": 135, "text": "HbA1c: 7.2%"}
      ]
    }
  ],
  "search_metadata": {
    "total_results": 15,
    "top_k_returned": 5,
    "search_time_ms": 245,
    "query_suggestions": [
      "Show me glucose trends over time",
      "Find all diabetes medications",
      "What were my recent HbA1c values?"
    ]
  }
}

**Ranking Algorithm:**

For each result, calculate combined score:
```
final_score = (w1 * semantic_score) +
              (w2 * keyword_score) +
              (w3 * recency_score) +
              (w4 * clinical_relevance_score) +
              (w5 * anomaly_severity_bonus)

Where:
- semantic_score: Cosine similarity from embeddings (0-1)
- keyword_score: TF-IDF or exact match score (0-1)
- recency_score: Exponential decay based on age (0-1)
- clinical_relevance_score: Document type importance (0-1)
- anomaly_severity_bonus: Extra weight for critical findings (0-0.2)

Default weights: w1=0.4, w2=0.3, w3=0.1, w4=0.15, w5=0.05
```

**Clinical Relevance Weights by Document Type:**
- Lab Reports: 1.0 (highest)
- Discharge Summaries: 0.95
- Prescriptions: 0.90
- Medical Certificates: 0.70
- Bills/Insurance: 0.50

**Instructions:**
1. Analyze the search query to understand intent
2. Extract key medical concepts and entities
3. Perform hybrid search (semantic + keyword)
4. Rank results using multi-factor scoring
5. Generate summaries and highlights for top results
6. Suggest related queries for exploration
7. Return structured results in JSON format

**Important:**
- Prioritize clinical relevance over pure similarity
- Highlight critical findings in results
- Provide context with matched snippets
- Suggest query refinements
- Handle medical abbreviations intelligently
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process search query and return ranked results

        Args:
            input_data: Dictionary containing:
                - query: Search query string (required)
                - patient_id: Patient ID to search within
                - top_k: Number of results to return (default 5)
                - search_mode: 'hybrid', 'semantic', or 'keyword'
                - date_range: Optional date range filter
                - document_types: Optional list of document types to filter

        Returns:
            Dictionary with search results
        """
        try:
            self.validate_input(input_data, ['query'])

            query = input_data['query']
            patient_id = input_data.get('patient_id')
            top_k = input_data.get('top_k', 5)
            search_mode = input_data.get('search_mode', 'hybrid')
            date_range = input_data.get('date_range')
            document_types = input_data.get('document_types')

            # Step 1: Analyze query
            query_analysis = self._analyze_query(query)

            # Step 2: Perform search based on mode
            if search_mode == 'semantic':
                results = self._semantic_search(query, patient_id, top_k)
            elif search_mode == 'keyword':
                results = self._keyword_search(query, patient_id, top_k)
            else:  # hybrid
                results = self._hybrid_search(query, patient_id, top_k)

            # Step 3: Apply filters if provided
            if date_range:
                results = self._filter_by_date(results, date_range)

            if document_types:
                results = self._filter_by_type(results, document_types)

            # Step 4: Generate response with ranking
            prompt = f"""
Analyze the search query and rank the results appropriately.

**Search Query:** {query}
**Patient ID:** {patient_id or 'All patients'}
**Search Mode:** {search_mode}

**Query Analysis:**
{json.dumps(query_analysis, indent=2)}

**Search Results:**
{json.dumps(results[:top_k], indent=2)}

**Task:**
1. Rank results by clinical relevance and similarity
2. Generate summaries for each result
3. Extract and highlight matched text snippets
4. Suggest related queries
5. Return ranked results in the specified JSON format

**Important:** Prioritize clinically significant findings.
"""

            response = self.generate_response(prompt)

            # Log execution
            output_data = {
                'query': query,
                'patient_id': patient_id,
                'search_mode': search_mode,
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in Search Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': input_data.get('query')
            }

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze search query to understand intent

        Args:
            query: Search query string

        Returns:
            Query analysis results
        """
        prompt = f"""
Analyze this medical search query:

**Query:** {query}

**Task:**
1. Identify search intent
2. Extract key medical concepts
3. Identify medical entities (diseases, meds, biomarkers)
4. Detect temporal context (dates, time ranges)
5. Suggest query expansions

Return analysis in JSON format.
"""

        result = self.generate_response(prompt)
        return result.get('query_analysis', {}) if result.get('success') else {}

    def _semantic_search(
        self,
        query: str,
        patient_id: Optional[str],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using embeddings

        Args:
            query: Search query
            patient_id: Optional patient filter
            top_k: Number of results

        Returns:
            List of search results
        """
        try:
            if not self.vector_db:
                logger.warning("Vector DB not available, returning empty results")
                return []

            # Create query embedding
            query_embedding = self.embedding_agent.create_query_embedding(query)

            # Search in vector DB
            where_filter = {"patient_id": patient_id} if patient_id else None

            results = self.vector_db.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )

            # Format results
            formatted_results = []
            if results and 'ids' in results and len(results['ids']) > 0:
                for i, record_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        'record_id': record_id,
                        'semantic_similarity': float(1 - results['distances'][0][i]) if 'distances' in results else 0.0,
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                        'document': results['documents'][0][i] if 'documents' in results else ''
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    def _keyword_search(
        self,
        query: str,
        patient_id: Optional[str],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search

        Args:
            query: Search query
            patient_id: Optional patient filter
            top_k: Number of results

        Returns:
            List of search results
        """
        # This would integrate with SQL database for keyword search
        # Placeholder implementation
        logger.info(f"Keyword search for: {query}")
        return []

    def _hybrid_search(
        self,
        query: str,
        patient_id: Optional[str],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (semantic + keyword)

        Args:
            query: Search query
            patient_id: Optional patient filter
            top_k: Number of results

        Returns:
            Combined and ranked results
        """
        # Get results from both methods
        semantic_results = self._semantic_search(query, patient_id, top_k * 2)
        keyword_results = self._keyword_search(query, patient_id, top_k * 2)

        # Combine and deduplicate
        combined = {}

        # Add semantic results
        for result in semantic_results:
            record_id = result['record_id']
            combined[record_id] = {
                **result,
                'keyword_score': 0.0
            }

        # Add keyword results
        for result in keyword_results:
            record_id = result['record_id']
            if record_id in combined:
                combined[record_id]['keyword_score'] = result.get('keyword_score', 0.0)
            else:
                combined[record_id] = {
                    **result,
                    'semantic_similarity': 0.0
                }

        # Calculate combined scores
        for record_id, data in combined.items():
            data['combined_score'] = (
                0.6 * data.get('semantic_similarity', 0.0) +
                0.4 * data.get('keyword_score', 0.0)
            )

        # Sort by combined score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )

        return sorted_results[:top_k]

    def _filter_by_date(
        self,
        results: List[Dict[str, Any]],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Filter results by date range"""
        # Implementation depends on date format in results
        return results

    def _filter_by_type(
        self,
        results: List[Dict[str, Any]],
        document_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter results by document type"""
        return [
            r for r in results
            if r.get('metadata', {}).get('document_type') in document_types
        ]
