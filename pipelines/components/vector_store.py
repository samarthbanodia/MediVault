import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import json

class MedicalVectorStore:
    """ChromaDB interface for medical records"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB"""
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="medical_records",
            metadata={"description": "Patient medical records with embeddings"}
        )

    def add_record(self, record_id: str, embedding: List[float], metadata: Dict, document: str):
        """Add a single medical record"""
        self.collection.add(
            ids=[record_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[document]
        )

    def add_records(self, record_ids: List[str], embeddings: List[List[float]],
                    metadatas: List[Dict], documents: List[str]):
        """Add multiple medical records (batched)"""
        self.collection.add(
            ids=record_ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def search(self, query_embedding: List[float], n_results: int = 10,
               filter_dict: Optional[Dict] = None) -> Dict:
        """
        Search for similar records

        Args:
            query_embedding: Query vector
            n_results: Number of results to return
            filter_dict: Metadata filters (e.g., {"patient_id": "P123"})
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict if filter_dict else None
        )

        return {
            'ids': results['ids'][0],
            'distances': results['distances'][0],
            'metadatas': results['metadatas'][0],
            'documents': results['documents'][0]
        }

    def get_record(self, record_id: str) -> Dict:
        """Retrieve a specific record by ID"""
        result = self.collection.get(ids=[record_id])

        if result['ids']:
            return {
                'id': result['ids'][0],
                'metadata': result['metadatas'][0],
                'document': result['documents'][0]
            }
        return None

    def delete_record(self, record_id: str):
        """Delete a record"""
        self.collection.delete(ids=[record_id])

    def count(self) -> int:
        """Get total number of records"""
        return self.collection.count()
