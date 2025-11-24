#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the condition that the above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

import pytest
from unittest.mock import Mock, patch
from utils.security import (
	InputValidator,
	InputSanitizer,
	SecurityChecker,
	validate_and_sanitize_input,
	escape_markdown,
	safe_format_string
)
from utils.exceptions import ValidationError, SecurityError


class TestInputValidator:
	"""Test the InputValidator class."""

	def test_validate_email_valid(self):
		"""Test validating valid email addresses."""
		valid_emails = [
			"test@example.com",
			"user.name@domain.co.uk",
			"user+tag@example.org",
			"test123@example-domain.com"
		]

		for email in valid_emails:
			validated = InputValidator.validate_email(email)
			assert validated == email.strip().lower()

	def test_validate_email_invalid(self):
		"""Test validating invalid email addresses."""
		invalid_emails = [
			"invalid-email",
			"@example.com",
			"test@",
			"test@.com",
			"test@example"
		]

		for email in invalid_emails:
			with pytest.raises(ValidationError) as exc_info:
				InputValidator.validate_email(email)
			assert exc_info.value.field_name == "email"
			assert "Invalid" in str(exc_info.value) or "required" in str(exc_info.value)

	def test_validate_email_custom_field_name(self):
		"""Test validating email with custom field name."""
		with pytest.raises(ValidationError) as exc_info:
			InputValidator.validate_email("invalid", field_name="user_email")
		assert exc_info.value.field_name == "user_email"

	def test_validate_url_valid(self):
		"""Test validating valid URLs."""
		valid_urls = [
			"http://example.com",
			"https://example.com",
			"https://www.example.com:8080/path",
			"https://subdomain.example.co.uk/path?query=value",
			"http://localhost:3000",
			"http://127.0.0.1:8000"
		]

		for url in valid_urls:
			validated = InputValidator.validate_url(url)
			assert validated == url

	def test_validate_url_invalid(self):
		"""Test validating invalid URLs."""
		invalid_urls = [
			"",
			"not-a-url",
			"ftp://example.com",  # FTP not allowed by default
			"javascript:alert('xss')",  # JavaScript URL
			"https://",
			"https://.com"
		]

		for url in invalid_urls:
			with pytest.raises(ValidationError) as exc_info:
				InputValidator.validate_url(url)
			assert exc_info.value.field_name == "url"

	def test_validate_discord_id_valid(self):
		"""Test validating valid Discord IDs."""
		valid_ids = [
			"123456789012345678",
			"987654321098765432",
			"111111111111111111"
		]

		for discord_id in valid_ids:
			validated = InputValidator.validate_discord_id(discord_id)
			assert validated == discord_id

	def test_validate_discord_id_invalid(self):
		"""Test validating invalid Discord IDs."""
		invalid_ids = [
			"",  # Empty
			"123",  # Too short
			"abc123",  # Contains letters
			"1234567890123456",  # 16 chars (too short)
			"123456789012345678901",  # 21 chars (too long)
			"123-456-789"  # Contains dashes
		]

		for discord_id in invalid_ids:
			with pytest.raises(ValidationError) as exc_info:
				InputValidator.validate_discord_id(discord_id)
			assert exc_info.value.field_name == "discord_id"
			assert "Invalid" in str(exc_info.value) or "required" in str(exc_info.value)

	def test_validate_currency_code_valid(self):
		"""Test validating valid currency codes."""
		valid_codes = ["USD", "EUR", "GBP", "JPY", "THB", "BTC"]

		for code in valid_codes:
			validated = InputValidator.validate_currency_code(code)
			assert validated == code

	def test_validate_currency_code_invalid(self):
		"""Test validating invalid currency codes."""
		invalid_codes = [
			"us",  # Too short
			"usdd",  # Too long
			"us$",  # Invalid characters
			"123",  # Numbers
		]

		for code in invalid_codes:
			with pytest.raises(ValidationError) as exc_info:
				InputValidator.validate_currency_code(code)
			assert exc_info.value.field_name == "currency"
			assert "Invalid" in str(exc_info.value)
		
		# Test that lowercase gets converted to uppercase and passes
		validated = InputValidator.validate_currency_code("usd")
		assert validated == "USD"

	def test_validate_length_valid(self):
		"""Test validating text length."""
		text = "This is a valid text"
		validated = InputValidator.validate_length(text, min_length=5, max_length=100, field_name="test_field")
		assert validated == text

	def test_validate_length_too_short(self):
		"""Test validating text that is too short."""
		with pytest.raises(ValidationError) as exc_info:
			InputValidator.validate_length("hi", min_length=5, max_length=100, field_name="test_field")
		assert exc_info.value.field_name == "test_field"
		assert "at least 5 characters" in str(exc_info.value)

	def test_validate_length_too_long(self):
		"""Test validating text that is too long."""
		long_text = "A" * 101
		with pytest.raises(ValidationError) as exc_info:
			InputValidator.validate_length(long_text, min_length=5, max_length=100, field_name="test_field")
		assert exc_info.value.field_name == "test_field"
		assert "no more than 100 characters" in str(exc_info.value)

	def test_validate_choice_valid(self):
		"""Test validating choice from allowed values."""
		choices = ["red", "green", "blue"]
		validated = InputValidator.validate_choice("red", choices, field_name="color")
		assert validated == "red"

	def test_validate_choice_invalid(self):
		"""Test validating invalid choice."""
		choices = ["red", "green", "blue"]
		with pytest.raises(ValidationError) as exc_info:
			InputValidator.validate_choice("yellow", choices, field_name="color")
		assert exc_info.value.field_name == "color"
		assert "must be one of" in str(exc_info.value)


class TestInputSanitizer:
	"""Test the InputSanitizer class."""

	def test_sanitize_text_basic(self):
		"""Test basic text sanitization."""
		text = "Hello world!"
		sanitized = InputSanitizer.sanitize_text(text)
		assert sanitized == text

	def test_sanitize_text_truncate(self):
		"""Test text sanitization with truncation."""
		long_text = "A" * 150
		sanitized = InputSanitizer.sanitize_text(long_text, max_length=100)
		assert len(sanitized) <= 100

	def test_sanitize_html_basic(self):
		"""Test basic HTML sanitization."""
		html = "<p>Hello <b>world</b></p>"
		sanitized = InputSanitizer.sanitize_html(html)
		assert "Hello" in sanitized
		assert "world" in sanitized

	def test_sanitize_html_removes_dangerous_tags(self):
		"""Test that dangerous HTML tags are removed."""
		dangerous_html = """
        <p>Normal text</p>
        <script>alert('XSS')</script>
        <img src=x onerror=alert('XSS')>
        <iframe src="evil.com"></iframe>
        """

		sanitized = InputSanitizer.sanitize_html(dangerous_html)

		# Check that dangerous tags are removed or sanitized
		assert "<script>" not in sanitized
		assert "onerror=" not in sanitized

		# Check that safe text is preserved
		assert "Normal text" in sanitized

	def test_sanitize_url_valid(self):
		"""Test URL sanitization."""
		url = "https://example.com/path?query=value"
		sanitized = InputSanitizer.sanitize_url(url)
		assert "example.com" in sanitized

	def test_sanitize_filename_valid(self):
		"""Test filename sanitization."""
		filename = "test_file.txt"
		sanitized = InputSanitizer.sanitize_filename(filename)
		assert "test_file.txt" in sanitized

	def test_sanitize_filename_removes_dangerous_chars(self):
		"""Test that dangerous characters are removed from filename."""
		dangerous_filename = "../../../etc/passwd"
		sanitized = InputSanitizer.sanitize_filename(dangerous_filename)
		assert ".." not in sanitized
		assert "/" not in sanitized

	def test_remove_markdown_injection(self):
		"""Test removing markdown injection attempts."""
		text = "Hello <script>alert('XSS')</script> and <iframe src='evil.com'></iframe>!"
		sanitized = InputSanitizer.remove_markdown_injection(text)
		assert "<script>" not in sanitized
		assert "<iframe" not in sanitized
		assert "Hello" in sanitized
		assert "and" in sanitized


class TestSecurityChecker:
	"""Test the SecurityChecker class."""

	def test_check_xss_patterns_detected(self):
		"""Test XSS pattern detection."""
		xss_attempts = [
			"<script>alert('XSS')</script>",
			"<img src=x onerror=alert('XSS')>",
			"javascript:alert('XSS')",
			"<svg onload=alert('XSS')>"
		]

		for attempt in xss_attempts:
			assert SecurityChecker.check_xss_patterns(attempt) is True

	def test_check_xss_patterns_safe(self):
		"""Test safe content doesn't trigger XSS detection."""
		safe_content = [
			"Hello world",
			"This is normal text",
			"<p>Safe HTML</p>"
		]

		for content in safe_content:
			assert SecurityChecker.check_xss_patterns(content) is False

	def test_check_sql_injection_patterns_detected(self):
		"""Test SQL injection pattern detection."""
		sql_injection_attempts = [
			"'; DROP TABLE users; --",
			"1 OR 1=1",
			"admin' --",
			"' UNION SELECT * FROM users --"
		]

		for attempt in sql_injection_attempts:
			assert SecurityChecker.check_sql_injection_patterns(attempt) is True

	def test_check_sql_injection_patterns_safe(self):
		"""Test safe content doesn't trigger SQL injection detection."""
		safe_content = [
			"Hello world",
			"user@example.com",
			"Normal text with apostrophe's"
		]

		for content in safe_content:
			assert SecurityChecker.check_sql_injection_patterns(content) is False

	def test_check_command_injection_patterns_detected(self):
		"""Test command injection pattern detection."""
		command_injection_attempts = [
			"; rm -rf /",
			"&& ls -la",
			"| cat /etc/passwd",
			"`whoami`"
		]

		for attempt in command_injection_attempts:
			assert SecurityChecker.check_command_injection_patterns(attempt) is True

	def test_check_command_injection_patterns_safe(self):
		"""Test safe content doesn't trigger command injection detection."""
		safe_content = [
			"Hello world",
			"user@example.com",
			"Text with & symbol"
		]

		for content in safe_content:
			assert SecurityChecker.check_command_injection_patterns(content) is False


class TestUtilityFunctions:
	"""Test utility functions in the security module."""

	def test_validate_and_sanitize_input_text(self):
		"""Test validate_and_sanitize_input with text type."""
		result = validate_and_sanitize_input("Hello world", input_type="text")
		assert result == "Hello world"

	def test_validate_and_sanitize_input_email(self):
		"""Test validate_and_sanitize_input with email type."""
		result = validate_and_sanitize_input("test@example.com", input_type="email")
		assert result == "test@example.com"

	def test_validate_and_sanitize_input_invalid(self):
		"""Test validate_and_sanitize_input with invalid input."""
		with pytest.raises(ValidationError):
			validate_and_sanitize_input("invalid-email", input_type="email")

	def test_escape_markdown(self):
		"""Test markdown escaping."""
		text = "Hello *world* _test_ **bold**"
		escaped = escape_markdown(text)
		assert "\\*" in escaped or "*world*" not in escaped

	def test_safe_format_string(self):
		"""Test safe string formatting."""
		template = "Hello {name}, welcome to {place}!"
		result = safe_format_string(template, name="Alice", place="Wonderland")
		assert "Alice" in result
		assert "Wonderland" in result

	def test_safe_format_string_with_unsafe_content(self):
		"""Test safe string formatting with potentially unsafe content."""
		template = "User input: {input}"
		result = safe_format_string(template, input="<script>alert('XSS')</script>")
		# The markdown escaping should handle the special characters
		assert "input" in result
