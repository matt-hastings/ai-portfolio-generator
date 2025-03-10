"""
Content Generator Package

A modular, context-independent package for generating content using Claude API.
"""

import os
from .extractors.metadata_extractor import (
    extract_metadata, get_categories, get_items_in_category,
    get_item_by_index, get_item_name, get_file_type
)
from .generators.prompt_generator import generate_full_prompt, generate_prompt_from_topic
from .utils.api_utils import generate_content_with_claude
from .utils.file_utils import write_file
from .config import DEFAULT_OUTPUT_DIR

class ContentGenerator:
    """
    Main class for generating content using Claude API
    """
    
    def __init__(self, api_key=None, metadata_path=None, output_dir=DEFAULT_OUTPUT_DIR):
        """
        Initialize the ContentGenerator
        
        Args:
            api_key (str, optional): API key for Claude API
            metadata_path (str, optional): Path to metadata file
            output_dir (str, optional): Directory to save generated content
        """
        self.api_key = api_key
        self.metadata_path = metadata_path
        self.output_dir = output_dir
        self.metadata = None
        
        # Load metadata if path is provided
        if metadata_path:
            self.load_metadata(metadata_path)
    
    def load_metadata(self, metadata_path):
        """
        Load metadata from a file
        
        Args:
            metadata_path (str): Path to metadata file
            
        Returns:
            bool: True if metadata was loaded successfully, False otherwise
        """
        self.metadata = extract_metadata(metadata_path)
        return bool(self.metadata)
    
    def get_categories(self):
        """
        Get the list of categories from metadata
        
        Returns:
            list: List of category names
        """
        if not self.metadata:
            return []
        return get_categories(self.metadata)
    
    def get_items_in_category(self, category):
        """
        Get the list of items in a category
        
        Args:
            category (str): Category name
            
        Returns:
            list: List of items in the category
        """
        if not self.metadata:
            return []
        return get_items_in_category(self.metadata, category)
    
    def generate_from_metadata(self, category, item_index, include_examples=True, save=True):
        """
        Generate content from metadata
        
        Args:
            category (str): Category name
            item_index (int): Index of the item in the category
            include_examples (bool, optional): Whether to include examples in the prompt
            save (bool, optional): Whether to save the generated content to a file
            
        Returns:
            str: Generated content
        """
        if not self.metadata:
            print("No metadata loaded. Use load_metadata() first.")
            return None
        
        # Get the item from metadata
        item = get_item_by_index(self.metadata, category, item_index)
        if not item:
            print(f"Item not found at index {item_index} in category {category}")
            return None
        
        # Generate prompt
        prompt = generate_full_prompt(item, include_examples)
        
        # Generate content
        content = generate_content_with_claude(prompt, api_key=self.api_key)
        
        # Save content if requested
        if save:
            item_name = get_item_name(item)
            file_type = get_file_type(item)
            filename = f"{file_type}_{item_name.replace(' ', '_')}.md"
            write_file(content, filename, self.output_dir)
        
        return content
    
    def generate_from_topic(self, topic, file_type="lesson", learning_objectives=None, save=True):
        """
        Generate content from a topic
        
        Args:
            topic (str): Topic to generate content for
            file_type (str, optional): Type of file (e.g., 'lesson', 'lab')
            learning_objectives (list, optional): List of learning objectives
            save (bool, optional): Whether to save the generated content to a file
            
        Returns:
            str: Generated content
        """
        # Generate prompt
        prompt = generate_prompt_from_topic(topic, file_type, learning_objectives)
        
        # Generate content
        content = generate_content_with_claude(prompt, api_key=self.api_key)
        
        # Save content if requested
        if save:
            filename = f"{file_type}_{topic.replace(' ', '_')}.md"
            write_file(content, filename, self.output_dir)
        
        return content
