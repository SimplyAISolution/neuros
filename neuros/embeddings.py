"""Embedding module for NEUROS - Sentence transformer-based semantic encoding."""

import numpy as np
from typing import List, Dict, Optional, Tuple
import os
import logging

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    logging.warning(f"Optional dependencies not installed: {e}")
    SentenceTransformer = None
    chromadb = None


class EmbeddingManager:
    """Manages semantic embeddings using sentence transformers and ChromaDB."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", 
                 db_path: str = "./chroma_db"):
        """Initialize embedding manager.
        
        Args:
            model_name: Name of the sentence transformer model
            db_path: Path to ChromaDB storage
        """
        self.model_name = model_name
        self.db_path = db_path
        self.model = None
        self.chroma_client = None
        self.collection = None
        
        self._initialize_model()
        self._initialize_chroma()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if SentenceTransformer is None:
            logging.warning("SentenceTransformer not available. Install with: pip install sentence-transformers")
            return
        
        try:
            self.model = SentenceTransformer(self.model_name)
            logging.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to load embedding model {self.model_name}: {e}")
    
    def _initialize_chroma(self):
        """Initialize ChromaDB for vector storage."""
        if chromadb is None:
            logging.warning("ChromaDB not available. Install with: pip install chromadb")
            return
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.db_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="neuros_memories",
                metadata={"hnsw:space": "cosine"}
            )
            
            logging.info(f"Initialized ChromaDB at {self.db_path}")
            
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB: {e}")
    
    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """Encode text into embeddings.
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding vector or None if encoding fails
        """
        if self.model is None:
            return None
            
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logging.error(f"Failed to encode text: {e}")
            return None
    
    def encode_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """Encode multiple texts into embeddings.
        
        Args:
            texts: List of texts to encode
            
        Returns:
            Array of embedding vectors or None if encoding fails
        """
        if self.model is None:
            return None
            
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logging.error(f"Failed to encode batch: {e}")
            return None
    
    def store_embedding(self, memory_id: str, text: str, 
                       metadata: Optional[Dict] = None) -> bool:
        """Store text embedding in ChromaDB.
        
        Args:
            memory_id: Unique identifier for the memory
            text: Text content to embed and store
            metadata: Optional metadata to store
            
        Returns:
            True if storage successful, False otherwise
        """
        if self.collection is None or self.model is None:
            return False
        
        try:
            # Generate embedding
            embedding = self.encode_text(text)
            if embedding is None:
                return False
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding.tolist()],
                documents=[text],
                metadatas=[metadata or {}],
                ids=[str(memory_id)]
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to store embedding for memory {memory_id}: {e}")
            return False
    
    def search_similar(self, query_text: str, n_results: int = 5, 
                      min_similarity: float = 0.1) -> List[Dict]:
        """Search for similar memories using semantic similarity.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar memories with metadata
        """
        if self.collection is None or self.model is None:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.encode_text(query_text)
            if query_embedding is None:
                return []
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results
            )
            
            # Format results
            similar_memories = []
            for i, (doc, metadata, distance, memory_id) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0],
                results['ids'][0]
            )):
                similarity = 1 - distance  # Convert distance to similarity
                if similarity >= min_similarity:
                    similar_memories.append({
                        'memory_id': memory_id,
                        'content': doc,
                        'metadata': metadata,
                        'similarity': similarity
                    })
            
            return similar_memories
            
        except Exception as e:
            logging.error(f"Failed to search for similar memories: {e}")
            return []
    
    def update_embedding(self, memory_id: str, text: str, 
                        metadata: Optional[Dict] = None) -> bool:
        """Update an existing embedding.
        
        Args:
            memory_id: Memory ID to update
            text: New text content
            metadata: New metadata
            
        Returns:
            True if update successful, False otherwise
        """
        if self.collection is None:
            return False
        
        try:
            # Delete existing embedding
            self.collection.delete(ids=[str(memory_id)])
            
            # Store new embedding
            return self.store_embedding(memory_id, text, metadata)
            
        except Exception as e:
            logging.error(f"Failed to update embedding for memory {memory_id}: {e}")
            return False
    
    def delete_embedding(self, memory_id: str) -> bool:
        """Delete an embedding from storage.
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if self.collection is None:
            return False
        
        try:
            self.collection.delete(ids=[str(memory_id)])
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete embedding for memory {memory_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the embedding collection.
        
        Returns:
            Dictionary with collection statistics
        """
        if self.collection is None:
            return {'count': 0, 'model': self.model_name}
        
        try:
            count = self.collection.count()
            return {
                'count': count,
                'model': self.model_name,
                'db_path': self.db_path
            }
        except Exception as e:
            logging.error(f"Failed to get collection stats: {e}")
            return {'count': 0, 'model': self.model_name}
    
    def reset_collection(self) -> bool:
        """Reset (delete all) embeddings in the collection.
        
        Returns:
            True if reset successful, False otherwise
        """
        if self.chroma_client is None:
            return False
        
        try:
            self.chroma_client.delete_collection("neuros_memories")
            self.collection = self.chroma_client.create_collection(
                name="neuros_memories",
                metadata={"hnsw:space": "cosine"}
            )
            return True
            
        except Exception as e:
            logging.error(f"Failed to reset collection: {e}")
            return False
    
    def close(self):
        """Clean up resources."""
        # ChromaDB handles persistence automatically
        self.collection = None
        self.chroma_client = None
        self.model = None
