# AI Portfolio Content Builder

A tool for generating AI training portfolio content based on exemplars.

## Project Structure

- `content_generator/`: Main Python package
  - `extractors/`: Modules for extracting metadata and content from exemplars
  - `generators/`: Modules for generating formatted content and prompts
  - `utils/`: Utility functions for file operations and API interactions
- `Exemplars/`: Collection of training materials used as reference

## Getting Started

1. Install the required dependencies:
   ```
   pip install -r content_generator/requirements.txt
   ```

2. Run the package:
   ```
   python -m content_generator.cli
   ```

## Features

- Extract metadata from training materials
- Generate formatted content based on exemplars
- Create prompts for AI-assisted content generation
