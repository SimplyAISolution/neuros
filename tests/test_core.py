import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from neuros.core import NEUROS
from neuros.storage import MemoryStorage


class TestNEUROS:
    """Test cases for NEUROS core functionality."""
    
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
    def neuros_instance(self, temp_db_path):
        """Create a NEUROS instance for testing."""
        return NEUROS(db_path=temp_db_path)
    
    def test_neuros_initialization(self, temp_db_path):
        """Test NEUROS initialization."""
        neuros = NEUROS(db_path=temp_db_path)
        assert neuros.storage is not None
        assert isinstance(neuros.storage, MemoryStorage)
    
    def test_neuros_initialization_default_path(self):
        """Test NEUROS initialization with default database path."""
        neuros = NEUROS()
        assert neuros.storage is not None
        assert isinstance(neuros.storage, MemoryStorage)
    
    def test_store_memory(self, neuros_instance):
        """Test storing a memory through NEUROS interface."""
        content = "Test memory for NEUROS storage"
        context = {"source": "test", "type": "note"}
        
        memory_id = neuros_instance.store(content, context)
        assert memory_id is not None
        assert isinstance(memory_id, str)
    
    def test_retrieve_memory(self, neuros_instance):
        """Test retrieving a memory through NEUROS interface."""
        content = "Test memory for NEUROS retrieval"
        context = {"source": "test", "type": "note"}
        
        memory_id = neuros_instance.store(content, context)
        retrieved_memory = neuros_instance.retrieve(memory_id)
        
        assert retrieved_memory is not None
        assert retrieved_memory['content'] == content
        assert retrieved_memory['context'] == context
        assert retrieved_memory['id'] == memory_id
    
    def test_recall_memories(self, neuros_instance):
        """Test recalling memories using NEUROS semantic search."""
        # Store test memories
        neuros_instance.store("Python programming concepts", {"topic": "programming"})
        neuros_instance.store("Machine learning algorithms", {"topic": "AI"})
        neuros_instance.store("Python data analysis", {"topic": "data"})
        
        # Test recall functionality
        results = neuros_instance.recall("Python programming")
        assert len(results) >= 1
        
        # Verify relevant memories are recalled
        found_relevant = any("Python" in result['content'] for result in results)
        assert found_relevant
    
    def test_recall_empty_query(self, neuros_instance):
        """Test recall with empty query."""
        neuros_instance.store("Some memory content", {})
        
        results = neuros_instance.recall("")
        # Should return some results or handle gracefully
        assert isinstance(results, list)
    
    def test_recall_no_matches(self, neuros_instance):
        """Test recall when no memories match the query."""
        neuros_instance.store("Unrelated content about cats", {})
        
        results = neuros_instance.recall("quantum physics")
        # Should return empty list or very low relevance matches
        assert isinstance(results, list)
    
    @patch('neuros.core.NEUROS._generate_reasoning_response')
    def test_reason_basic(self, mock_reasoning, neuros_instance):
        """Test basic reasoning functionality."""
        # Mock the reasoning response
        mock_reasoning.return_value = "Based on the memories, here is my reasoning..."
        
        # Store some relevant memories
        neuros_instance.store("The sky is blue because of light scattering", {"topic": "science"})
        neuros_instance.store("Blue light has shorter wavelengths", {"topic": "physics"})
        
        # Test reasoning
        query = "Why is the sky blue?"
        response = neuros_instance.reason(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        mock_reasoning.assert_called_once()
    
    @patch('neuros.core.NEUROS._generate_reasoning_response')
    def test_reason_with_context(self, mock_reasoning, neuros_instance):
        """Test reasoning with additional context."""
        mock_reasoning.return_value = "Contextual reasoning response"
        
        # Store memories
        neuros_instance.store("Project deadline is next week", {"project": "MVP"})
        
        # Test reasoning with context
        query = "What should I prioritize?"
        context = {"project": "MVP", "urgency": "high"}
        response = neuros_instance.reason(query, context)
        
        assert response is not None
        assert isinstance(response, str)
        mock_reasoning.assert_called_once()
    
    def test_reason_empty_query(self, neuros_instance):
        """Test reasoning with empty query."""
        with pytest.raises((ValueError, TypeError)):
            neuros_instance.reason("")
    
    def test_reason_none_query(self, neuros_instance):
        """Test reasoning with None query."""
        with pytest.raises((ValueError, TypeError)):
            neuros_instance.reason(None)
    
    def test_integration_store_recall_reason(self, neuros_instance):
        """Test integration of store, recall, and reason operations."""
        # Store related memories
        neuros_instance.store("Python is a programming language", {"topic": "programming"})
        neuros_instance.store("Python is great for data science", {"topic": "data_science"})
        neuros_instance.store("Data science involves statistics", {"topic": "statistics"})
        
        # Test recall
        recall_results = neuros_instance.recall("Python programming")
        assert len(recall_results) >= 1
        
        # Test reasoning (will use mocked response in integration)
        with patch.object(neuros_instance, '_generate_reasoning_response') as mock_reason:
            mock_reason.return_value = "Python is versatile for programming and data science."
            
            reason_result = neuros_instance.reason("What can Python be used for?")
            assert reason_result is not None
            assert "Python" in reason_result
    
    def test_memory_persistence_across_sessions(self, temp_db_path):
        """Test that memories persist across NEUROS instances."""
        content = "Persistent memory across sessions"
        context = {"session": "test"}
        
        # Store with first instance
        neuros1 = NEUROS(db_path=temp_db_path)
        memory_id = neuros1.store(content, context)
        
        # Retrieve with second instance
        neuros2 = NEUROS(db_path=temp_db_path)
        retrieved = neuros2.retrieve(memory_id)
        
        assert retrieved is not None
        assert retrieved['content'] == content
        assert retrieved['context'] == context
    
    def test_error_handling_invalid_memory_id(self, neuros_instance):
        """Test error handling for invalid memory ID."""
        result = neuros_instance.retrieve("invalid-memory-id")
        assert result is None
    
    def test_error_handling_corrupted_context(self, neuros_instance):
        """Test handling of various context types."""
        # Test with different context types
        neuros_instance.store("Test with None context", None)
        neuros_instance.store("Test with empty context", {})
        neuros_instance.store("Test with string context", "string_context")
        neuros_instance.store("Test with number context", 123)
        
        # All should work without raising exceptions
        memories = neuros_instance.recall("Test")
        assert len(memories) >= 4
