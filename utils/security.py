"""
Security utilities for the cocobot application.

This module provides input validation, sanitization, and security best practices
to protect against common vulnerabilities.
"""

import re
from typing import Union, List, Optional
from urllib.parse import urlparse
import html
import bleach
from .exceptions import ValidationError, SecurityError


class InputValidator:
    """Utility class for input validation."""
    
    # Regex patterns for common validations
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    DISCORD_ID_PATTERN = re.compile(r'^\d{17,20}$')  # Discord IDs are 17-20 digits
    CURRENCY_CODE_PATTERN = re.compile(r'^[A-Z]{3}$')  # ISO 4217 currency codes
    
    @classmethod
    def validate_email(cls, email: str, field_name: str = "email") -> str:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If email format is invalid
        """
        if not email:
            raise ValidationError(f"{field_name} is required", field_name)
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid {field_name} format", field_name)
        
        return email.strip().lower()
    
    @classmethod
    def validate_url(cls, url: str, field_name: str = "url", allowed_schemes: Optional[List[str]] = None) -> str:
        """
        Validate URL format and scheme.
        
        Args:
            url: URL to validate
            field_name: Name of the field for error messages
            allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL format is invalid
        """
        if not url:
            raise ValidationError(f"{field_name} is required", field_name)
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        if not cls.URL_PATTERN.match(url):
            raise ValidationError(f"Invalid {field_name} format", field_name)
        
        parsed = urlparse(url)
        if parsed.scheme not in allowed_schemes:
            raise ValidationError(f"Invalid scheme for {field_name}. Allowed: {', '.join(allowed_schemes)}", field_name)
        
        return url
    
    @classmethod
    def validate_discord_id(cls, discord_id: str, field_name: str = "discord_id") -> str:
        """
        Validate Discord ID format (17-20 digits).
        
        Args:
            discord_id: Discord ID to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated Discord ID
            
        Raises:
            ValidationError: If Discord ID format is invalid
        """
        if not discord_id:
            raise ValidationError(f"{field_name} is required", field_name)
        
        if not cls.DISCORD_ID_PATTERN.match(discord_id):
            raise ValidationError(f"Invalid {field_name} format. Must be 17-20 digits", field_name)
        
        return discord_id
    
    @classmethod
    def validate_currency_code(cls, currency: str, field_name: str = "currency") -> str:
        """
        Validate currency code format (ISO 4217 - 3 uppercase letters).
        
        Args:
            currency: Currency code to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated currency code
            
        Raises:
            ValidationError: If currency code format is invalid
        """
        if not currency:
            raise ValidationError(f"{field_name} is required", field_name)
        
        currency = currency.strip().upper()
        
        if not cls.CURRENCY_CODE_PATTERN.match(currency):
            raise ValidationError(f"Invalid {field_name} format. Must be 3 uppercase letters", field_name)
        
        return currency
    
    @classmethod
    def validate_length(cls, value: str, min_length: int = 0, max_length: int = None, field_name: str = "value") -> str:
        """
        Validate string length.
        
        Args:
            value: String to validate
            min_length: Minimum length required
            max_length: Maximum length allowed (None for no limit)
            field_name: Name of the field for error messages
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If string length is outside bounds
        """
        if value is None:
            value = ""
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters", field_name)
        
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"{field_name} must be no more than {max_length} characters", field_name)
        
        return value
    
    @classmethod
    def validate_choice(cls, value: str, choices: List[str], field_name: str = "value") -> str:
        """
        Validate that value is in allowed choices.
        
        Args:
            value: Value to validate
            choices: List of allowed values
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValidationError: If value is not in choices
        """
        if value not in choices:
            raise ValidationError(f"{field_name} must be one of: {', '.join(choices)}", field_name)
        
        return value


class InputSanitizer:
    """Utility class for input sanitization."""
    
    # Allowed HTML tags and attributes for rich text
    ALLOWED_TAGS = [
        'p', 'br', 'b', 'i', 'em', 'strong', 'code', 'pre',
        'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    ALLOWED_ATTRIBUTES = {
        'code': ['class'],
        'pre': ['class'],
    }
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 1000) -> str:
        """
        Sanitize plain text input.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if text is None:
            return ""
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove control characters except common whitespace
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    @classmethod
    def sanitize_html(cls, html_content: str, max_length: int = 10000) -> str:
        """
        Sanitize HTML content, allowing only safe tags and attributes.
        
        Args:
            html_content: HTML content to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized HTML
        """
        if html_content is None:
            return ""
        
        # Truncate if too long
        if len(html_content) > max_length:
            html_content = html_content[:max_length]
        
        # Sanitize using bleach
        sanitized = bleach.clean(
            html_content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return sanitized
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Sanitize URL by encoding special characters.
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL
        """
        from urllib.parse import quote, unquote, urlparse, urlunparse
        
        if not url:
            return ""
        
        # First unquote to get the raw URL, then quote properly
        url = unquote(url)
        
        # Parse the URL into components
        parsed = urlparse(url)
        
        # Rebuild the URL with encoded components
        sanitized = urlunparse(
            (
                parsed.scheme,
                parsed.netloc.lower(),  # Normalize to lowercase
                quote(parsed.path, safe="/"),
                quote(parsed.params, safe=""),
                quote(parsed.query, safe="=&?"),
                quote(parsed.fragment, safe="")
            )
        )
        
        return sanitized
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and other attacks.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return ""
        
        import os
        
        # Remove path components to prevent directory traversal
        filename = os.path.basename(filename)
        
        # Remove potentially dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1F\x7F]', '', filename)
        
        # Limit length (255 is typical filesystem limit)
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @classmethod
    def remove_markdown_injection(cls, text: str) -> str:
        """
        Remove potentially dangerous markdown patterns that could be used for injection.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove potentially dangerous patterns while preserving safe markdown
        # This is a simplified approach - for more comprehensive sanitization,
        # consider using a dedicated markdown parser
        
        # Remove HTML tags that might be in markdown
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<object[^>]*>.*?</object>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<embed[^>]*>.*?</embed>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove JavaScript in href attributes
        text = re.sub(r'href\s*=\s*["\'][^"\']*(javascript:|vbscript:|data:)[^"\']*["\']', 'href="#"', text, flags=re.IGNORECASE)
        
        return text


class SecurityChecker:
    """Security utilities for checking potentially malicious content."""
    
    @classmethod
    def check_xss_patterns(cls, content: str) -> bool:
        """
        Check for potential XSS patterns in content.
        
        Args:
            content: Content to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not content:
            return False
        
        # Convert to lowercase for pattern matching
        content_lower = content.lower()
        
        # Common XSS patterns
        xss_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'expression\(',
            r'eval\(',
            r'exec\(',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    @classmethod
    def check_sql_injection_patterns(cls, content: str) -> bool:
        """
        Check for potential SQL injection patterns in content.
        
        Args:
            content: Content to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not content:
            return False
        
        # Convert to lowercase for pattern matching
        content_lower = content.lower()
        
        # Common SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|UNION\s+SELECT)\b)",
            r"(\b(OR|AND)\s+[\d\s\'\"=])",
            r"(\'\s*(OR|AND)\s*\'\d)",
            r"(\'\s*=\s*\')",
            r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC))",
            r"(\'\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC))",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    @classmethod
    def check_command_injection_patterns(cls, content: str) -> bool:
        """
        Check for potential command injection patterns in content.
        
        Args:
            content: Content to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not content:
            return False
        
        # Common command injection patterns
        cmd_patterns = [
            r'[;&|`]',
            r'\$\(',
            r'%\w+%',
            r'`\w+`',
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, content):
                # Additional check to see if it's actually a command pattern
                if re.search(r'\b(echo|cat|ls|pwd|whoami|rm|mv|cp|chmod|chown|ps|kill|grep|find|touch|mkdir|rmdir|cd|env|export|unset|source|eval|exec|command)\b', content.lower()):
                    return True
        
        return False


def validate_and_sanitize_input(input_value: str, input_type: str = "text", **kwargs) -> str:
    """
    Validate and sanitize input based on type.
    
    Args:
        input_value: Input value to validate and sanitize
        input_type: Type of input ('text', 'url', 'email', 'discord_id', 'currency')
        **kwargs: Additional validation parameters
        
    Returns:
        Validated and sanitized input
        
    Raises:
        ValidationError: If validation fails
        SecurityError: If security check fails
    """
    # Security check first
    if SecurityChecker.check_xss_patterns(input_value):
        raise SecurityError("Potential XSS pattern detected in input")
    
    if SecurityChecker.check_sql_injection_patterns(input_value):
        raise SecurityError("Potential SQL injection pattern detected in input")
    
    if SecurityChecker.check_command_injection_patterns(input_value):
        raise SecurityError("Potential command injection pattern detected in input")
    
    # Validation based on type
    if input_type == "text":
        max_length = kwargs.get('max_length', 1000)
        min_length = kwargs.get('min_length', 0)
        input_value = InputValidator.validate_length(input_value, min_length, max_length)
        input_value = InputSanitizer.sanitize_text(input_value, max_length)
        
    elif input_type == "url":
        input_value = InputValidator.validate_url(input_value)
        input_value = InputSanitizer.sanitize_url(input_value)
        
    elif input_type == "email":
        input_value = InputValidator.validate_email(input_value)
        
    elif input_type == "discord_id":
        input_value = InputValidator.validate_discord_id(input_value)
        
    elif input_type == "currency":
        input_value = InputValidator.validate_currency_code(input_value)
        
    else:
        # For unknown types, apply basic text sanitization
        max_length = kwargs.get('max_length', 1000)
        input_value = InputSanitizer.sanitize_text(input_value, max_length)
    
    return input_value


def escape_markdown(text: str) -> str:
    """
    Escape markdown characters in text to prevent markdown injection.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    # Characters to escape in Discord markdown
    markdown_chars = r'([*_~`\\>\[\](){}#+\-=|.!])'
    return re.sub(markdown_chars, r'\\\1', text)


def safe_format_string(template: str, **kwargs) -> str:
    """
    Safely format a string with validation to prevent format string attacks.
    
    Args:
        template: Template string
        **kwargs: Format parameters
        
    Returns:
        Formatted string
    """
    # Validate that template doesn't contain dangerous format patterns
    if re.search(r'{\s*\w*\s*[^\w\s{}:]*\s*}', template):
        raise SecurityError("Template contains potentially dangerous format patterns")
    
    # Escape markdown in all values
    safe_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            safe_kwargs[key] = escape_markdown(str(value))
        else:
            safe_kwargs[key] = value
    
    try:
        return template.format(**safe_kwargs)
    except (KeyError, ValueError, TypeError) as e:
        raise ValidationError(f"Error formatting string: {str(e)}")


# Initialize commonly used validators
email_validator = InputValidator.validate_email
url_validator = InputValidator.validate_url
discord_id_validator = InputValidator.validate_discord_id
currency_validator = InputValidator.validate_currency_code

text_sanitizer = InputSanitizer.sanitize_text
html_sanitizer = InputSanitizer.sanitize_html
url_sanitizer = InputSanitizer.sanitize_url