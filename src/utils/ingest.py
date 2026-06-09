"""
Document Ingestion Pipeline using Docling
Converts PDFs to structured markdown and creates embeddings
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠️  Docling not available. Install with: pip install docling")


class DocumentIngester:
    """Handles document ingestion, chunking, and embedding generation"""
    
    def __init__(
        self,
        documents_path: str = "./data/documents",
        processed_path: str = "./data/documents/processed",
        vector_db_path: str = "./data/vector_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize document ingester
        
        Args:
            documents_path: Path to raw documents
            processed_path: Path to store processed markdown
            vector_db_path: Path to store FAISS index
            embedding_model: Sentence transformer model name
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.documents_path = Path(documents_path)
        self.processed_path = Path(processed_path)
        self.vector_db_path = Path(vector_db_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create directories
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        print(f"📦 Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        print(f"✅ Embedding dimension: {self.embedding_dim}")
        
        # Initialize Docling converter if available
        if DOCLING_AVAILABLE:
            self.converter = DocumentConverter()
            print(f"✅ Docling converter initialized")
        else:
            self.converter = None
            print(f"⚠️  Docling not available - using fallback text extraction")
    
    def convert_pdf_to_markdown(self, pdf_path: Path) -> str:
        """
        Convert PDF to structured markdown using Docling
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Markdown content
        """
        if not DOCLING_AVAILABLE or self.converter is None:
            # Fallback: simple text extraction
            print(f"⚠️  Using fallback text extraction for {pdf_path.name}")
            return self._fallback_pdf_extraction(pdf_path)
        
        try:
            print(f"📄 Converting {pdf_path.name} to markdown...")
            result = self.converter.convert(str(pdf_path))
            markdown_content = result.document.export_to_markdown()
            print(f"✅ Converted {pdf_path.name} ({len(markdown_content)} chars)")
            return markdown_content
        except Exception as e:
            print(f"❌ Docling conversion failed: {e}")
            print(f"⚠️  Falling back to simple text extraction")
            return self._fallback_pdf_extraction(pdf_path)
    
    def _fallback_pdf_extraction(self, pdf_path: Path) -> str:
        """
        Fallback PDF text extraction without Docling
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                return text
        except ImportError:
            return f"# {pdf_path.stem}\n\nPDF content extraction requires PyPDF2 or Docling."
        except Exception as e:
            return f"# {pdf_path.stem}\n\nError extracting PDF: {str(e)}"
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Intelligently chunk text with overlap
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_id = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": current_chunk.strip(),
                    "metadata": metadata.copy()
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                current_chunk = " ".join(overlap_words) + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "metadata": metadata.copy()
            })
        
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk["text"] for chunk in chunks]
        print(f"🔢 Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        print(f"✅ Generated embeddings: {embeddings.shape}")
        return embeddings
    
    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Create FAISS index from embeddings
        
        Args:
            embeddings: Numpy array of embeddings
            
        Returns:
            FAISS index
        """
        print(f"🗂️  Creating FAISS index...")
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embeddings.astype('float32'))
        print(f"✅ FAISS index created with {index.ntotal} vectors")
        return index
    
    def save_index(self, index: faiss.Index, chunks: List[Dict], index_name: str):
        """
        Save FAISS index and metadata
        
        Args:
            index: FAISS index
            chunks: Chunk metadata
            index_name: Name for the index
        """
        index_path = self.vector_db_path / f"{index_name}.index"
        metadata_path = self.vector_db_path / f"{index_name}_metadata.json"
        
        # Save FAISS index
        faiss.write_index(index, str(index_path))
        print(f"✅ Saved FAISS index to {index_path}")
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved metadata to {metadata_path}")
    
    def ingest_document(self, pdf_path: Path, doc_type: str) -> bool:
        """
        Complete ingestion pipeline for a single document
        
        Args:
            pdf_path: Path to PDF file
            doc_type: Type of document (e.g., 'fifa_rules', 'var_guidelines')
            
        Returns:
            True if successful
        """
        try:
            print(f"\n{'='*60}")
            print(f"📚 Ingesting: {pdf_path.name}")
            print(f"{'='*60}")
            
            # Step 1: Convert PDF to markdown
            markdown = self.convert_pdf_to_markdown(pdf_path)
            
            # Save processed markdown
            markdown_path = self.processed_path / f"{pdf_path.stem}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"✅ Saved markdown to {markdown_path}")
            
            # Step 2: Chunk the text
            metadata = {
                "source": pdf_path.name,
                "doc_type": doc_type,
                "processed_file": str(markdown_path)
            }
            chunks = self.chunk_text(markdown, metadata)
            
            # Step 3: Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            # Step 4: Create FAISS index
            index = self.create_faiss_index(embeddings)
            
            # Step 5: Save index and metadata
            index_name = f"{doc_type}_{pdf_path.stem}"
            self.save_index(index, chunks, index_name)
            
            print(f"{'='*60}")
            print(f"✅ Successfully ingested {pdf_path.name}")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"❌ Failed to ingest {pdf_path.name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ingest_all_documents(self):
        """Ingest all documents in the documents folder"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting Document Ingestion Pipeline")
        print(f"{'='*60}\n")
        
        # Define document categories
        categories = {
            "fifa_rules": self.documents_path / "fifa_rules",
            "var_guidelines": self.documents_path / "var_guidelines"
        }
        
        total_success = 0
        total_failed = 0
        
        for doc_type, folder in categories.items():
            if not folder.exists():
                print(f"⚠️  Folder not found: {folder}")
                continue
            
            pdf_files = list(folder.glob("*.pdf"))
            if not pdf_files:
                print(f"⚠️  No PDF files found in {folder}")
                continue
            
            print(f"\n📁 Processing {doc_type}: {len(pdf_files)} files")
            
            for pdf_path in pdf_files:
                if self.ingest_document(pdf_path, doc_type):
                    total_success += 1
                else:
                    total_failed += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Ingestion Summary")
        print(f"{'='*60}")
        print(f"✅ Successful: {total_success}")
        print(f"❌ Failed: {total_failed}")
        print(f"{'='*60}\n")


def main():
    """Main ingestion script"""
    ingester = DocumentIngester()
    ingester.ingest_all_documents()


if __name__ == "__main__":
    main()

# Made with Bob