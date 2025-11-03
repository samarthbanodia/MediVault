"""
Embedding Agent using Google Gemini
Creates vector embeddings for semantic search
"""

import logging
from typing import Dict, Any, List
import numpy as np

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EmbeddingAgent(BaseAgent):
    """
    Agent for creating vector embeddings for semantic search
    Uses Google's embedding models for medical text
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Embedding Agent",
            model="text-embedding-004",  # Google's embedding model
            temperature=0.0,
            **kwargs
        )

        # Import Google's embedding function
        import google.generativeai as genai
        self.embedding_model = "models/text-embedding-004"

    def get_system_prompt(self) -> str:
        """Embedding agent doesn't use traditional prompts"""
        return ""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create embeddings for medical text

        Args:
            input_data: Dictionary containing:
                - text: Text to embed (required)
                - record_id: Optional record identifier
                - patient_id: Optional patient identifier
                - metadata: Optional metadata dictionary

        Returns:
            Dictionary with embedding vector and metadata
        """
        try:
            self.validate_input(input_data, ['text'])

            text = input_data['text']
            record_id = input_data.get('record_id')
            patient_id = input_data.get('patient_id')
            metadata = input_data.get('metadata', {})

            # Generate embedding
            embedding = self._create_embedding(text)

            output_data = {
                'success': True,
                'embedding': embedding,
                'dimension': len(embedding),
                'text_length': len(text),
                'record_id': record_id,
                'patient_id': patient_id,
                'metadata': metadata
            }

            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in Embedding Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'record_id': input_data.get('record_id'),
                'patient_id': input_data.get('patient_id')
            }

    def _create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        try:
            import google.generativeai as genai

            # Generate embedding using Google's API
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )

            return result['embedding']

        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise

    def create_query_embedding(self, query: str) -> List[float]:
        """
        Create embedding for search query

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        try:
            import google.generativeai as genai

            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )

            return result['embedding']

        except Exception as e:
            logger.error(f"Error creating query embedding: {e}")
            raise

    def batch_process(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create embeddings for multiple texts

        Args:
            texts: List of dictionaries with 'text' and optional metadata

        Returns:
            List of embedding results
        """
        results = []

        for item in texts:
            result = self.process(item)
            results.append(result)

        return results

    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            similarity = dot_product / (norm1 * norm2)

            # Normalize to 0-1 range
            return float((similarity + 1) / 2)

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_similar_texts(
        self,
        query_text: str,
        candidate_texts: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar texts to query

        Args:
            query_text: Query text
            candidate_texts: List of dicts with 'text' and optional metadata
            top_k: Number of top results to return

        Returns:
            List of most similar texts with scores
        """
        try:
            # Create query embedding
            query_embedding = self.create_query_embedding(query_text)

            # Create embeddings for all candidates
            similarities = []

            for candidate in candidate_texts:
                if 'embedding' in candidate:
                    # Use pre-computed embedding
                    candidate_embedding = candidate['embedding']
                else:
                    # Create new embedding
                    result = self.process({'text': candidate['text']})
                    if result.get('success'):
                        candidate_embedding = result['embedding']
                    else:
                        continue

                # Calculate similarity
                similarity = self.calculate_similarity(query_embedding, candidate_embedding)

                similarities.append({
                    **candidate,
                    'similarity_score': similarity
                })

            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

            # Return top K
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Error finding similar texts: {e}")
            return []

    def store_in_vector_db(
        self,
        embedding_result: Dict[str, Any],
        vector_db
    ) -> bool:
        """
        Store embedding in vector database (ChromaDB)

        Args:
            embedding_result: Result from process() method
            vector_db: ChromaDB collection object

        Returns:
            True if successful
        """
        try:
            if not embedding_result.get('success'):
                return False

            # Prepare data for ChromaDB
            record_id = embedding_result.get('record_id') or embedding_result.get('patient_id')
            if not record_id:
                logger.error("No record_id or patient_id provided")
                return False

            vector_db.add(
                ids=[record_id],
                embeddings=[embedding_result['embedding']],
                metadatas=[embedding_result.get('metadata', {})],
                documents=[embedding_result.get('metadata', {}).get('text', '')]
            )

            logger.info(f"Stored embedding for record {record_id} in vector DB")
            return True

        except Exception as e:
            logger.error(f"Error storing in vector DB: {e}")
            return False
