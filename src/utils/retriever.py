"""
FAISS-based Document Retriever
Retrieves relevant document chunks for RAG
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class DocumentRetriever:
    """Retrieves relevant document chunks using FAISS similarity search"""
    
    def __init__(
        self,
        vector_db_path: str = "./data/vector_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize document retriever
        
        Args:
            vector_db_path: Path to FAISS indices
            embedding_model: Sentence transformer model name
        """
        self.vector_db_path = Path(vector_db_path)
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Storage for loaded indices
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata: Dict[str, List[Dict]] = {}
        
        print(f"✅ Document retriever initialized")
    
    def load_index(self, index_name: str) -> bool:
        """
        Load a FAISS index and its metadata
        
        Args:
            index_name: Name of the index to load
            
        Returns:
            True if successful
        """
        index_path = self.vector_db_path / f"{index_name}.index"
        metadata_path = self.vector_db_path / f"{index_name}_metadata.json"
        
        if not index_path.exists():
            print(f"⚠️  Index not found: {index_path}")
            return False
        
        if not metadata_path.exists():
            print(f"⚠️  Metadata not found: {metadata_path}")
            return False
        
        try:
            # Load FAISS index
            index = faiss.read_index(str(index_path))
            self.indices[index_name] = index
            
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            self.metadata[index_name] = metadata
            
            print(f"✅ Loaded index '{index_name}' with {index.ntotal} vectors")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load index '{index_name}': {e}")
            return False
    
    def load_all_indices(self):
        """Load all available indices in the vector_db folder"""
        if not self.vector_db_path.exists():
            print(f"⚠️  Vector DB path not found: {self.vector_db_path}")
            return
        
        index_files = list(self.vector_db_path.glob("*.index"))
        
        if not index_files:
            print(f"⚠️  No indices found in {self.vector_db_path}")
            return
        
        print(f"\n📚 Loading {len(index_files)} indices...")
        
        for index_file in index_files:
            index_name = index_file.stem
            self.load_index(index_name)
        
        print(f"✅ Loaded {len(self.indices)} indices\n")
    
    def retrieve(
        self,
        query: str,
        index_name: Optional[str] = None,
        top_k: int = 3,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Retrieve relevant document chunks
        
        Args:
            query: Search query
            index_name: Specific index to search (None = search all)
            top_k: Number of results to return
            score_threshold: Minimum similarity score (lower is better for L2)
            
        Returns:
            List of retrieved chunks with scores
        """
        if not self.indices:
            print(f"⚠️  No indices loaded. Call load_index() or load_all_indices() first.")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = np.array([query_embedding], dtype='float32')
        
        results = []
        
        # Search specific index or all indices
        indices_to_search = {index_name: self.indices[index_name]} if index_name else self.indices
        
        for idx_name, index in indices_to_search.items():
            if idx_name not in self.metadata:
                continue
            
            # Search FAISS index
            # type: ignore - FAISS search method has incomplete type stubs
            distances, indices = index.search(query_embedding, top_k)  # type: ignore[call-arg]
            
            # Collect results
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                
                # Apply score threshold if specified
                if score_threshold is not None and distance > score_threshold:
                    continue
                
                chunk = self.metadata[idx_name][idx].copy()
                chunk['score'] = float(distance)
                chunk['index_name'] = idx_name
                chunk['rank'] = i + 1
                results.append(chunk)
        
        # Sort by score (lower is better for L2 distance)
        results.sort(key=lambda x: x['score'])
        
        # Return top_k results
        return results[:top_k]
    
    def retrieve_fifa_rules(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve FIFA rules relevant to query
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant FIFA rule chunks
        """
        # Search all FIFA rules indices
        fifa_indices = [name for name in self.indices.keys() if 'fifa_rules' in name]
        
        if not fifa_indices:
            print(f"⚠️  No FIFA rules indices found")
            return []
        
        all_results = []
        for index_name in fifa_indices:
            results = self.retrieve(query, index_name=index_name, top_k=top_k)
            all_results.extend(results)
        
        # Sort and return top_k
        all_results.sort(key=lambda x: x['score'])
        return all_results[:top_k]
    
    def retrieve_var_guidelines(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve VAR guidelines relevant to query
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant VAR guideline chunks
        """
        # Search all VAR guidelines indices
        var_indices = [name for name in self.indices.keys() if 'var_guidelines' in name]
        
        if not var_indices:
            print(f"⚠️  No VAR guidelines indices found")
            return []
        
        all_results = []
        for index_name in var_indices:
            results = self.retrieve(query, index_name=index_name, top_k=top_k)
            all_results.extend(results)
        
        # Sort and return top_k
        all_results.sort(key=lambda x: x['score'])
        return all_results[:top_k]
    
    def format_retrieved_context(self, results: List[Dict]) -> str:
        """
        Format retrieved chunks into context string
        
        Args:
            results: List of retrieved chunks
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'Unknown')
            text = result['text']
            score = result['score']
            
            context_parts.append(
                f"[Source {i}: {source} (Relevance: {1/(1+score):.2f})]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_index_info(self) -> Dict:
        """
        Get information about loaded indices
        
        Returns:
            Dictionary with index information
        """
        info = {
            "total_indices": len(self.indices),
            "indices": {}
        }
        
        for name, index in self.indices.items():
            info["indices"][name] = {
                "vectors": index.ntotal,
                "chunks": len(self.metadata.get(name, []))
            }
        
        return info


# Made with Bob