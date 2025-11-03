import spacy
from pipelines.components.embeddings import MedicalEmbeddings
from pipelines.components.vector_store import MedicalVectorStore
from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta

class SmartSearchEngine:
    """Intelligent medical record search with multilingual support"""

    def __init__(self):
        self.embeddings = MedicalEmbeddings()
        self.vector_store = MedicalVectorStore()
        self.nlp = spacy.load('en_core_web_sm')

    def parse_query(self, query: str) -> Dict:
        """
        Parse search query to extract intent

        Returns:
            {
                'query_type': 'condition' | 'biomarker' | 'medication' | 'temporal',
                'entities': [...],
                'temporal': 'last_week' | 'last_month' | specific date,
                'biomarker': 'glucose' | 'bp' | etc.
            }
        """
        doc = self.nlp(query.lower())

        parsed = {
            'raw_query': query,
            'query_type': 'general',
            'entities': [],
            'temporal': None,
            'biomarker': None,
            'condition': None
        }

        # Extract named entities
        for ent in doc.ents:
            parsed['entities'].append({
                'text': ent.text,
                'label': ent.label_
            })

        # Detect biomarker queries
        biomarkers = ['glucose', 'sugar', 'bp', 'blood pressure', 'cholesterol',
                      'hba1c', 'hemoglobin', 'creatinine']
        for biomarker in biomarkers:
            if biomarker in query.lower():
                parsed['biomarker'] = biomarker
                parsed['query_type'] = 'biomarker'

        # Detect temporal queries
        temporal_patterns = {
            r'last\s+week': 'last_week',
            r'last\s+month': 'last_month',
            r'last\s+(\d+)\s+days': 'last_n_days',
            r'past\s+week': 'last_week',
            r'recent': 'last_month'
        }

        for pattern, temporal_type in temporal_patterns.items():
            match = re.search(pattern, query.lower())
            if match:
                parsed['temporal'] = temporal_type
                if temporal_type == 'last_n_days':
                    parsed['days'] = int(match.group(1))

        # Detect condition queries
        conditions = ['diabetes', 'hypertension', 'heart disease', 'kidney disease']
        for condition in conditions:
            if condition in query.lower():
                parsed['condition'] = condition
                parsed['query_type'] = 'condition'

        return parsed

    def build_filter(self, parsed_query: Dict, patient_id: Optional[str] = None) -> Dict:
        """Build metadata filter for vector search"""
        filter_dict = {}

        # Filter by patient
        if patient_id:
            filter_dict['patient_id'] = patient_id

        # Temporal filter
        if parsed_query['temporal']:
            now = datetime.now()

            if parsed_query['temporal'] == 'last_week':
                cutoff = now - timedelta(days=7)
            elif parsed_query['temporal'] == 'last_month':
                cutoff = now - timedelta(days=30)
            elif parsed_query['temporal'] == 'last_n_days':
                cutoff = now - timedelta(days=parsed_query.get('days', 7))
            else:
                cutoff = None

            if cutoff:
                filter_dict['date'] = {'$gte': cutoff.isoformat()}

        return filter_dict if filter_dict else None

    def search(self, query: str, patient_id: Optional[str] = None,
               n_results: int = 10) -> Dict:
        """
        Perform semantic search on medical records

        Args:
            query: Natural language search query
            patient_id: Optional patient ID to filter results
            n_results: Number of results to return

        Returns:
            Ranked search results with relevance scores
        """
        # Parse query
        parsed = self.parse_query(query)

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Build filter
        filter_dict = self.build_filter(parsed, patient_id)

        # Semantic search
        results = self.vector_store.search(
            query_embedding=query_embedding.tolist(),
            n_results=n_results,
            filter_dict=filter_dict
        )

        # Post-process and rank
        processed_results = []
        for i in range(len(results['ids'])):
            result = {
                'record_id': results['ids'][i],
                'relevance_score': 1 - results['distances'][i],  # Convert distance to similarity
                'metadata': results['metadatas'][i],
                'document': results['documents'][i],
                'matched_query_type': parsed['query_type']
            }
            processed_results.append(result)

        return {
            'query': query,
            'parsed_query': parsed,
            'results': processed_results,
            'total_results': len(processed_results)
        }

    def hybrid_search(self, query: str, patient_id: Optional[str] = None,
                     n_results: int = 10) -> Dict:
        """
        Combine semantic search with keyword filtering
        """
        # Get semantic results
        semantic_results = self.search(query, patient_id, n_results * 2)

        # Extract keywords from query
        doc = self.nlp(query.lower())
        keywords = [token.text for token in doc if not token.is_stop and token.is_alpha]

        # Re-rank based on keyword matches
        for result in semantic_results['results']:
            keyword_score = sum(1 for kw in keywords if kw in result['document'].lower())
            result['keyword_score'] = keyword_score
            result['final_score'] = result['relevance_score'] * 0.7 + (keyword_score / len(keywords)) * 0.3 if keywords else result['relevance_score']

        # Sort by final score
        semantic_results['results'].sort(key=lambda x: x['final_score'], reverse=True)
        semantic_results['results'] = semantic_results['results'][:n_results]

        return semantic_results
