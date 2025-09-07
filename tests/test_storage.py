import pytest
import tempfile
import os
from pathlib import Path
from neuros.storage import MemoryStorage


class TestMemoryStorage:
    """Test cases for MemoryStorage class."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def storage(self, temp_db_path):
        """Create a MemoryStorage instance for testing."""
        return MemoryStorage(db_path=temp_db_path)
    
    def test_init_creates_db_file(self, temp_db_path):
        """Test that initializing MemoryStorage creates the database file."""
        # Remove the file first
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
        
        storage = MemoryStorage(db_path=temp_db_path)
        assert os.path.exists(temp_db_path)
    
    def test_store_memory(self, storage):
        """Test storing a memory."""
        content = "This is a test memory"
        context = {"source": "test", "importance": 5}
        
        memory_id = storage.store(content, context)
        assert memory_id is not None
        assert isinstance(memory_id, str)
    
    def test_retrieve_memory(self, storage):
        """Test retrieving a stored memory."""
        content = "This is a test memory for retrieval"
        context = {"source": "test", "importance": 8}
        
        memory_id = storage.store(content, context)
        retrieved_memory = storage.retrieve(memory_id)
        
        assert retrieved_memory is not None
        assert retrieved_memory['content'] == content
        assert retrieved_memory['context'] == context
        assert retrieved_memory['id'] == memory_id
    
    def test_retrieve_nonexistent_memory(self, storage):
        """Test retrieving a memory that doesn't exist."""
        result = storage.retrieve("nonexistent-id")
        assert result is None
    
    def test_search_memories(self, storage):
        """Test searching for memories."""
        # Store multiple memories
        storage.store("Python programming tutorial", {"topic": "programming"})
        storage.store("Machine learning basics", {"topic": "AI"})
        storage.store("Python data structures", {"topic": "programming"})
        
        # Search for programming-related memories
        results = storage.search("Python programming")
        assert len(results) >= 1
        
        # Verify search results contain relevant content
        found_programming = any("Python" in result['content'] for result in results)
        assert found_programming
    
    def test_list_all_memories(self, storage):
        """Test listing all stored memories."""
        # Store some test memories
        storage.store("Memory 1", {"test": True})
        storage.store("Memory 2", {"test": True})
        storage.store("Memory 3", {"test": True})
        
        all_memories = storage.list_all()
        assert len(all_memories) >= 3
        
        # Verify all stored memories are present
        contents = [memory['content'] for memory in all_memories]
        assert "Memory 1" in contents
        assert "Memory 2" in contents
        assert "Memory 3" in contents
    
    def test_delete_memory(self, storage):
        """Test deleting a memory."""
        content = "Memory to be deleted"
        memory_id = storage.store(content, {})
        
        # Verify memory exists
        assert storage.retrieve(memory_id) is not None
        
        # Delete memory
        success = storage.delete(memory_id)
        assert success is True
        
        # Verify memory is deleted
        assert storage.retrieve(memory_id) is None
    
    def test_delete_nonexistent_memory(self, storage):
        """Test deleting a memory that doesn't exist."""
        success = storage.delete("nonexistent-id")
        assert success is False
    
    def test_memory_persistence(self, temp_db_path):
        """Test that memories persist between storage instances."""
        content = "Persistent memory test"
        context = {"persistent": True}
        
        # Store memory with first instance
        storage1 = MemoryStorage(db_path=temp_db_path)
        memory_id = storage1.store(content, context)
        
        # Create new instance and retrieve memory
        storage2 = MemoryStorage(db_path=temp_db_path)
        retrieved = storage2.retrieve(memory_id)
        
        assert retrieved is not None
        assert retrieved['content'] == content
        assert retrieved['context'] == context
