#!/usr/bin/env python3
"""
Command-line interface for the Content Generator package.
"""

import argparse
import sys
from . import ContentGenerator
from .config import DEFAULT_METADATA_PATH, DEFAULT_OUTPUT_DIR

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Generate content using Claude API')
    
    # Main arguments
    parser.add_argument('--topic', type=str, help='Topic to generate content for')
    parser.add_argument('--type', type=str, default='lesson', help='Type of content (lesson, lab, etc.)')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_DIR, help='Output directory')
    
    # Metadata-based generation
    parser.add_argument('--metadata', type=str, default=DEFAULT_METADATA_PATH, help='Path to metadata file')
    parser.add_argument('--category', type=str, help='Category in metadata')
    parser.add_argument('--item', type=int, help='Item index in category')
    parser.add_argument('--list-categories', action='store_true', help='List categories in metadata')
    parser.add_argument('--list-items', type=str, help='List items in a category')
    
    # Options
    parser.add_argument('--no-examples', action='store_true', help='Do not include examples in prompt')
    parser.add_argument('--no-save', action='store_true', help='Do not save generated content to file')
    parser.add_argument('--objectives', type=str, nargs='+', help='Learning objectives')
    
    return parser.parse_args()

def list_categories(generator):
    """List categories in metadata"""
    categories = generator.get_categories()
    if not categories:
        print("No categories found in metadata.")
        return
    
    print("Available categories:")
    for i, category in enumerate(categories):
        print(f"{i+1}. {category}")

def list_items(generator, category):
    """List items in a category"""
    items = generator.get_items_in_category(category)
    if not items:
        print(f"No items found in category '{category}'.")
        return
    
    print(f"Items in category '{category}':")
    for i, item in enumerate(items):
        from .extractors.metadata_extractor import get_item_name
        name = get_item_name(item)
        print(f"{i}. {name}")

def main():
    """Main entry point for the CLI"""
    args = parse_args()
    
    # Initialize the generator
    generator = ContentGenerator(
        metadata_path=args.metadata,
        output_dir=args.output
    )
    
    # List categories if requested
    if args.list_categories:
        list_categories(generator)
        return
    
    # List items if requested
    if args.list_items:
        list_items(generator, args.list_items)
        return
    
    # Generate content from metadata
    if args.category is not None and args.item is not None:
        print(f"Generating content from metadata for category '{args.category}', item {args.item}...")
        content = generator.generate_from_metadata(
            args.category,
            args.item,
            include_examples=not args.no_examples,
            save=not args.no_save
        )
        if not content:
            print("Failed to generate content.")
            return
        
        if args.no_save:
            print("\n=== Generated Content ===\n")
            print(content)
            print("\n=== End of Generated Content ===\n")
        
        print("Content generation complete!")
        return
    
    # Generate content from topic
    if args.topic:
        print(f"Generating {args.type} on '{args.topic}'...")
        content = generator.generate_from_topic(
            args.topic,
            file_type=args.type,
            learning_objectives=args.objectives,
            save=not args.no_save
        )
        
        if not content:
            print("Failed to generate content.")
            return
        
        if args.no_save:
            print("\n=== Generated Content ===\n")
            print(content)
            print("\n=== End of Generated Content ===\n")
        
        print("Content generation complete!")
        return
    
    # If no generation options were provided, show help
    print("No generation options provided. Use --topic or --category and --item to generate content.")
    print("Use --help for more information.")

if __name__ == '__main__':
    main()
