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

from utils.exceptions import (
    APIError,
    CocobotException,
    CommandError,
    ConfigurationError,
    DatabaseError,
    RateLimitError,
    SecurityError,
    ValidationError,
)


class TestCocobotException:
    """Test the base CocobotException class."""

    def test_cocobot_exception_basic(self):
        """Test basic CocobotException instantiation."""
        exc = CocobotException("Test error message")
        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.error_code is None
        assert exc.original_exception is None

    def test_cocobot_exception_with_error_code(self):
        """Test CocobotException with error code."""
        exc = CocobotException("Test error message", error_code="TEST_ERROR")
        assert str(exc) == "[TEST_ERROR] Test error message"
        assert exc.error_code == "TEST_ERROR"

    def test_cocobot_exception_with_original_exception(self):
        """Test CocobotException with original exception."""
        original = ValueError("Original error")
        exc = CocobotException("Test error message", original_exception=original)
        assert exc.original_exception == original
        assert str(exc) == "Test error message"

    def test_cocobot_exception_with_all_parameters(self):
        """Test CocobotException with all parameters."""
        original = RuntimeError("Original error")
        exc = CocobotException(
            "Test error message", error_code="TEST_ERROR", original_exception=original
        )
        assert str(exc) == "[TEST_ERROR] Test error message"
        assert exc.error_code == "TEST_ERROR"
        assert exc.original_exception == original


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_configuration_error_basic(self):
        """Test basic ConfigurationError instantiation."""
        exc = ConfigurationError("Configuration failed")
        assert str(exc) == "[CONFIG_ERROR] Configuration failed"
        assert exc.error_code == "CONFIG_ERROR"
        assert exc.config_key is None

    def test_configuration_error_with_config_key(self):
        """Test ConfigurationError with config key."""
        exc = ConfigurationError("Missing API key", config_key="API_KEY")
        assert str(exc) == "[CONFIG_ERROR] Missing API key"
        assert exc.config_key == "API_KEY"


class TestAPIError:
    """Test APIError class."""

    def test_api_error_basic(self):
        """Test basic APIError instantiation."""
        exc = APIError("API request failed")
        assert str(exc) == "[API_ERROR] API request failed"
        assert exc.error_code == "API_ERROR"
        assert exc.status_code is None
        assert exc.api_name is None

    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        exc = APIError("API request failed", status_code=404)
        assert exc.status_code == 404

    def test_api_error_with_api_name(self):
        """Test APIError with API name."""
        exc = APIError("API request failed", api_name="WeatherAPI")
        assert exc.api_name == "WeatherAPI"

    def test_api_error_with_all_parameters(self):
        """Test APIError with all parameters."""
        exc = APIError("API request failed", status_code=500, api_name="TestAPI")
        assert exc.status_code == 500
        assert exc.api_name == "TestAPI"


class TestCommandError:
    """Test CommandError class."""

    def test_command_error_basic(self):
        """Test basic CommandError instantiation."""
        exc = CommandError("Command execution failed")
        assert str(exc) == "[COMMAND_ERROR] Command execution failed"
        assert exc.error_code == "COMMAND_ERROR"
        assert exc.command_name is None

    def test_command_error_with_command_name(self):
        """Test CommandError with command name."""
        exc = CommandError("Command execution failed", command_name="test_command")
        assert exc.command_name == "test_command"


class TestRateLimitError:
    """Test RateLimitError class."""

    def test_rate_limit_error_basic(self):
        """Test basic RateLimitError instantiation."""
        exc = RateLimitError("Rate limit exceeded")
        assert str(exc) == "[RATE_LIMIT_ERROR] Rate limit exceeded"
        assert exc.error_code == "RATE_LIMIT_ERROR"
        assert exc.retry_after is None

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry after time."""
        exc = RateLimitError("Rate limit exceeded", retry_after=60.5)
        assert exc.retry_after == 60.5


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_basic(self):
        """Test basic ValidationError instantiation."""
        exc = ValidationError("Invalid input")
        assert str(exc) == "[VALIDATION_ERROR] Invalid input"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field_name is None

    def test_validation_error_with_field_name(self):
        """Test ValidationError with field name."""
        exc = ValidationError("Invalid email format", field_name="email")
        assert exc.field_name == "email"


class TestDatabaseError:
    """Test DatabaseError class."""

    def test_database_error_basic(self):
        """Test basic DatabaseError instantiation."""
        exc = DatabaseError("Database operation failed")
        assert str(exc) == "[DB_ERROR] Database operation failed"
        assert exc.error_code == "DB_ERROR"
        assert exc.operation is None

    def test_database_error_with_operation(self):
        """Test DatabaseError with operation."""
        exc = DatabaseError("Database operation failed", operation="INSERT")
        assert exc.operation == "INSERT"


class TestSecurityError:
    """Test SecurityError class."""

    def test_security_error_basic(self):
        """Test basic SecurityError instantiation."""
        exc = SecurityError("Security violation detected")
        assert str(exc) == "[SECURITY_ERROR] Security violation detected"
        assert exc.error_code == "SECURITY_ERROR"
        assert exc.security_type is None

    def test_security_error_with_security_type(self):
        """Test SecurityError with security type."""
        exc = SecurityError(
            "Security violation detected", security_type="SQL_INJECTION"
        )
        assert exc.security_type == "SQL_INJECTION"


class TestExceptionHierarchy:
    """Test that all custom exceptions inherit from CocobotException."""

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from CocobotException."""
        exc = ConfigurationError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)

    def test_api_error_inheritance(self):
        """Test APIError inherits from CocobotException."""
        exc = APIError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)

    def test_command_error_inheritance(self):
        """Test CommandError inherits from CocobotException."""
        exc = CommandError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)

    def test_rate_limit_error_inheritance(self):
        """Test RateLimitError inherits from CocobotException."""
        exc = RateLimitError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from CocobotException."""
        exc = ValidationError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)

    def test_database_error_inheritance(self):
        """Test DatabaseError inherits from CocobotException."""
        exc = DatabaseError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)

    def test_security_error_inheritance(self):
        """Test SecurityError inherits from CocobotException."""
        exc = SecurityError("Test")
        assert isinstance(exc, CocobotException)
        assert isinstance(exc, Exception)


class TestExceptionUsage:
    """Test that exceptions can be raised and caught correctly."""

    def test_raise_and_catch_configuration_error(self):
        """Test raising and catching ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Config error", config_key="TEST_KEY")

        assert exc_info.value.config_key == "TEST_KEY"
        assert "[CONFIG_ERROR]" in str(exc_info.value)

    def test_raise_and_catch_api_error(self):
        """Test raising and catching APIError."""
        with pytest.raises(APIError) as exc_info:
            raise APIError("API error", status_code=404, api_name="TestAPI")

        assert exc_info.value.status_code == 404
        assert exc_info.value.api_name == "TestAPI"

    def test_catch_cocobot_exception_base_class(self):
        """Test catching any CocobotException via base class."""
        exceptions_to_test = [
            ConfigurationError("Test"),
            APIError("Test"),
            CommandError("Test"),
            RateLimitError("Test"),
            ValidationError("Test"),
            DatabaseError("Test"),
            SecurityError("Test"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(CocobotException):
                raise exc

    def test_exception_with_original_exception_chain(self):
        """Test exception chaining with original exception."""
        original = ValueError("Original error")

        with pytest.raises(CocobotException) as exc_info:
            raise APIError("API failed", original_exception=original)

        assert exc_info.value.original_exception == original
        assert isinstance(exc_info.value.original_exception, ValueError)
