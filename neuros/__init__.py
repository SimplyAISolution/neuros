"""NEUROS: Neural Enhanced Universal Reasoning and Organizational System

A local-first AI memory and reasoning system that provides persistent memory
and enhanced reasoning capabilities for personal AI interactions.
"""

__version__ = "0.1.0"
__author__ = "NEUROS Team"
__email__ = "support@neuros.ai"

# Core imports
from .core import NEUROS
from .storage import MemoryStorage
from .embeddings import EmbeddingManager

__all__ = [
    "NEUROS",
    "MemoryStorage", 
    "EmbeddingManager"
]
