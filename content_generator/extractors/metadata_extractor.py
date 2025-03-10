"""
Functions for extracting and processing metadata.
"""

from ..config import DEFAULT_METADATA_PATH
from ..utils.file_utils import read_json

def extract_metadata(metadata_path=DEFAULT_METADATA_PATH):
    """
    Extract metadata from a JSON file
    
    Args:
        metadata_path (str): Path to the metadata JSON file
        
    Returns:
        dict: The metadata as a dictionary
    """
    metadata = read_json(metadata_path)
    if not metadata:
        print(f"Failed to load metadata from {metadata_path}")
        return {}
    
    print(f"Loaded metadata with {len(metadata)} categories")
    return metadata

def get_categories(metadata):
    """Get the list of categories from metadata"""
    return list(metadata.keys())

def get_items_in_category(metadata, category):
    """Get the list of items in a category"""
    if category in metadata:
        return metadata[category]
    return []

def get_item_by_index(metadata, category, index):
    """Get an item by its index in a category"""
    items = get_items_in_category(metadata, category)
    if 0 <= index < len(items):
        return items[index]
    return None

def get_item_name(item):
    """Get the name of an item (topic or course title)"""
    return item.get('topic', item.get('course_title', 'unnamed'))

def get_file_type(item):
    """Get the file type of an item"""
    return item.get('file_type', 'content').lower()

def get_learning_objectives(item):
    """Get the learning objectives of an item"""
    return item.get('learning_objectives', [])

def get_content_metrics(item):
    """Get the content metrics of an item"""
    return item.get('content_metrics', {})
