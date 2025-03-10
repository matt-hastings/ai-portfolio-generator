#!/usr/bin/env python3
"""
Test script to verify that the Content Generator package works correctly.
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from content_generator import ContentGenerator
from content_generator.generators.prompt_generator import generate_prompt_from_topic
from content_generator.extractors.example_extractor import extract_example_content
from content_generator.generators.format_generator import generate_format_instructions

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports... ", end="")
    try:
        # Try importing all modules
        from content_generator import ContentGenerator
        from content_generator.extractors import example_extractor, metadata_extractor
        from content_generator.generators import format_generator, prompt_generator
        from content_generator.utils import api_utils, file_utils
        print("OK")
        return True
    except ImportError as e:
        print(f"FAILED: {e}")
        return False

def test_prompt_generation():
    """Test prompt generation"""
    print("Testing prompt generation... ", end="")
    try:
        # Generate a prompt from a topic
        topic = "Test Topic"
        prompt = generate_prompt_from_topic(topic)
        
        # Check that the prompt contains the topic
        if topic in prompt:
            print("OK")
            return True
        else:
            print(f"FAILED: Topic '{topic}' not found in prompt")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_example_extraction():
    """Test example extraction"""
    print("Testing example extraction... ", end="")
    try:
        # Extract example content
        example = extract_example_content("lesson")
        
        # Check that example content is not empty
        if example and len(example) > 0:
            print("OK")
            return True
        else:
            print("FAILED: Example content is empty")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_format_instructions():
    """Test format instructions generation"""
    print("Testing format instructions generation... ", end="")
    try:
        # Generate format instructions
        instructions = generate_format_instructions("lesson")
        
        # Check that instructions are not empty
        if instructions and len(instructions) > 0:
            print("OK")
            return True
        else:
            print("FAILED: Format instructions are empty")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("Content Generator Package Tests")
    print("==============================\n")
    
    # Run tests
    tests = [
        test_imports,
        test_prompt_generation,
        test_example_extraction,
        test_format_instructions
    ]
    
    # Count successes
    successes = sum(1 for test in tests if test())
    
    # Print summary
    print(f"\n{successes}/{len(tests)} tests passed")
    
    # Return success status
    return successes == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
