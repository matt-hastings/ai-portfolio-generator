"""
Functions for generating format instructions and content standards.
"""

def generate_format_instructions(file_type):
    """
    Generate format instructions based on file type
    
    Args:
        file_type (str): Type of file to generate format instructions for (e.g., 'lesson', 'lab')
        
    Returns:
        str: Format instructions for the specified file type
    """
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
    elif file_type == 'lab':
        return """
FORMAT STRUCTURE:
- Begin with the GA logo: ![](https://ga-dash.s3.amazonaws.com/production/assets/logo-9f88ae6c9c3871690e33280fcf557f33.png)
- Include a metadata table with: Title, Type, Duration, Author
- Format as a multi-day lab with clear day-by-day breakdowns
- Include detailed learning objectives
- Include user stories that define functionality from the user's perspective
- Provide step-by-step instructions for each task
- Include submission instructions at the end
- Use code blocks with proper syntax highlighting
- Include diagrams and images where appropriate
- Add hints using expandable sections with <details> tags
- Include checkpoint moments where students can verify their progress
- Add "Challenge" sections for students who want to go deeper
"""
    else:
        return """
FORMAT STRUCTURE:
- Use proper markdown formatting
- Include clear headings and subheadings
- Format code examples with proper syntax highlighting
- Include diagrams and images where appropriate
"""

def generate_content_standards():
    """
    Generate content standards
    
    Returns:
        str: Content standards
    """
    return """
CONTENT STANDARDS:
- Follow 30% theory, 70% hands-on practice ratio
- Include at least 5 hands-on activities
- Each concept should be immediately followed by application
- Write in American English
- Include diagrams and visuals to illustrate points
- Begin with clear learning objectives
- Write for instructor live delivery over Zoom
- Ensure content is engaging and interactive
- Include practical examples and demonstrations
- Provide opportunities for students to apply what they've learned
- Ensure the content follows a logical flow
- Include references to additional resources where appropriate
- Frame the lesson within a realistic development scenario
- Include references to industry practices
- Add "Why This Matters" sections connecting concepts to job skills
"""

def generate_step_by_step_guidance():
    """
    Generate step-by-step guidance
    
    Returns:
        str: Step-by-step guidance
    """
    return """
STEP-BY-STEP GUIDANCE:
- Build functionality incrementally, with each step building on the previous one
- Show immediate results after each step (e.g., "Run the code and observe...")
- Provide code snippets at each step, not just at the end
- Include screenshots or descriptions of expected results after key steps
- Use diagrams to show architecture/component relationships
- Highlight what changes between steps
- Include prompts like "Take a minute to consider what this code is doing"
- Explain why certain approaches are used, not just how
- Include notes explaining concepts in context
- Add "Try it out" moments after each significant change
- Include specific questions for students to consider at key points
"""
