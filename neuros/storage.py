"""Storage module for NEUROS - SQLite-based memory management."""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class MemoryStorage:
    """SQLite-based storage for NEUROS memories with metadata support."""
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize memory storage.
        
        Args:
            db_path: Path to SQLite database file. Defaults to in-memory DB.
        """
        self.db_path = db_path
        self.connection = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database connection and initialize tables."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        # Create memories table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT,
                embedding_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                importance INTEGER DEFAULT 1
            )
        """)
        
        # Create index for faster searching
        self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_created_at 
            ON memories(created_at)
        """)
        
        self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_importance 
            ON memories(importance)
        """)
        
        self.connection.commit()
    
    def store_memory(self, content: str, metadata: Optional[Dict] = None, 
                    tags: Optional[List[str]] = None, importance: int = 1) -> int:
        """Store a new memory.
        
        Args:
            content: The memory content
            metadata: Optional metadata dictionary
            tags: Optional list of tags
            importance: Importance level (1-10)
            
        Returns:
            The ID of the stored memory
        """
        metadata_json = json.dumps(metadata) if metadata else None
        tags_json = json.dumps(tags) if tags else None
        
        cursor = self.connection.execute("""
            INSERT INTO memories (content, metadata, tags, importance)
            VALUES (?, ?, ?, ?)
        """, (content, metadata_json, tags_json, importance))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a memory by ID.
        
        Args:
            memory_id: The memory ID
            
        Returns:
            Memory dictionary or None if not found
        """
        cursor = self.connection.execute("""
            SELECT * FROM memories WHERE id = ?
        """, (memory_id,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
    
    def search_memories(self, query: str = None, tags: List[str] = None, 
                       limit: int = 50) -> List[Dict[str, Any]]:
        """Search memories by content or tags.
        
        Args:
            query: Text to search for in content
            tags: List of tags to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        
        if tags:
            for tag in tags:
                sql += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.connection.execute(sql, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def update_memory(self, memory_id: int, content: str = None, 
                     metadata: Dict = None, tags: List[str] = None, 
                     importance: int = None) -> bool:
        """Update an existing memory.
        
        Args:
            memory_id: The memory ID to update
            content: New content (optional)
            metadata: New metadata (optional)
            tags: New tags (optional)
            importance: New importance level (optional)
            
        Returns:
            True if memory was updated, False if not found
        """
        updates = []
        params = []
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))
        
        if importance is not None:
            updates.append("importance = ?")
            params.append(importance)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        sql = f"UPDATE memories SET {', '.join(updates)} WHERE id = ?"
        params.append(memory_id)
        
        cursor = self.connection.execute(sql, params)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: The memory ID to delete
            
        Returns:
            True if memory was deleted, False if not found
        """
        cursor = self.connection.execute("""
            DELETE FROM memories WHERE id = ?
        """, (memory_id,))
        
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_all_memories(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all memories.
        
        Args:
            limit: Optional limit on number of memories
            
        Returns:
            List of all memories
        """
        sql = "SELECT * FROM memories ORDER BY created_at DESC"
        params = []
        
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        
        cursor = self.connection.execute(sql, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary."""
        result = dict(row)
        
        # Parse JSON fields
        if result.get('metadata'):
            try:
                result['metadata'] = json.loads(result['metadata'])
            except json.JSONDecodeError:
                result['metadata'] = None
        
        if result.get('tags'):
            try:
                result['tags'] = json.loads(result['tags'])
            except json.JSONDecodeError:
                result['tags'] = []
        
        return result
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
