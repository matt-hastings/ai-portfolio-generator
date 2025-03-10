#!/usr/bin/env python3
"""
Example usage of the Content Generator package.
"""

from content_generator import ContentGenerator

def example_topic_generation():
    """Example of generating content from a topic"""
    print("Example: Generating content from a topic")
    
    # Initialize the generator
    generator = ContentGenerator()
    
    # Define topic and learning objectives
    topic = "Python List Comprehensions"
    file_type = "lesson"
    learning_objectives = [
        "Understand the syntax of list comprehensions",
        "Compare list comprehensions to traditional loops",
        "Apply list comprehensions to solve real-world problems"
    ]
    
    # Generate content
    print(f"Generating {file_type} on '{topic}'...")
    content = generator.generate_from_topic(
        topic,
        file_type=file_type,
        learning_objectives=learning_objectives
    )
    
    print("Content generation complete!")
    print(f"Content saved to generated_content/{file_type}_{topic.replace(' ', '_')}.md")

def example_metadata_generation():
    """Example of generating content from metadata"""
    print("\nExample: Generating content from metadata")
    
    # Initialize the generator with metadata
    generator = ContentGenerator(metadata_path='sample_content/content_metadata')
    
    # List categories
    print("Available categories:")
    categories = generator.get_categories()
    for i, category in enumerate(categories):
        print(f"{i+1}. {category}")
    
    # Select a category
    category = "GA_Lesson_Examples"
    print(f"\nItems in category '{category}':")
    items = generator.get_items_in_category(category)
    for i, item in enumerate(items):
        from content_generator.extractors.metadata_extractor import get_item_name
        name = get_item_name(item)
        print(f"{i}. {name}")
    
    # Generate content for an item
    item_index = 0
    print(f"\nGenerating content for item {item_index} in category '{category}'...")
    content = generator.generate_from_metadata(category, item_index)
    
    print("Content generation complete!")

def example_programmatic_usage():
    """Example of programmatic usage with custom settings"""
    print("\nExample: Programmatic usage with custom settings")
    
    # Initialize the generator with custom settings
    generator = ContentGenerator(
        output_dir="custom_output"
    )
    
    # Create a custom metadata item
    item = {
        'topic': "RESTful API Design",
        'file_type': "lesson",
        'learning_objectives': [
            "Understand REST principles",
            "Design resource-oriented APIs",
            "Implement proper HTTP methods"
        ],
        'content_metrics': {
            'word_count': 800,
            'text_to_code_ratio': 0.8,
            'number_of_images': 1,
            'number_of_diagrams': 2
        }
    }
    
    # Generate a prompt without generating content
    from content_generator.generators.prompt_generator import generate_full_prompt
    prompt = generate_full_prompt(item, include_examples=True)
    
    print("Generated prompt:")
    print(f"{prompt[:500]}...\n[Prompt truncated for brevity]")
    
    print("\nYou can now send this prompt to Claude API to generate content.")

if __name__ == "__main__":
    print("Content Generator Package Examples")
    print("=================================\n")
    
    # Uncomment the examples you want to run
    # example_topic_generation()
    # example_metadata_generation()
    example_programmatic_usage()
