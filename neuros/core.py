"""Core module for NEUROS - Main API and orchestration."""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from .storage import MemoryStorage
from .embeddings import EmbeddingManager


class NEUROS:
    """Main NEUROS class that orchestrates memory storage and semantic search."""
    
    def __init__(self, 
                 db_path: str = ":memory:",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chroma_path: str = "./chroma_db",
                 enable_embeddings: bool = True):
        """Initialize NEUROS system.
        
        Args:
            db_path: Path to SQLite database
            embedding_model: Name of sentence transformer model
            chroma_path: Path to ChromaDB storage
            enable_embeddings: Whether to enable semantic search
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.chroma_path = chroma_path
        self.enable_embeddings = enable_embeddings
        
        # Initialize storage
        self.storage = MemoryStorage(db_path)
        
        # Initialize embeddings if enabled
        self.embeddings = None
        if enable_embeddings:
            try:
                self.embeddings = EmbeddingManager(embedding_model, chroma_path)
                logging.info("NEUROS initialized with semantic search enabled")
            except Exception as e:
                logging.warning(f"Failed to initialize embeddings: {e}")
                logging.warning("NEUROS will operate without semantic search")
        else:
            logging.info("NEUROS initialized without semantic search")
    
    def remember(self, content: str, metadata: Optional[Dict] = None, 
                tags: Optional[List[str]] = None, importance: int = 1) -> int:
        """Store a new memory.
        
        Args:
            content: The content to remember
            metadata: Optional metadata dictionary
            tags: Optional list of tags
            importance: Importance level (1-10)
            
        Returns:
            Memory ID of the stored memory
        """
        # Store in SQLite
        memory_id = self.storage.store_memory(content, metadata, tags, importance)
        
        # Store embedding if enabled
        if self.embeddings and memory_id:
            success = self.embeddings.store_embedding(
                str(memory_id), content, metadata
            )
            if not success:
                logging.warning(f"Failed to store embedding for memory {memory_id}")
        
        logging.info(f"Stored memory {memory_id}: {content[:50]}...")
        return memory_id
    
    def recall(self, query: str = None, tags: List[str] = None, 
              use_semantic: bool = True, limit: int = 10, 
              min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """Retrieve memories based on query.
        
        Args:
            query: Text query to search for
            tags: Tags to filter by
            use_semantic: Whether to use semantic search
            limit: Maximum number of results
            min_similarity: Minimum similarity for semantic search
            
        Returns:
            List of matching memories
        """
        memories = []
        
        # Try semantic search first if enabled and query provided
        if (use_semantic and self.embeddings and query and 
            query.strip() and len(query.strip()) > 2):
            try:
                semantic_results = self.embeddings.search_similar(
                    query, limit, min_similarity
                )
                
                # Get full memory details from storage
                for result in semantic_results:
                    memory_id = int(result['memory_id'])
                    memory = self.storage.get_memory(memory_id)
                    if memory:
                        memory['similarity'] = result['similarity']
                        memory['search_type'] = 'semantic'
                        memories.append(memory)
                
                logging.info(f"Semantic search found {len(memories)} memories")
                
                # If semantic search found enough results, return them
                if len(memories) >= limit or len(memories) > 0:
                    return memories[:limit]
            
            except Exception as e:
                logging.warning(f"Semantic search failed: {e}")
        
        # Fall back to text search in SQLite
        try:
            text_results = self.storage.search_memories(query, tags, limit)
            for memory in text_results:
                memory['search_type'] = 'text'
                memories.append(memory)
            
            logging.info(f"Text search found {len(text_results)} memories")
        
        except Exception as e:
            logging.error(f"Text search failed: {e}")
        
        return memories[:limit]
    
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID.
        
        Args:
            memory_id: The memory ID
            
        Returns:
            Memory dictionary or None if not found
        """
        return self.storage.get_memory(memory_id)
    
    def update_memory(self, memory_id: int, content: str = None, 
                     metadata: Dict = None, tags: List[str] = None, 
                     importance: int = None) -> bool:
        """Update an existing memory.
        
        Args:
            memory_id: Memory ID to update
            content: New content
            metadata: New metadata
            tags: New tags
            importance: New importance level
            
        Returns:
            True if update successful
        """
        # Update in SQLite
        success = self.storage.update_memory(
            memory_id, content, metadata, tags, importance
        )
        
        # Update embedding if content changed and embeddings enabled
        if success and content and self.embeddings:
            embed_success = self.embeddings.update_embedding(
                str(memory_id), content, metadata
            )
            if not embed_success:
                logging.warning(f"Failed to update embedding for memory {memory_id}")
        
        return success
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if deletion successful
        """
        # Delete from SQLite
        success = self.storage.delete_memory(memory_id)
        
        # Delete embedding if exists
        if success and self.embeddings:
            embed_success = self.embeddings.delete_embedding(str(memory_id))
            if not embed_success:
                logging.warning(f"Failed to delete embedding for memory {memory_id}")
        
        return success
    
    def get_all_memories(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all memories.
        
        Args:
            limit: Optional limit on number of memories
            
        Returns:
            List of all memories
        """
        return self.storage.get_all_memories(limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics.
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            'total_memories': len(self.storage.get_all_memories()),
            'db_path': self.db_path,
            'embedding_model': self.embedding_model,
            'embeddings_enabled': self.embeddings is not None
        }
        
        if self.embeddings:
            embedding_stats = self.embeddings.get_collection_stats()
            stats.update({
                'embedding_count': embedding_stats.get('count', 0),
                'chroma_path': embedding_stats.get('db_path', self.chroma_path)
            })
        
        return stats
    
    def reason(self, query: str, context_limit: int = 5) -> str:
        """Simple reasoning over memories (MVP implementation).
        
        Args:
            query: Question or query to reason about
            context_limit: Number of relevant memories to consider
            
        Returns:
            Reasoning response based on memories
        """
        # Get relevant memories
        memories = self.recall(query, limit=context_limit)
        
        if not memories:
            return "I don't have any relevant memories to answer that question."
        
        # Simple reasoning: concatenate relevant memories
        context_parts = []
        for i, memory in enumerate(memories, 1):
            content = memory.get('content', '')
            similarity = memory.get('similarity', 0)
            search_type = memory.get('search_type', 'unknown')
            
            context_parts.append(
                f"Memory {i} ({search_type}, similarity: {similarity:.2f}): {content}"
            )
        
        context = "\n\n".join(context_parts)
        
        # MVP reasoning response
        response = f"Based on {len(memories)} relevant memories:\n\n{context}\n\n"
        response += f"To answer '{query}', I found the above related information. "
        response += "For more sophisticated reasoning, this MVP can be enhanced with LLM integration."
        
        return response
    
    def export_memories(self, format: str = 'json') -> str:
        """Export all memories.
        
        Args:
            format: Export format ('json' or 'text')
            
        Returns:
            Exported data as string
        """
        memories = self.get_all_memories()
        
        if format == 'json':
            import json
            return json.dumps(memories, indent=2, default=str)
        
        elif format == 'text':
            lines = []
            for memory in memories:
                lines.append(f"ID: {memory.get('id')}")
                lines.append(f"Content: {memory.get('content')}")
                lines.append(f"Created: {memory.get('created_at')}")
                if memory.get('tags'):
                    lines.append(f"Tags: {', '.join(memory['tags'])}")
                lines.append("-" * 50)
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def reset(self) -> bool:
        """Reset all memories and embeddings.
        
        Returns:
            True if reset successful
        """
        try:
            # Reset embeddings first
            if self.embeddings:
                self.embeddings.reset_collection()
            
            # Close and reinitialize storage
            self.storage.close()
            if self.db_path != ":memory:":
                Path(self.db_path).unlink(missing_ok=True)
            
            self.storage = MemoryStorage(self.db_path)
            
            logging.info("NEUROS system reset successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to reset NEUROS: {e}")
            return False
    
    def close(self):
        """Clean up resources."""
        if self.storage:
            self.storage.close()
        
        if self.embeddings:
            self.embeddings.close()
        
        logging.info("NEUROS system closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
