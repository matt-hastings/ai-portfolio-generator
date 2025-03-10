"""
Configuration settings for the content generator package.
"""

import os
from pathlib import Path

# Default paths
DEFAULT_METADATA_PATH = 'sample_content/content_metadata'
DEFAULT_OUTPUT_DIR = 'generated_content'

# Example content paths by file type
EXAMPLE_PATHS = {
    'lesson': 'sample_content/GA Lesson Examples/ikea-app-and-gcp-deploy-content-main/build-express-app.md',
    'lab': 'sample_content/GA Lab Examples/lifting-state-in-react-lab-main/exercise/README.md'
}

# API settings
DEFAULT_MODEL = "claude-3-sonnet-20240229"
DEFAULT_MAX_TOKENS = 4000

# File settings
TRUNCATE_EXAMPLE_LENGTH = 2000
