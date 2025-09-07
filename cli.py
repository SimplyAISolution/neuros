#!/usr/bin/env python3
"""CLI entrypoint for NEUROS - Neural Enhanced Universal Reasoning and Organizational System."""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Optional

try:
    from neuros import NEUROS
except ImportError:
    print("Error: NEUROS package not found. Please install it first.")
    print("Run: pip install -e .")
    sys.exit(1)


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def remember_command(neuros: NEUROS, content: str, tags: Optional[str] = None, 
                    importance: int = 1, metadata: Optional[str] = None) -> int:
    """Store a new memory."""
    tags_list = tags.split(',') if tags else None
    metadata_dict = json.loads(metadata) if metadata else None
    
    memory_id = neuros.remember(content, metadata_dict, tags_list, importance)
    print(f"Memory stored with ID: {memory_id}")
    return memory_id


def recall_command(neuros: NEUROS, query: str = None, tags: Optional[str] = None,
                  limit: int = 10, semantic: bool = True) -> list:
    """Retrieve memories."""
    tags_list = tags.split(',') if tags else None
    
    memories = neuros.recall(query, tags_list, semantic, limit)
    
    if not memories:
        print("No memories found matching your query.")
        return []
    
    print(f"Found {len(memories)} memories:\n")
    for i, memory in enumerate(memories, 1):
        print(f"[{i}] ID: {memory.get('id')}")
        print(f"    Content: {memory.get('content', '')[:100]}{'...' if len(memory.get('content', '')) > 100 else ''}")
        print(f"    Created: {memory.get('created_at')}")
        
        if memory.get('tags'):
            print(f"    Tags: {', '.join(memory['tags'])}")
        
        if memory.get('similarity'):
            print(f"    Similarity: {memory['similarity']:.3f}")
        
        if memory.get('search_type'):
            print(f"    Search: {memory['search_type']}")
        
        print()
    
    return memories


def reason_command(neuros: NEUROS, query: str, context_limit: int = 5) -> str:
    """Reason over memories."""
    response = neuros.reason(query, context_limit)
    print("NEUROS Reasoning:\n")
    print(response)
    return response


def stats_command(neuros: NEUROS) -> dict:
    """Show system statistics."""
    stats = neuros.get_stats()
    
    print("NEUROS System Statistics:")
    print(f"  Total Memories: {stats.get('total_memories', 0)}")
    print(f"  Database Path: {stats.get('db_path', 'N/A')}")
    print(f"  Embedding Model: {stats.get('embedding_model', 'N/A')}")
    print(f"  Embeddings Enabled: {stats.get('embeddings_enabled', False)}")
    
    if stats.get('embeddings_enabled'):
        print(f"  Embedding Count: {stats.get('embedding_count', 0)}")
        print(f"  ChromaDB Path: {stats.get('chroma_path', 'N/A')}")
    
    return stats


def export_command(neuros: NEUROS, format: str = 'json', output: Optional[str] = None) -> str:
    """Export memories."""
    data = neuros.export_memories(format)
    
    if output:
        Path(output).write_text(data)
        print(f"Memories exported to {output}")
    else:
        print(data)
    
    return data


def reset_command(neuros: NEUROS, confirm: bool = False) -> bool:
    """Reset all memories."""
    if not confirm:
        response = input("This will delete ALL memories. Are you sure? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Reset cancelled.")
            return False
    
    success = neuros.reset()
    if success:
        print("NEUROS system reset successfully.")
    else:
        print("Failed to reset NEUROS system.")
    
    return success


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NEUROS - Neural Enhanced Universal Reasoning and Organizational System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neuros remember "Meeting notes about project X"
  neuros recall "project X" --limit 5
  neuros reason "What was decided about project X?"
  neuros stats
  neuros export --format json --output memories.json
        """
    )
    
    # Global options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--db-path', default='neuros.db',
                       help='Path to SQLite database (default: neuros.db)')
    parser.add_argument('--no-embeddings', action='store_true',
                       help='Disable semantic search')
    parser.add_argument('--embedding-model', default='all-MiniLM-L6-v2',
                       help='Sentence transformer model name')
    parser.add_argument('--chroma-path', default='./chroma_db',
                       help='Path to ChromaDB storage')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Remember command
    remember_parser = subparsers.add_parser('remember', help='Store a new memory')
    remember_parser.add_argument('content', help='Content to remember')
    remember_parser.add_argument('--tags', help='Comma-separated tags')
    remember_parser.add_argument('--importance', type=int, default=1,
                               help='Importance level (1-10)')
    remember_parser.add_argument('--metadata', help='JSON metadata string')
    
    # Recall command
    recall_parser = subparsers.add_parser('recall', help='Retrieve memories')
    recall_parser.add_argument('query', nargs='?', help='Search query')
    recall_parser.add_argument('--tags', help='Comma-separated tags')
    recall_parser.add_argument('--limit', type=int, default=10,
                              help='Maximum number of results')
    recall_parser.add_argument('--no-semantic', action='store_true',
                              help='Disable semantic search')
    
    # Reason command
    reason_parser = subparsers.add_parser('reason', help='Reason over memories')
    reason_parser.add_argument('query', help='Question or query to reason about')
    reason_parser.add_argument('--context-limit', type=int, default=5,
                              help='Number of memories to consider')
    
    # Stats command
    subparsers.add_parser('stats', help='Show system statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export memories')
    export_parser.add_argument('--format', choices=['json', 'text'], default='json',
                              help='Export format')
    export_parser.add_argument('--output', help='Output file path')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset all memories')
    reset_parser.add_argument('--yes', action='store_true',
                             help='Skip confirmation prompt')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return
    
    # Initialize NEUROS
    try:
        neuros = NEUROS(
            db_path=args.db_path,
            embedding_model=args.embedding_model,
            chroma_path=args.chroma_path,
            enable_embeddings=not args.no_embeddings
        )
    except Exception as e:
        print(f"Error initializing NEUROS: {e}")
        sys.exit(1)
    
    # Execute commands
    try:
        if args.command == 'remember':
            remember_command(neuros, args.content, args.tags, 
                           args.importance, args.metadata)
        
        elif args.command == 'recall':
            recall_command(neuros, args.query, args.tags, 
                         args.limit, not args.no_semantic)
        
        elif args.command == 'reason':
            reason_command(neuros, args.query, args.context_limit)
        
        elif args.command == 'stats':
            stats_command(neuros)
        
        elif args.command == 'export':
            export_command(neuros, args.format, args.output)
        
        elif args.command == 'reset':
            reset_command(neuros, args.yes)
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        neuros.close()


if __name__ == '__main__':
    main()
