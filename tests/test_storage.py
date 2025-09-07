import os
import tempfile
import pytest
from neuros.storage import MemoryStorage

@pytest.fixture
def temp_db():
    # Create a temporary file for the SQLite database
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmpfile.name
    tmpfile.close()
    storage = MemoryStorage(db_path)
    yield storage
    storage.close()
    os.remove(db_path)

def test_store_and_retrieve_memory(temp_db):
    mem_id = temp_db.store_memory("Test content", metadata={"a": 1}, tags=["test"], importance=2)
    memory = temp_db.get_memory(mem_id)
    assert memory is not None
    assert memory["content"] == "Test content"
    assert memory["metadata"]["a"] == 1
    assert "test" in memory["tags"]
    assert memory["importance"] == 2

def test_search_memories_by_content(temp_db):
    id1 = temp_db.store_memory("First test memory")
    id2 = temp_db.store_memory("Second memory keyword")
    results = temp_db.search_memories("keyword")
    assert any(r["content"] == "Second memory keyword" for r in results)
    assert all("memory" in r["content"] for r in results)

def test_search_memories_by_tags(temp_db):
    id1 = temp_db.store_memory("Alpha", tags=["x", "y"])
    id2 = temp_db.store_memory("Beta", tags=["y", "z"])
    results = temp_db.search_memories(tags=["x"])
    assert len(results) == 1 and results[0]["content"] == "Alpha"
    results = temp_db.search_memories(tags=["y"])
    assert len(results) == 2

def test_update_memory(temp_db):
    mem_id = temp_db.store_memory("To be updated", metadata={"foo": "bar"}, tags=["old"], importance=3)
    updated = temp_db.update_memory(mem_id, content="Updated content", metadata={"foo": "baz"}, tags=["new"], importance=5)
    assert updated
    memory = temp_db.get_memory(mem_id)
    assert memory["content"] == "Updated content"
    assert memory["metadata"]["foo"] == "baz"
    assert "new" in memory["tags"]
    assert memory["importance"] == 5

def test_delete_memory(temp_db):
    mem_id = temp_db.store_memory("To delete")
    success = temp_db.delete_memory(mem_id)
    assert success
    assert temp_db.get_memory(mem_id) is None

def test_get_all_memories(temp_db):
    ids = [temp_db.store_memory(f"Mem {i}") for i in range(5)]
    all_memories = temp_db.get_all_memories()
    assert len(all_memories) == 5

def test_persistence_across_instances():
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmpfile.name
    tmpfile.close()
    try:
        s1 = MemoryStorage(db_path)
        mem_id = s1.store_memory("Persistent memory")
        s1.close()
        s2 = MemoryStorage(db_path)
        memory = s2.get_memory(mem_id)
        s2.close()
        assert memory is not None and memory["content"] == "Persistent memory"
    finally:
        os.remove(db_path)

def test_error_handling_nonexistent(temp_db):
    assert temp_db.get_memory(99999) is None
    assert not temp_db.update_memory(99999, content="Nothing")
    assert not temp_db.delete_memory(99999)
