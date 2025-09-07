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
        # Validate metadata before storing
        if metadata is not None and not isinstance(metadata, dict):
            metadata = None
        
        # Store in SQLite
        memory_id = self.storage.store_memory(content, metadata, tags, importance)
        
        # Store embedding if enabled
        if self.embeddings and memory_id:
            success = self.embeddings.store_embedding(
                str(memory_id), content, metadata or {}
            )
            if not success:
                logging.warning(f"Failed to store embedding for memory {memory_id}")
        
        if memory_id:
            logging.info(f"Stored memory with ID: {memory_id}")
        else:
            logging.error("Failed to store memory")
            
        return memory_id
    
    def recall(self, query: str, limit: int = 10, 
              tags: Optional[List[str]] = None, 
              importance_min: int = 1) -> List[Dict[str, Any]]:
        """Retrieve memories matching the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            tags: Optional tag filter
            importance_min: Minimum importance level
            
        Returns:
            List of memory dictionaries
        """
        if self.embeddings:
            # Use semantic search
            try:
                semantic_results = self.embeddings.search(
                    query, limit=limit
                )
                
                if semantic_results:
                    memory_ids = [int(result['id']) for result in semantic_results]
                    memories = self.storage.get_memories_by_ids(memory_ids)
                    
                    # Filter by tags and importance if specified
                    if tags or importance_min > 1:
                        memories = self._filter_memories(memories, tags, importance_min)
                    
                    logging.info(f"Semantic search returned {len(memories)} memories")
                    return memories
            except Exception as e:
                logging.warning(f"Semantic search failed: {e}, falling back to text search")
        
        # Fallback to text search
        memories = self.storage.search_memories(
            query, limit=limit, tags=tags, importance_min=importance_min
        )
        logging.info(f"Text search returned {len(memories)} memories")
        return memories
    
    def reason(self, query: str, context_limit: int = 5) -> List[Dict[str, Any]]:
        """Reason about a query by recalling relevant memories.
        
        Args:
            query: The reasoning query
            context_limit: Maximum number of memories to consider
            
        Returns:
            List of relevant memories for reasoning
        """
        # Ensure context_limit is an integer
        context_limit = int(context_limit)
        
        # Use recall to get relevant memories
        relevant_memories = self.recall(query, limit=context_limit)
        
        logging.info(f"Reasoning with {len(relevant_memories)} memories for query: {query}")
        return relevant_memories
    
    def _filter_memories(self, memories: List[Dict], 
                        tags: Optional[List[str]] = None,
                        importance_min: int = 1) -> List[Dict]:
        """Filter memories by tags and importance."""
        filtered = memories
        
        if tags:
            filtered = [m for m in filtered 
                       if m.get('tags') and any(tag in m['tags'] for tag in tags)]
        
        if importance_min > 1:
            filtered = [m for m in filtered 
                       if m.get('importance', 1) >= importance_min]
        
        return filtered
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID.
        
        Args:
            memory_id: Memory ID to retrieve
            
        Returns:
            Memory dictionary or None if not found
        """
        return self.storage.get_memory_by_id(memory_id)
    
    def update_memory(self, memory_id: int, content: str = None, 
                     metadata: Dict = None, tags: List[str] = None, 
                     importance: int = None) -> bool:
        """Update an existing memory.
        
        Args:
            memory_id: ID of memory to update
            content: New content (optional)
            metadata: New metadata (optional)
            tags: New tags (optional)
            importance: New importance (optional)
            
        Returns:
            True if update successful
        """
        success = self.storage.update_memory(
            memory_id, content, metadata, tags, importance
        )
        
        if success and self.embeddings and content:
            # Update embedding if content changed
            self.embeddings.update_embedding(
                str(memory_id), content, metadata or {}
            )
        
        return success
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if deletion successful
        """
        success = self.storage.delete_memory(memory_id)
        
        if success and self.embeddings:
            self.embeddings.delete_embedding(str(memory_id))
        
        return success
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all stored memories.
        
        Returns:
            List of all memory dictionaries
        """
        return self.storage.get_all_memories()
    
    def get_memory_count(self) -> int:
        """Get total number of memories.
        
        Returns:
            Total memory count
        """
        return self.storage.get_memory_count()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics.
        
        Returns:
            Dictionary with system stats
        """
        stats = {
            'total_memories': self.get_memory_count(),
            'embeddings_enabled': self.embeddings is not None,
            'db_path': self.db_path,
            'embedding_model': self.embedding_model if self.embeddings else None
        }
        
        if self.embeddings:
            stats['embedding_count'] = self.embeddings.get_count()
        
        return stats
    
    def export_memories(self, format: str = 'json') -> str:
        """Export all memories in specified format.
        
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
