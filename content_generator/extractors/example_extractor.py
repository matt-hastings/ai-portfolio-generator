"""
Functions for extracting example content from files.
"""

from ..config import EXAMPLE_PATHS, TRUNCATE_EXAMPLE_LENGTH
from ..utils.file_utils import read_file

def get_example_path(file_type):
    """Get the path to an example file based on file type"""
    # Default to lesson if file_type not found
    return EXAMPLE_PATHS.get(file_type.lower(), EXAMPLE_PATHS.get('lesson'))

def extract_example_content(file_type=None, file_path=None):
    """
    Extract example content from a file
    
    Args:
        file_type (str, optional): Type of file to extract example from (e.g., 'lesson', 'lab')
        file_path (str, optional): Direct path to example file, overrides file_type
        
    Returns:
        str: The example content, truncated if necessary
    """
    # Determine the file path
    path = file_path if file_path else get_example_path(file_type)
    
    try:
        # Read the file content
        content = read_file(path)
        
        # Truncate if necessary
        if content and len(content) > TRUNCATE_EXAMPLE_LENGTH:
            content = content[:TRUNCATE_EXAMPLE_LENGTH] + "\n...\n[Example truncated for brevity]"
        
        return content or "Example content not available."
    except Exception as e:
        print(f"Error extracting example content from {path}: {e}")
        return "Example content not available."
