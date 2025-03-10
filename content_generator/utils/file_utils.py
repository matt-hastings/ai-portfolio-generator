"""
Utility functions for file operations.
"""

import os
import json
from pathlib import Path

def read_file(filepath):
    """Read content from a file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def read_json(filepath):
    """Read JSON data from a file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file {filepath}: {e}")
        return None

def write_file(content, filepath, output_dir=None):
    """Write content to a file with error handling"""
    try:
        # Handle output directory if provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filepath)
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        # Write content to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"Content saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")
        return None

def read_example_content(file_path, max_length=None):
    """Read example content from a file with truncation"""
    content = read_file(file_path)
    if content and max_length and len(content) > max_length:
        content = content[:max_length] + "\n...\n[Example truncated for brevity]"
    return content
