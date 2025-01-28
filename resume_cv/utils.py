import bleach
import uuid
from bs4 import BeautifulSoup

def generate_unique_code():
    """Generate a unique code for resumes"""
    return str(uuid.uuid4())

def sanitize_html(html_content):
    """
    Sanitize HTML content to prevent XSS attacks while preserving safe HTML elements and attributes
    """
    if not html_content:
        return ""
        
    # Define allowed tags and attributes
    allowed_tags = [
        'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'em', 'u', 'strike', 'br', 'hr',
        'ul', 'ol', 'li',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'img', 'a',
        'section', 'article', 'header', 'footer', 'nav',
        'blockquote', 'pre', 'code'
    ]
    
    allowed_attributes = {
        '*': ['class', 'style', 'id'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height']
    }
    
    allowed_styles = [
        'background', 'background-color', 'border', 'border-radius',
        'color', 'display', 'font-family', 'font-size', 'font-weight',
        'height', 'line-height', 'margin', 'padding', 'text-align',
        'text-decoration', 'width'
    ]
    
    # Clean the HTML
    cleaned_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        styles=allowed_styles,
        strip=True
    )
    
    # Parse and format the HTML
    soup = BeautifulSoup(cleaned_html, 'html.parser')
    return soup.prettify()

def format_file_size(size_in_bytes):
    """Convert file size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"

def validate_file_type(file, allowed_types):
    """Validate file type against a list of allowed MIME types"""
    if not file:
        return False
    return file.content_type in allowed_types

def get_file_extension(filename):
    """Get file extension from filename"""
    try:
        return filename.rsplit('.', 1)[1].lower()
    except IndexError:
        return None 