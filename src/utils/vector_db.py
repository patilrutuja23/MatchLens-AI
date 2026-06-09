"""
FAISS Vector Database Manager
Handles embedding storage and retrieval for match context
"""

import os
import pickle
from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from src.utils.config import load_config, ensure_directories

class VectorDatabase:
    """FAISS-based vector database for match context retrieval"""
    
    def __init__(self):
        """Initialize vector database"""
        self.config = load_config()
        ensure_directories()
        
        # Initialize embedding model with fallback
        try:
            self.embedding_model = SentenceTransformer(
                self.config.embedding_model,
                device="cpu"
            )
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        except Exception as e:
            print(f"Embedding model initialization failed: {e}")
            print("Running in fallback mode without SentenceTransformer")
            self.embedding_model = None
            self.embedding_dim = 384
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.metadata = []
        
        # Load existing index if available
        self._load_index()
    
    def _get_index_path(self) -> str:
        """Get path to FAISS index file"""
        return os.path.join(self.config.vector_db_path, "faiss_index.bin")
    
    def _get_metadata_path(self) -> str:
        """Get path to metadata file"""
        return os.path.join(self.config.vector_db_path, "metadata.pkl")
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        index_path = self._get_index_path()
        metadata_path = self._get_metadata_path()
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
                print(f"Loaded {len(self.documents)} documents from vector database")
            except Exception as e:
                print(f"Error loading index: {e}")
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            faiss.write_index(self.index, self._get_index_path())
            with open(self._get_metadata_path(), 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata
                }, f)
            print(f"Saved {len(self.documents)} documents to vector database")
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None
    ):
        """
        Add documents to the vector database
        
        Args:
            documents: List of text documents to add
            metadata: Optional metadata for each document
        """
        if not documents:
            return
        
        # Check if embedding model is available
        if self.embedding_model is None:
            return
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents)
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to FAISS index
        # type: ignore - FAISS add method has incomplete type stubs
        self.index.add(embeddings)  # type: ignore[call-arg]
        
        # Store documents and metadata
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(documents))
        
        # Save index
        self._save_index()
    
    def search(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[str, Dict, float]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, metadata, distance) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        # Check if embedding model is available
        if self.embedding_model is None:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search
        # type: ignore - FAISS search returns (distances, indices) tuple
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))  # type: ignore[call-arg]
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(dist)
                ))
        
        return results
    
    def clear(self):
        """Clear all documents from the database"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.metadata = []
        self._save_index()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": self.embedding_dim,
            "index_size": self.index.ntotal
        }

# Made with Bob
