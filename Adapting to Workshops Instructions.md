# Adapting Content Generator for Workshop Materials

This guide outlines how to adapt your existing LLM-powered content generation pipeline to handle workshop materials. The enhanced approach focuses on preserving formatting, maintaining learning experience patterns, and integrating with Google Workspace.

## 1. Project Structure: Enhanced Workshop Module

Create a new subdirectory within your existing content_generator to house the workshop-specific code:

```
content_generator/
├── lessons/          # Existing markdown-based generator
│   ├── extractors/
│   ├── format_generator.py
│   ├── prompt_generator.py
│   └── ...
├── workshops/        # NEW workshop-based generator
│   ├── extractors/
│   │   ├── metadata_extractor.py
│   │   ├── example_extractor.py
│   │   ├── format_extractor.py      # NEW: Extracts formatting information
│   │   └── learning_pattern_extractor.py  # NEW: Analyzes learning patterns
│   ├── generators/
│   │   ├── format_generator.py
│   │   ├── prompt_generator.py
│   │   └── output_generator.py      # NEW: Generates formatted output files
│   └── google_integration/          # NEW: Google Workspace integration
│       ├── auth.py
│       ├── slides_api.py
│       ├── docs_api.py
│       └── sheets_api.py
├── utils/
│   ├── file_utils.py                # Needs modification
│   └── google_utils.py              # NEW: Google API utilities
└── config.py                        # Needs modification
```

## 2. Core Components and Modifications

### 2.1. config.py

Update the configuration to include workshop-specific settings:

```python
# Example paths
EXAMPLE_PATHS = {
    'lesson': '/path/to/example_lesson.md',  # Existing
    'lab': '/path/to/example_lab.md',        # Existing
    'workshop': '/path/to/example_workshop_directory' # NEW
}

# Workshop-specific configurations
ACCEPTED_WORKSHOP_FILE_TYPES = ['.pptx', '.docx', '.xlsx']
GOOGLE_WORKSPACE_ENABLED = True  # Enable Google Workspace integration
GOOGLE_API_CREDENTIALS_PATH = 'path/to/credentials.json'
PRESERVE_FORMATTING = True  # Enable format preservation
```

### 2.2. utils/file_utils.py

Extend file utilities to handle both Office formats and Google Workspace formats:

```python
import os
import pptx
import docx
import openpyxl

def read_file(filepath):
    """Read content from a file with format-specific handling."""
    file_extension = filepath.split('.')[-1].lower()

    if file_extension == 'pptx':
        try:
            prs = pptx.Presentation(filepath)
            text = []
            for slide_index, slide in enumerate(prs.slides):
                slide_text = [f"--- Slide {slide_index + 1} ---"]
                # Extract slide title if available
                if slide.shapes.title and slide.shapes.title.text:
                    slide_text.append(f"Title: {slide.shapes.title.text}")
                
                # Extract text from all shapes
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        slide_text.append(shape.text)
                
                # Extract notes if available
                if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text:
                    slide_text.append(f"Notes: {slide.notes_slide.notes_text_frame.text}")
                
                text.append("\n".join(slide_text))
            return "\n\n".join(text)
        except Exception as e:
            print(f"Error reading PPTX file: {e}")
            return None

    elif file_extension == 'docx':
        try:
            doc = docx.Document(filepath)
            text = []
            
            # Extract document structure with heading levels
            for paragraph in doc.paragraphs:
                if paragraph.style.name.startswith('Heading'):
                    level = paragraph.style.name.replace('Heading', '')
                    text.append(f"{'#' * int(level)} {paragraph.text}")
                else:
                    text.append(paragraph.text)
            
            # Extract tables
            for table in doc.tables:
                text.append("--- Table ---")
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        row_text.append(cell.text)
                    text.append(" | ".join(row_text))
            
            return "\n".join(text)
        except Exception as e:
            print(f"Error reading DOCX file: {e}")
            return None

    elif file_extension == 'xlsx':
        try:
            workbook = openpyxl.load_workbook(filepath)
            text = []
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                text.append(f"--- Sheet: {sheet_name} ---")
                
                # Extract headers (first row)
                headers = []
                for cell in sheet[1]:
                    headers.append(str(cell.value) if cell.value is not None else "")
                text.append("Headers: " + " | ".join(headers))
                
                # Extract data rows
                for row_idx, row in enumerate(sheet.iter_rows(min_row=2)):
                    row_data = []
                    for cell in row:
                        row_data.append(str(cell.value) if cell.value is not None else "")
                    text.append(f"Row {row_idx + 1}: " + " | ".join(row_data))
            
            return "\n\n".join(text)
        except Exception as e:
            print(f"Error reading XLSX file: {e}")
            return None
    else:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

def list_files(directory, extensions):
    """Lists files in a directory with specified extensions."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

def extract_file_metadata(filepath):
    """Extract metadata about a file including creation date, size, etc."""
    try:
        stats = os.stat(filepath)
        return {
            'path': filepath,
            'filename': os.path.basename(filepath),
            'size': stats.st_size,
            'created': stats.st_ctime,
            'modified': stats.st_mtime,
            'extension': os.path.splitext(filepath)[1].lower()
        }
    except Exception as e:
        print(f"Error extracting file metadata: {e}")
        return None
```

### 2.3. utils/google_utils.py

Add utilities for Google Workspace integration:

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Define scopes needed for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

def get_google_credentials(credentials_path, token_path='token.pickle'):
    """Get Google API credentials, refreshing if necessary."""
    creds = None
    
    # Check if token.pickle exists
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials don't exist or are invalid, refresh or get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_slides_service(credentials):
    """Get Google Slides API service."""
    return build('slides', 'v1', credentials=credentials)

def get_docs_service(credentials):
    """Get Google Docs API service."""
    return build('docs', 'v1', credentials=credentials)

def get_sheets_service(credentials):
    """Get Google Sheets API service."""
    return build('sheets', 'v4', credentials=credentials)

def get_drive_service(credentials):
    """Get Google Drive API service."""
    return build('drive', 'v3', credentials=credentials)
```

### 2.4. workshops/extractors/metadata_extractor.py

Enhance the metadata extractor to extract comprehensive information from workshop files:

```python
import os
from ...utils.file_utils import list_files, read_file, extract_file_metadata
from ...config import ACCEPTED_WORKSHOP_FILE_TYPES

def extract_metadata(workshop_directory):
    """Extract comprehensive metadata from a workshop directory."""
    metadata = {
        'workshop_name': os.path.basename(workshop_directory),
        'files': {},
        'presentation': {},
        'instructor_guide': {},
        'pacing_guide': {},
        'learning_objectives': [],
        'target_audience': '',
        'duration': '',
        'content_structure': {}
    }
    
    # Get all relevant files
    files = list_files(workshop_directory, ACCEPTED_WORKSHOP_FILE_TYPES)
    
    # Process each file based on type
    for filepath in files:
        file_meta = extract_file_metadata(filepath)
        if not file_meta:
            continue
            
        file_extension = file_meta['extension']
        filename = file_meta['filename'].lower()
        
        # Store file metadata
        metadata['files'][filepath] = file_meta
        
        # Process based on file type
        if file_extension == '.pptx':
            # Assume this is the main presentation
            content = read_file(filepath)
            if content:
                metadata['presentation'][filepath] = {
                    'content': content,
                    'slide_count': content.count('--- Slide'),
                    'has_notes': content.count('Notes:') > 0
                }
                
                # Try to extract workshop name from first slide title
                if 'Title:' in content:
                    first_title = content.split('Title:')[1].split('\n')[0].strip()
                    if first_title:
                        metadata['workshop_name'] = first_title
        
        elif file_extension == '.docx':
            content = read_file(filepath)
            if content:
                # Check if this is an instructor guide
                if 'instructor' in filename or 'guide' in filename:
                    metadata['instructor_guide'][filepath] = {
                        'content': content
                    }
                    
                    # Try to extract learning objectives
                    if 'learning objectives' in content.lower() or 'objectives' in content.lower():
                        # Simple extraction - can be improved with regex
                        sections = content.lower().split('objectives')
                        if len(sections) > 1:
                            objectives_section = sections[1].split('#')[0]  # Get text until next heading
                            objectives = [obj.strip() for obj in objectives_section.split('\n') if obj.strip()]
                            metadata['learning_objectives'].extend(objectives)
                    
                    # Try to extract target audience
                    if 'audience' in content.lower() or 'participants' in content.lower():
                        sections = content.lower().split('audience')
                        if len(sections) > 1:
                            audience_section = sections[1].split('#')[0]
                            metadata['target_audience'] = audience_section.strip()
        
        elif file_extension == '.xlsx':
            content = read_file(filepath)
            if content:
                # Check if this is a pacing guide
                if 'schedule' in filename or 'pacing' in filename or 'guide' in filename:
                    metadata['pacing_guide'][filepath] = {
                        'content': content
                    }
                    
                    # Try to extract duration
                    if 'duration' in content.lower() or 'time' in content.lower():
                        # Simple extraction - can be improved
                        metadata['duration'] = "Extracted from pacing guide"
    
    return metadata

def get_item_name(item):
    """Get the name of a workshop item."""
    return item.get('workshop_name', 'Unnamed Workshop')

def get_file_type(item):
    """Get the file type of a workshop item."""
    return 'workshop'

def get_learning_objectives(item):
    """Get the learning objectives of a workshop item."""
    return item.get('learning_objectives', [])

def get_content_metrics(item):
    """Get the content metrics of a workshop item."""
    presentation_files = item.get('presentation', {})
    
    metrics = {
        'slide_count': sum(data.get('slide_count', 0) for data in presentation_files.values()),
        'has_instructor_guide': bool(item.get('instructor_guide')),
        'has_pacing_guide': bool(item.get('pacing_guide')),
        'duration': item.get('duration', 'Unknown')
    }
    
    return metrics
```

### 2.5. workshops/extractors/format_extractor.py

Add a new extractor specifically for formatting information:

```python
import pptx
import os
from ...utils.file_utils import list_files

def extract_slide_layouts(pptx_file):
    """Extract slide layout information from a PowerPoint file."""
    try:
        presentation = pptx.Presentation(pptx_file)
        layouts = {}
        
        # Extract master slide layouts
        for master in presentation.slide_masters:
            master_layouts = {}
            for layout in master.slide_layouts:
                layout_info = {
                    'name': layout.name,
                    'placeholder_count': len(layout.placeholders),
                    'placeholders': [{'idx': p.idx, 'type': p.placeholder_format.type} 
                                    for p in layout.placeholders]
                }
                master_layouts[layout.name] = layout_info
            
            layouts[master.name] = master_layouts
        
        # Extract slide layout usage
        slide_layouts = []
        for i, slide in enumerate(presentation.slides):
            layout_name = slide.slide_layout.name
            slide_layouts.append({
                'slide_index': i,
                'layout_name': layout_name
            })
        
        return {
            'master_layouts': layouts,
            'slide_layouts': slide_layouts
        }
    except Exception as e:
        print(f"Error extracting slide layouts: {e}")
        return None

def extract_slide_formatting(pptx_file):
    """Extract detailed formatting information from slides."""
    try:
        presentation = pptx.Presentation(pptx_file)
        formatting = []
        
        for i, slide in enumerate(presentation.slides):
            slide_format = {
                'slide_index': i,
                'layout_name': slide.slide_layout.name,
                'shapes': []
            }
            
            for shape in slide.shapes:
                shape_info = {
                    'name': shape.name,
                    'type': shape.shape_type,
                }
                
                # Extract text formatting if available
                if hasattr(shape, "text") and shape.text:
                    text_frame = shape.text_frame
                    paragraphs = []
                    
                    for paragraph in text_frame.paragraphs:
                        para_info = {
                            'text': paragraph.text,
                            'alignment': paragraph.alignment if hasattr(paragraph, 'alignment') else None,
                            'level': paragraph.level,
                            'runs': []
                        }
                        
                        for run in paragraph.runs:
                            run_info = {
                                'text': run.text,
                                'bold': run.font.bold,
                                'italic': run.font.italic,
                                'underline': run.font.underline,
                                'font_name': run.font.name,
                                'size': run.font.size.pt if run.font.size else None,
                                'color': str(run.font.color.rgb) if run.font.color and run.font.color.rgb else None
                            }
                            para_info['runs'].append(run_info)
                        
                        paragraphs.append(para_info)
                    
                    shape_info['paragraphs'] = paragraphs
                
                slide_format['shapes'].append(shape_info)
            
            formatting.append(slide_format)
        
        return formatting
    except Exception as e:
        print(f"Error extracting slide formatting: {e}")
        return None

def extract_formatting(workshop_directory):
    """Extract formatting information from all presentation files in a workshop."""
    formatting_data = {}
    pptx_files = list_files(workshop_directory, ['.pptx'])
    
    for pptx_file in pptx_files:
        file_name = os.path.basename(pptx_file)
        formatting_data[file_name] = {
            'layouts': extract_slide_layouts(pptx_file),
            'formatting': extract_slide_formatting(pptx_file)
        }
    
    return formatting_data
```

### 2.6. workshops/extractors/learning_pattern_extractor.py

Add a new extractor for learning patterns:

```python
import re
import os
from ...utils.file_utils import read_file, list_files

def identify_slide_types(slide_content):
    """Identify the type of slide based on its content."""
    slide_type = "unknown"
    
    # Define patterns for different slide types
    patterns = {
        'title': r'Title Slide|Cover|Introduction',
        'agenda': r'Agenda|Overview|Outline|Schedule',
        'learning_objectives': r'Learning Objectives|Objectives|Goals',
        'concept': r'Concept|Definition|Theory|Overview',
        'example': r'Example|Case Study|Demonstration',
        'activity': r'Activity|Exercise|Practice|Try it|Your turn',
        'discussion': r'Discussion|Reflect|Think about|Consider',
        'assessment': r'Quiz|Test|Check|Assessment|Knowledge Check',
        'summary': r'Summary|Recap|Review|Key Takeaways',
        'resources': r'Resources|References|Further Reading|Learn More'
    }
    
    # Check each pattern
    for type_name, pattern in patterns.items():
        if re.search(pattern, slide_content, re.IGNORECASE):
            slide_type = type_name
            break
    
    return slide_type

def extract_learning_patterns(workshop_directory):
    """Extract learning patterns from workshop materials."""
    patterns = {
        'slide_sequence': [],
        'activity_distribution': {},
        'learning_flow': {},
        'timing_allocation': {},
        'question_patterns': [],
        'assessment_strategies': []
    }
    
    # Process PowerPoint files for slide sequence
    pptx_files = list_files(workshop_directory, ['.pptx'])
    for pptx_file in pptx_files:
        content = read_file(pptx_file)
        if not content:
            continue
        
        # Split content by slides
        slides = content.split('--- Slide')
        
        # Process each slide
        for i, slide in enumerate(slides[1:], 1):  # Skip the first split which is empty
            slide_type = identify_slide_types(slide)
            patterns['slide_sequence'].append({
                'index': i,
                'type': slide_type,
                'file': os.path.basename(pptx_file)
            })
            
            # Count slide types for activity distribution
            if slide_type not in patterns['activity_distribution']:
                patterns['activity_distribution'][slide_type] = 0
            patterns['activity_distribution'][slide_type] += 1
            
            # Extract questions
            if '?' in slide:
                questions = re.findall(r'[A-Z][^.!?]*\?', slide)
                for question in questions:
                    patterns['question_patterns'].append({
                        'slide_index': i,
                        'question': question.strip(),
                        'type': 'discussion' if slide_type == 'discussion' else 'knowledge_check'
                    })
    
    # Process Excel files for timing allocation
    xlsx_files = list_files(workshop_directory, ['.xlsx'])
    for xlsx_file in xlsx_files:
        if 'schedule' in xlsx_file.lower() or 'pacing' in xlsx_file.lower():
            content = read_file(xlsx_file)
            if not content:
                continue
            
            # Extract timing information (simplified)
            timing_rows = [line for line in content.split('\n') if 'Row' in line]
            for row in timing_rows:
                # Simple parsing - can be improved
                cells = row.split('|')
                if len(cells) >= 3:  # Assuming at least activity and duration columns
                    activity = cells[1].strip()
                    duration = cells[2].strip()
                    if activity and duration:
                        patterns['timing_allocation'][activity] = duration
    
    # Analyze learning flow
    if patterns['slide_sequence']:
        # Identify common sequences (e.g., concept -> example -> activity)
        sequence_length = 3
        for i in range(len(patterns['slide_sequence']) - sequence_length + 1):
            sequence = [patterns['slide_sequence'][i+j]['type'] for j in range(sequence_length)]
            sequence_key = ' -> '.join(sequence)
            
            if sequence_key not in patterns['learning_flow']:
                patterns['learning_flow'][sequence_key] = 0
            patterns['learning_flow'][sequence_key] += 1
    
    return patterns
```

### 2.7. workshops/extractors/example_extractor.py

Enhance the example extractor to include formatting and learning patterns:

```python
import os
from ...config import EXAMPLE_PATHS, ACCEPTED_WORKSHOP_FILE_TYPES
from ...utils.file_utils import list_files, read_file
from .format_extractor import extract_formatting
from .learning_pattern_extractor import extract_learning_patterns

def extract_example_content(file_type='workshop', file_path=None):
    """Extract comprehensive example content from a workshop directory."""
    if not file_path:
        file_path = EXAMPLE_PATHS.get(file_type.lower())
    if not file_path:
        return "Example workshop path not found in configuration."

    try:
        # Extract text content from all files
        all_text = []
        files = list_files(file_path, ACCEPTED_WORKSHOP_FILE_TYPES)
        for filepath in files:
            content = read_file(filepath)
            if content:
                all_text.append(f"---[Content from: {os.path.basename(filepath)}]---\n{content}")
        
        text_content = "\n\n".join(all_text)
        
        # Extract formatting information if enabled
        from ...config import PRESERVE_FORMATTING
        formatting_data = {}
        if PRESERVE_FORMATTING:
            formatting_data = extract_formatting(file_path)
        
        # Extract learning patterns
        learning_patterns = extract_learning_patterns(file_path)
        
        return {
            'text_content': text_content,
            'formatting': formatting_data,
            'learning_patterns': learning_patterns
        }
    except Exception as e:
        print(f"Error extracting example content from workshop: {e}")
        return "Example content not available."
```

### 2.8. workshops/generators/format_generator.py

Enhance the format generator to include detailed formatting instructions:

```python
def generate_format_instructions(file_type, formatting_data=None, learning_patterns=None):
    """Generate format instructions based on file type and extracted formatting."""
    if file_type != 'workshop':
        # Use existing format instructions for non-workshop types
        return generate_default_format_instructions(file_type)
    
    # Generate workshop-specific format instructions
    instructions = """
FORMAT STRUCTURE:
- The workshop should include a PowerPoint presentation, instructor guide, and pacing guide.
- The PowerPoint presentation should cover the core concepts.
- The instructor guide should provide detailed instructions and activities.
- The pacing guide should outline the schedule and timing of each activity.
"""
    
    # Add formatting-specific instructions if available
    if formatting_data:
        slide_layout_instructions = generate_slide_layout_instructions(formatting_data)
        instructions += f"\n{slide_layout_instructions}"
    
    # Add learning pattern instructions if available
    if learning_patterns:
        pattern_instructions = generate_learning_pattern_instructions(learning_patterns)
        instructions += f"\n{pattern_instructions}"
    
    return instructions

def generate_default_format_instructions(file_type):
    """Generate default format instructions for non-workshop file types."""
    # Original implementation for lessons, labs, etc.
    if file_type == 'lesson':
        return """
FORMAT STRUCTURE:
- Begin with: <h1>
  <span class="headline">[MAIN TITLE]</span>
  <span class="subhead">[SUBTITLE]</span>
</h1>
- Include the GA logo at the top: ![](https://ga-dash.s3.amazonaws.com/production/assets/logo-9f88ae6c9c3871690e33280fcf557f33.png)
- Include a metadata table with: Title, Type, Duration, Author
- Format learning objectives as: **Learning objective:** By the end of this lesson, students will [OBJECTIVES]
- Use proper heading hierarchy (h1, h2, h3)
- Format notes as: > 📚 *[NOTE TEXT]*
- Include code blocks with proper syntax highlighting
- Use bullet points for lists
- Include diagrams and images with proper captions
- Number steps explicitly (e.g., "Step 1:", "Step 2:")
- Include "Try it out" sections after each major step
- Add instructor notes about potential confusion points
- Include timing estimates for each section
- Add "Why This Matters" sections connecting concepts to job skills
"""
    # Add other file types as needed
    return """
FORMAT STRUCTURE:
- Use proper formatting
- Include clear headings and subheadings
- Format examples with proper syntax highlighting
- Include diagrams and images where appropriate
"""

def generate_slide_layout_instructions(formatting_data):
    """Generate instructions for slide layouts based on extracted formatting."""
    instructions = """
SLIDE FORMATTING:
- Maintain consistent slide layouts throughout the presentation
- Use the following slide types and layouts:
"""
    
    # Extract layout information from formatting data
    for file_name, data in formatting_data.items():
        if 'layouts' in data and data['layouts']:
            instructions += f"\nFor {file_name}:\n"
            
            # Add master layout information
            if 'master_layouts' in data['layouts']:
                for master_name, layouts in data['layouts']['master_layouts'].items():
                    instructions += f"- Master: {master_name}\n"
                    for layout_name, layout_info in layouts.items():
                        instructions += f"  - Layout: {layout_name} ({layout_info['placeholder_count']} placeholders)\n"
            
            # Add slide layout sequence
            if 'slide_layouts' in data['layouts'] and data['layouts']['slide_layouts']:
                instructions += "\nSlide Layout Sequence:\n"
                layout_counts = {}
                for slide in data['layouts']['slide_layouts']:
                    layout_name = slide['layout_name']
                    if layout_name not in layout_counts:
                        layout_counts[layout_name] = 0
                    layout_counts[layout_name] += 1
                
                for layout_name, count in layout_counts.items():
                    instructions += f"- {layout_name}: {count} slides\n"
    
    # Add text formatting guidelines
    instructions += """
TEXT FORMATTING:
- Use consistent fonts throughout the presentation
- Maintain consistent text sizes for titles, subtitles, and body text
- Use bullet points for lists
- Use consistent color schemes for emphasis
"""
    
    return instructions

def generate_learning_pattern_instructions(learning_patterns):
    """Generate instructions based on extracted learning patterns."""
    instructions = """
LEARNING EXPERIENCE PATTERNS:
"""
    
    # Add slide sequence patterns
    if 'slide_sequence' in learning_patterns:
        # Analyze the sequence to find patterns
        slide_types = [slide['type'] for slide in learning_patterns['slide_sequence']]
        unique_types = set(slide_types)
        
        instructions += "- Use the following slide types in your presentation:\n"
        for slide_type in unique_types:
            count = slide_types.count(slide_type)
            instructions += f"  - {slide_type.capitalize()} slides: {count}\n"
    
    # Add activity distribution
    if 'activity_distribution' in learning_patterns:
        instructions += "\n- Distribute activities as follows:\n"
        for activity_type, count in learning_patterns['activity_distribution'].items():
            instructions += f"  - {activity_type.capitalize()}: {count}\n"
    
    # Add learning flow patterns
    if 'learning_flow' in learning_patterns:
        instructions += "\n- Follow these learning sequences:\n"
        for sequence, count in learning_patterns['learning_flow'].items():
            instructions += f"  - {sequence}: {count} occurrences\n"
    
    # Add timing allocation
    if 'timing_allocation' in learning_patterns:
        instructions += "\n- Allocate time as follows:\n"
        for activity, duration in learning_patterns['timing_allocation'].items():
            instructions += f"  - {activity}: {duration}\n"
    
    # Add question patterns
    if 'question_patterns' in learning_patterns:
        instructions += "\n- Include the following types of questions:\n"
        question_types = {}
        for question in learning_patterns['question_patterns']:
            q_type = question['type']
            if q_type not in question_types:
                question_types[q_type] = 0
            question_types[q_type] += 1
        
        for q_type, count in question_types.items():
            instructions += f"  - {q_type.capitalize()} questions: {count}\n"
    
    return instructions
```

### 2.9. workshops/generators/prompt_generator.py

Enhance the prompt generator to include formatting and learning pattern information:

```python
from ..extractors.example_extractor import extract_example_content
from ..extractors.metadata_extractor import (
    get_file_type, get_item_name, get_learning_objectives, get_content_metrics
)
from .format_generator import generate_format_instructions
from ...config import PRESERVE_FORMATTING

def generate_basic_prompt(item):
    """Generate a basic prompt for workshop content."""
    file_type = get_file_type(item)
    workshop_name = get_item_name(item)
    learning_objectives = get_learning_objectives(item)
    
    basic_prompt = f"Generate a {file_type} on {workshop_name}."
    
    if learning_objectives:
        basic_prompt += f" Learning objectives: {', '.join(learning_objectives)}"
    
    if 'target_audience' in item and item['target_audience']:
        basic_prompt += f" Target audience: {item['target_audience']}"
    
    if 'duration' in item and item['duration']:
        basic_prompt += f" Duration: {item['duration']}"
    
    return basic_prompt

def generate_metrics_prompt(item):
    """Generate a prompt section for content metrics."""
    metrics = get_content_metrics(item)
    if not metrics:
        return ""
    
    metrics_prompt = "The workshop should include:"
    
    if 'slide_count' in metrics:
        metrics_prompt += f" Approximately {metrics['slide_count']} slides in the presentation."
    
    if 'has_instructor_guide' in metrics and metrics['has_instructor_guide']:
        metrics_prompt += " A comprehensive instructor guide with detailed instructions."
    
    if 'has_pacing_guide' in metrics and metrics['has_pacing_guide']:
        metrics_prompt += " A pacing guide with timing for each activity."
    
    return metrics_prompt

def generate_example_prompt(file_type, example_content):
    """Generate a prompt section with example content."""
    if not example_content or isinstance(example_content, str):
        return ""
    
    # Extract text content
    text_content = example_content.get('text_content', '')
    
    example_prompt = f"""
EXAMPLE STRUCTURE:
The following is an example of how the content should be structured and formatted:

{text_content}

Your generated content should follow a similar structure and formatting style.
"""
    
    return example_prompt

def generate_formatting_prompt(example_content):
    """Generate a prompt section for formatting instructions."""
    if not example_content or isinstance(example_content, str):
        return ""
    
    formatting_data = example_content.get('formatting', {})
    learning_patterns = example_content.get('learning_patterns', {})
    
    if not formatting_data and not learning_patterns:
        return ""
    
    formatting_prompt = """
FORMATTING INSTRUCTIONS:
Your content should maintain the same visual style and formatting as the example:
"""
    
    # Add specific formatting instructions based on extracted data
    if formatting_data:
        for file_name, data in formatting_data.items():
            if 'layouts' in data and data['layouts'] and 'master_layouts' in data['layouts']:
                formatting_prompt += f"\n- For {file_name}, use the following slide layouts:\n"
                for master_name, layouts in data['layouts']['master_layouts'].items():
                    for layout_name, layout_info in layouts.items():
                        formatting_prompt += f"  - {layout_name} layout for appropriate content\n"
    
    # Add learning pattern instructions
    if learning_patterns:
        formatting_prompt += "\n- Follow these learning patterns:\n"
        
        if 'learning_flow' in learning_patterns:
            top_flows = sorted(learning_patterns['learning_flow'].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
            for flow, count in top_flows:
                formatting_prompt += f"  - Use the sequence: {flow}\n"
    
    return formatting_prompt

def generate_full_prompt(item, include_examples=True):
    """Generate a full prompt based on metadata."""
    file_type = get_file_type(item)
    
    # Basic prompt
    basic_prompt = generate_basic_prompt(item)
    
    # Metrics prompt
    metrics_prompt = generate_metrics_prompt(item)
    
    # Extract example content if needed
    example_content = None
    if include_examples:
        example_content = extract_example_content(file_type)
    
    # Format instructions
    format_prompt = generate_format_instructions(
        file_type, 
        formatting_data=example_content.get('formatting', {}) if example_content and not isinstance(example_content, str) else None,
        learning_patterns=example_content.get('learning_patterns', {}) if example_content and not isinstance(example_content, str) else None
    )
    
    # Example content
    example_prompt = generate_example_prompt(file_type, example_content) if include_examples else ""
    
    # Formatting prompt
    formatting_prompt = generate_formatting_prompt(example_content) if include_examples else ""
    
    # Google Workspace specific instructions
    from ...config import GOOGLE_WORKSPACE_ENABLED
    google_prompt = """
GOOGLE WORKSPACE FORMAT:
- Create content that can be directly used in Google Slides, Google Docs, and Google Sheets
- Use formatting that is compatible with Google Workspace applications
- Ensure slide layouts are compatible with Google Slides
- Structure tables to be compatible with Google Sheets
""" if GOOGLE_WORKSPACE_ENABLED else ""
    
    # Combine all prompt components
    full_prompt = f"""
{basic_prompt}

{metrics_prompt}

{format_prompt}

{formatting_prompt}

{google_prompt}

{example_prompt}

Please generate complete, well-structured workshop content that follows all the guidelines above. The output should include:
1. A PowerPoint presentation (with slide-by-slide content)
2. An instructor guide (with detailed instructions for each section)
3. A pacing guide (with timing for each activity)

Ensure the content maintains the same visual style, formatting, and learning patterns as the example materials.
""".strip()
    
    return full_prompt

def generate_prompt_from_topic(topic, file_type="workshop", learning_objectives=None, target_audience=None, duration=None):
    """Generate a prompt from a topic without metadata."""
    if learning_objectives is None:
        learning_objectives = [
            f"Understand the core concepts of {topic}",
            f"Apply {topic} principles in practical scenarios",
            f"Develop skills in {topic} implementation"
        ]
    
    # Create a minimal metadata item
    item = {
        'workshop_name': topic,
        'file_type': file_type,
        'learning_objectives': learning_objectives,
        'target_audience': target_audience or "Professionals interested in learning about " + topic,
        'duration': duration or "1 day",
        'presentation': {},
        'instructor_guide': {},
        'pacing_guide': {}
    }
    
    return generate_full_prompt(item)
```

### 2.10. workshops/generators/output_generator.py

Add a new generator for creating formatted output files:

```python
import os
import re
from pptx import Presentation
from docx import Document
from openpyxl import Workbook
from ...utils.file_utils import write_file

def parse_llm_output(output_text):
    """Parse the LLM output into separate components for different file types."""
    components = {
        'presentation': [],
        'instructor_guide': [],
        'pacing_guide': []
    }
    
    # Look for section delimiters in the output
    presentation_pattern = r'(?i)(?:POWERPOINT PRESENTATION|PRESENTATION SLIDES|SLIDE DECK)[\s\n]*(?:BEGIN|START)?[\s\n]*(?:-{3,}|\*{3,}|={3,})?([\s\S]*?)(?:-{3,}|\*{3,}|={3,}|\Z)'
    instructor_pattern = r'(?i)(?:INSTRUCTOR GUIDE|TEACHING GUIDE|FACILITATOR GUIDE)[\s\n]*(?:BEGIN|START)?[\s\n]*(?:-{3,}|\*{3,}|={3,})?([\s\S]*?)(?:-{3,}|\*{3,}|={3,}|\Z)'
    pacing_pattern = r'(?i)(?:PACING GUIDE|SCHEDULE|TIMING|RUN OF SHOW)[\s\n]*(?:BEGIN|START)?[\s\n]*(?:-{3,}|\*{3,}|={3,})?([\s\S]*?)(?:-{3,}|\*{3,}|={3,}|\Z)'
    
    # Extract each component
    presentation_match = re.search(presentation_pattern, output_text)
    if presentation_match:
        components['presentation'] = parse_presentation_content(presentation_match.group(1))
    
    instructor_match = re.search(instructor_pattern, output_text)
    if instructor_match:
        components['instructor_guide'] = instructor_match.group(1).strip()
    
    pacing_match = re.search(pacing_pattern, output_text)
    if pacing_match:
        components['pacing_guide'] = parse_pacing_guide_content(pacing_match.group(1))
    
    return components

def parse_presentation_content(content):
    """Parse presentation content into individual slides."""
    slides = []
    
    # Look for slide delimiters
    slide_pattern = r'(?i)(?:Slide|SLIDE)\s*(\d+)[^\n]*\n([\s\S]*?)(?=(?:Slide|SLIDE)\s*\d+|\Z)'
    
    matches = re.finditer(slide_pattern, content)
    for match in matches:
        slide_num = match.group(1)
        slide_content = match.group(2).strip()
        
        # Parse slide content
        title = ""
        content = []
        
        # Try to extract title
        title_match = re.search(r'^(?:#|Title:)\s*(.*?)$', slide_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove the title line from content
            slide_content = re.sub(r'^(?:#|Title:)\s*(.*?)$', '', slide_content, flags=re.MULTILINE)
        
        # Rest is content
        content = slide_content.strip()
        
        slides.append({
            'number': int(slide_num),
            'title': title,
            'content': content
        })
    
    # If no slides were found with the pattern, try to split by slide indicators
    if not slides:
        content_parts = re.split(r'(?i)(?:^|\n)(?:Slide|SLIDE)\s*\d+[^\n]*\n', content)
        if len(content_parts) > 1:
            # First part is usually empty or introduction
            for i, part in enumerate(content_parts[1:], 1):
                slides.append({
                    'number': i,
                    'title': "",
                    'content': part.strip()
                })
    
    return slides

def parse_pacing_guide_content(content):
    """Parse pacing guide content into structured data."""
    # Simple parsing - can be enhanced
    lines = content.strip().split('\n')
    pacing_data = []
    
    for line in lines:
        if '|' in line:
            # Assume pipe-delimited format
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                pacing_data.append({
                    'activity': parts[0],
                    'duration': parts[1],
                    'description': parts[2]
                })
        elif ':' in line:
            # Assume colon-delimited format
            parts = [p.strip() for p in line.split(':', 1)]
            if len(parts) == 2:
                pacing_data.append({
                    'activity': parts[0],
                    'duration': '',
                    'description': parts[1]
                })
    
    return pacing_data

def generate_presentation_file(slides, output_path):
    """Generate a PowerPoint presentation file."""
    prs = Presentation()
    
    for slide_data in slides:
        # Add a slide
        slide_layout = prs.slide_layouts[1]  # Title and Content layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Set title
        if slide_data['title']:
            slide.shapes.title.text = slide_data['title']
        
        # Add content
        if slide_data['content']:
            content_shape = slide.placeholders[1]
            content_shape.text = slide_data['content']
    
    # Save the presentation
    prs.save(output_path)
    return output_path

def generate_instructor_guide_file(content, output_path):
    """Generate an instructor guide document."""
    doc = Document()
    
    # Add title
    doc.add_heading('Instructor Guide', 0)
    
    # Add content
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        # Check if this is a heading
        if para.startswith('#'):
            level = 1
            while para.startswith('#'):
                level += 1
                para = para[1:]
            doc.add_heading(para.strip(), level=min(level, 9))
        else:
            doc.add_paragraph(para)
    
    # Save the document
    doc.save(output_path)
    return output_path

def generate_pacing_guide_file(pacing_data, output_path):
    """Generate a pacing guide spreadsheet."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Pacing Guide"
    
    # Add headers
    ws['A1'] = "Activity"
    ws['B1'] = "Duration"
    ws['C1'] = "Description"
    
    # Add data
    for i, item in enumerate(pacing_data, 2):
        ws[f'A{i}'] = item.get('activity', '')
        ws[f'B{i}'] = item.get('duration', '')
        ws[f'C{i}'] = item.get('description', '')
    
    # Save the workbook
    wb.save(output_path)
    return output_path

def generate_output_files(llm_output, output_dir, workshop_name):
    """Generate all output files from LLM output."""
    # Create output directory
    workshop_dir = os.path.join(output_dir, workshop_name.replace(' ', '_'))
    os.makedirs(workshop_dir, exist_ok=True)
    
    # Parse LLM output
    components = parse_llm_output(llm_output)
    
    output_files = {}
    
    # Generate presentation file
    if components['presentation']:
        pptx_path = os.path.join(workshop_dir, f"{workshop_name} Presentation.pptx")
        output_files['presentation'] = generate_presentation_file(components['presentation'], pptx_path)
    
    # Generate instructor guide
    if components['instructor_guide']:
        docx_path = os.path.join(workshop_dir, f"{workshop_name} Instructor Guide.docx")
        output_files['instructor_guide'] = generate_instructor_guide_file(components['instructor_guide'], docx_path)
    
    # Generate pacing guide
    if components['pacing_guide']:
        xlsx_path = os.path.join(workshop_dir, f"{workshop_name} Pacing Guide.xlsx")
        output_files['pacing_guide'] = generate_pacing_guide_file(components['pacing_guide'], xlsx_path)
    
    # Also save the raw LLM output
    raw_path = os.path.join(workshop_dir, f"{workshop_name} Raw Output.txt")
    write_file(llm_output, raw_path)
    output_files['raw_output'] = raw_path
    
    return output_files
```

### 2.11. workshops/google_integration/auth.py

Add authentication for Google Workspace:

```python
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from ...config import GOOGLE_API_CREDENTIALS_PATH

# Define scopes needed for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

def get_credentials(token_path='token.pickle'):
    """Get Google API credentials, refreshing if necessary."""
    creds = None
    
    # Check if token.pickle exists
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials don't exist or are invalid, refresh or get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_API_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds
```

### 2.12. workshops/google_integration/slides_api.py

Add Google Slides integration:

```python
from googleapiclient.discovery import build
from .auth import get_credentials

def get_slides_service():
    """Get Google Slides API service."""
    creds = get_credentials()
    return build('slides', 'v1', credentials=creds)

def create_presentation(title):
    """Create a new Google Slides presentation."""
    service = get_slides_service()
    body = {
        'title': title
    }
    presentation = service.presentations().create(body=body).execute()
    return presentation.get('presentationId')

def add_slide(presentation_id, title=None, content=None):
    """Add a slide to a presentation."""
    service = get_slides_service()
    
    # Create a new slide
    requests = [
        {
            'createSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_AND_BODY'
                },
                'placeholderIdMappings': [
                    {
                        'layoutPlaceholder': {
                            'type': 'TITLE',
                            'index': 0
                        },
                        'objectId': 'title'
                    },
                    {
                        'layoutPlaceholder': {
                            'type': 'BODY',
                            'index': 0
                        },
                        'objectId': 'body'
                    }
                ]
            }
        }
    ]
    
    response = service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    slide_id = response.get('replies')[0].get('createSlide').get('objectId')
    
    # Add title and content if provided
    if title or content:
        requests = []
        
        if title:
            requests.append({
                'insertText': {
                    'objectId': 'title',
                    'text': title
                }
            })
        
        if content:
            requests.append({
                'insertText': {
                    'objectId': 'body',
                    'text': content
                }
            })
        
        if requests:
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
    
    return slide_id

def generate_google_slides(slides_data, title):
    """Generate a Google Slides presentation from slides data."""
    # Create a new presentation
    presentation_id = create_presentation(title)
    
    # Add slides
    for slide in slides_data:
        add_slide(
            presentation_id,
            title=slide.get('title', ''),
            content=slide.get('content', '')
        )
    
    return presentation_id
```

### 2.13. workshops/google_integration/docs_api.py

Add Google Docs integration:

```python
from googleapiclient.discovery import build
from .auth import get_credentials

def get_docs_service():
    """Get Google Docs API service."""
    creds = get_credentials()
    return build('docs', 'v1', credentials=creds)

def create_document(title, content):
    """Create a new Google Docs document."""
    service = get_docs_service()
    
    # Create a new document
    doc = service.documents().create(body={'title': title}).execute()
    document_id = doc.get('documentId')
    
    # Add content to the document
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': content
            }
        }
    ]
    
    service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()
    
    return document_id
```

### 2.14. workshops/google_integration/sheets_api.py

Add Google Sheets integration:

```python
from googleapiclient.discovery import build
from .auth import get_credentials

def get_sheets_service():
    """Get Google Sheets API service."""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)

def create_spreadsheet(title, data):
    """Create a new Google Sheets spreadsheet."""
    service = get_sheets_service()
    
    # Create a new spreadsheet
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    
    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = spreadsheet.get('spreadsheetId')
    
    # Add data to the spreadsheet
    if data:
        values = []
        
        # Add headers
        values.append(['Activity', 'Duration', 'Description'])
        
        # Add data rows
        for item in data:
            values.append([
                item.get('activity', ''),
                item.get('duration', ''),
                item.get('description', '')
            ])
        
        body = {
            'values': values
        }
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    return spreadsheet_id
```

## 3. Implementation Roadmap

To effectively implement this enhanced workshop content generator, follow this phased approach:

### Phase 1: Core Infrastructure (Weeks 1-2)
- Set up the project structure with the new workshop subdirectory
- Implement basic file reading for Office formats (.pptx, .docx, .xlsx)
- Create the metadata extraction framework

### Phase 2: Format Analysis (Weeks 3-4)
- Implement the format extractor for PowerPoint presentations
- Develop the learning pattern analyzer
- Create the example content extractor with formatting awareness

### Phase 3: Google Workspace Integration (Weeks 5-6)
- Set up Google API authentication
- Implement Google Slides, Docs, and Sheets API integration
- Create format converters between Office and Google formats

### Phase 4: Enhanced Prompt Engineering (Weeks 7-8)
- Develop format-aware prompt templates
- Implement learning pattern-based prompting
- Create Google Workspace-specific prompt components

### Phase 5: Output Generation (Weeks 9-10)
- Implement the output parser for LLM responses
- Create the format-preserving file generators
- Develop Google Workspace output generators

### Phase 6: Testing and Refinement (Weeks 11-12)
- Test with diverse workshop exemplars
- Measure format similarity between exemplars and generated content
- Refine based on instructional design expert feedback

## 4. Additional Considerations

### Performance Optimization
- Implement caching for extracted metadata and formatting information
- Use streaming for large file processing
- Consider parallel processing for multiple files

### Error Handling
- Implement robust error handling for all file operations
- Add validation for extracted metadata
- Create fallback mechanisms for format extraction failures

### Testing Strategy
- Create unit tests for each component
- Develop integration tests for the end-to-end workflow
- Include visual comparison tests for format preservation

### User Experience
- Add a preview feature to show generated content before finalizing
- Implement progress tracking for long-running operations
- Create detailed logs for troubleshooting

By following this enhanced plan, you'll create a powerful workshop content generator that preserves formatting, maintains learning experience patterns, and integrates seamlessly with Google Workspace.
