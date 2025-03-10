"""
Functions for generating prompts based on metadata and format instructions.
"""

from ..extractors.example_extractor import extract_example_content
from ..extractors.metadata_extractor import (
    get_file_type, get_item_name, get_learning_objectives, get_content_metrics
)
from .format_generator import (
    generate_format_instructions, generate_content_standards, generate_step_by_step_guidance
)

def generate_basic_prompt(item):
    """
    Generate a basic prompt based on metadata
    
    Args:
        item (dict): Metadata item
        
    Returns:
        str: Basic prompt
    """
    file_type = get_file_type(item)
    
    # Handle different content types
    if file_type == 'course_landing':
        # For course landing pages, use course_title instead of topic
        basic_prompt = f"Generate a {file_type} for {item['course_title']}. Course description: {item['course_description']}"
        
        # For course landing pages, use learning_path instead of learning_objectives if available
        if 'learning_path' in item:
            basic_prompt += f". Learning path: {', '.join(item['learning_path'])}"
    else:
        # For other content types, use topic and learning_objectives
        learning_objectives = get_learning_objectives(item)
        topic = get_item_name(item)
        basic_prompt = f"Generate a {file_type} on {topic}. Learning objectives: {', '.join(learning_objectives)}"
    
    return basic_prompt

def generate_metrics_prompt(item):
    """
    Generate a prompt section for content metrics
    
    Args:
        item (dict): Metadata item
        
    Returns:
        str: Metrics prompt section
    """
    metrics = get_content_metrics(item)
    if not metrics:
        return ""
    
    return (
        f"The content should be approximately {metrics.get('word_count', 500)} words with a "
        f"text-to-code ratio of {metrics.get('text_to_code_ratio', 0.7)}. "
        f"Include {metrics.get('number_of_images', 1)} images and {metrics.get('number_of_diagrams', 1)} diagrams."
    )

def generate_example_prompt(file_type):
    """
    Generate a prompt section with example content
    
    Args:
        file_type (str): Type of file
        
    Returns:
        str: Example prompt section
    """
    example_content = extract_example_content(file_type)
    
    return f"""
EXAMPLE STRUCTURE:
The following is an example of how the content should be structured and formatted:

{example_content}

Your generated content should follow a similar structure and formatting style.
"""

def generate_full_prompt(item, include_examples=True):
    """
    Generate a full prompt based on metadata
    
    Args:
        item (dict): Metadata item
        include_examples (bool): Whether to include example content
        
    Returns:
        str: Full prompt
    """
    file_type = get_file_type(item)
    
    # Basic prompt
    basic_prompt = generate_basic_prompt(item)
    
    # Metrics prompt
    metrics_prompt = generate_metrics_prompt(item)
    
    # Format instructions
    format_prompt = generate_format_instructions(file_type)
    
    # Content standards
    standards_prompt = generate_content_standards()
    
    # Step-by-step guidance
    step_by_step_prompt = generate_step_by_step_guidance()
    
    # Example content
    example_prompt = generate_example_prompt(file_type) if include_examples else ""
    
    # Combine all prompt components
    full_prompt = f"""
{basic_prompt}

{metrics_prompt}

{format_prompt}

{standards_prompt}

{step_by_step_prompt}

{example_prompt}

Please generate complete, well-structured content that follows all the guidelines above.
""".strip()
    
    return full_prompt

def generate_prompt_from_topic(topic, file_type="lesson", learning_objectives=None):
    """
    Generate a prompt from a topic without metadata
    
    Args:
        topic (str): Topic to generate content for
        file_type (str): Type of file (e.g., 'lesson', 'lab')
        learning_objectives (list): List of learning objectives
        
    Returns:
        str: Full prompt
    """
    if learning_objectives is None:
        learning_objectives = [
            f"Understand the core concepts of {topic}",
            f"Implement basic {topic} functionality",
            f"Debug common issues with {topic}"
        ]
    
    # Create a minimal metadata item
    item = {
        'topic': topic,
        'file_type': file_type,
        'learning_objectives': learning_objectives,
        'content_metrics': {
            'word_count': 1000,
            'text_to_code_ratio': 0.7,
            'number_of_images': 2,
            'number_of_diagrams': 1
        }
    }
    
    return generate_full_prompt(item)
