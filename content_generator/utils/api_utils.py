"""
Utility functions for API interactions.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from ..config import DEFAULT_MODEL, DEFAULT_MAX_TOKENS

def get_api_key():
    """Get API key from environment variables or .env file"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: No ANTHROPIC_API_KEY found in environment variables or .env file.")
        return None
    
    print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
    return api_key

def initialize_client(api_key=None):
    """Initialize the Anthropic client"""
    if not api_key:
        api_key = get_api_key()
        if not api_key:
            return None
    
    return Anthropic(api_key=api_key)

def generate_content_with_claude(prompt, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS, api_key=None):
    """Generate content using Claude API"""
    client = initialize_client(api_key)
    if not client:
        return "Error: Could not initialize Anthropic client."
    
    try:
        # Create a message using the specified model
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Return the generated content
        return message.content[0].text
    except Exception as e:
        return f"Error generating content: {str(e)}"
