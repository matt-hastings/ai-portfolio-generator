# Content Generator

A modular, context-independent package for generating educational content using Claude API.

## Overview

This package provides tools for generating educational content such as lessons, labs, and course landing pages. It extracts data from exemplars, processes that data into a format that a language model can understand, and then creates content that looks similar to the exemplars but with new topics.

## Features

- **Metadata-based generation**: Generate content based on structured metadata
- **Topic-based generation**: Generate content from a topic and learning objectives
- **Format instructions**: Automatically generate format instructions based on content type
- **Example extraction**: Extract examples from existing content to guide generation
- **Content standards**: Apply consistent content standards across all generated content
- **Step-by-step guidance**: Include detailed step-by-step guidance in generated content
- **Command-line interface**: Easy-to-use CLI for generating content
- **Programmatic API**: Flexible API for integration into other applications

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd content-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Create a `.env` file in the root directory
   - Add your Claude API key: `ANTHROPIC_API_KEY=your-api-key`

## Usage

### Command-line Interface

Generate content from a topic:

```bash
python -m content_generator.cli --topic "React Hooks" --type lesson
```

Generate content from metadata:

```bash
python -m content_generator.cli --category "GA_Lesson_Examples" --item 0
```

List available categories in metadata:

```bash
python -m content_generator.cli --list-categories
```

List items in a category:

```bash
python -m content_generator.cli --list-items "GA_Lesson_Examples"
```

### Python API

```python
from content_generator import ContentGenerator

# Initialize the generator
generator = ContentGenerator()

# Generate content from a topic
content = generator.generate_from_topic(
    topic="Python List Comprehensions",
    file_type="lesson",
    learning_objectives=[
        "Understand the syntax of list comprehensions",
        "Compare list comprehensions to traditional loops",
        "Apply list comprehensions to solve real-world problems"
    ]
)

# Generate content from metadata
generator = ContentGenerator(metadata_path='sample_content/content_metadata')
content = generator.generate_from_metadata("GA_Lesson_Examples", 0)
```

See `example.py` for more detailed examples.

## Package Structure

```
content_generator/
├── __init__.py           # Main package entry point
├── config.py             # Configuration settings
├── cli.py                # Command-line interface
├── example.py            # Example usage
├── extractors/           # Data extraction modules
│   ├── __init__.py
│   ├── metadata_extractor.py
│   └── example_extractor.py
├── generators/           # Content generation modules
│   ├── __init__.py
│   ├── prompt_generator.py
│   └── format_generator.py
└── utils/                # Utility functions
    ├── __init__.py
    ├── file_utils.py
    └── api_utils.py
```

## Customization

### Custom Metadata

You can create your own metadata file following the structure in `sample_content/content_metadata`. The metadata file should be a JSON file with categories and items.

### Custom Examples

You can customize the example paths in `config.py` to use your own examples for different content types.

### Custom Format Instructions

You can modify the format instructions in `generators/format_generator.py` to match your specific formatting requirements.

## License

[MIT License](LICENSE)
