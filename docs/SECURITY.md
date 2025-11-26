# Security Policy

## Supported Versions

We support the latest version of cocobot with security updates. For older versions, please upgrade to the latest version to receive security fixes.

| Version | Supported          |
| ------- | ------------------ |
| latest  | ✅ Supported       |
| < latest | ❌ Not supported  |

## Reporting a Vulnerability

We take the security of cocobot seriously. If you believe you have found a security vulnerability, please follow these steps:

### Do Not Create Public Issues
Please do not create public GitHub issues for security vulnerabilities. This could potentially expose the vulnerability to malicious actors before we have a chance to fix it.

### How to Report
1. **Email**: Send an email to kolja.nolte@gmail.com with the subject "Security Vulnerability Report"
2. **Include details**:
   - Type of vulnerability
   - Location where the vulnerability exists
   - Reproduction steps
   - Potential impact
   - Your contact information (optional)

### What to Expect
- Acknowledgment of your report within 48 hours
- Updates on our progress fixing the vulnerability
- Notification when the fix has been released
- Public disclosure of the vulnerability after the fix is released

## Security Best Practices

### For Users
- Keep your bot token secure and never commit it to version control
- Regularly rotate your API keys
- Use environment variables for sensitive configuration
- Monitor your bot's activity for unusual behavior
- Only invite the bot to trusted servers

### For Developers
- Follow secure coding practices
- Validate and sanitize all inputs
- Implement proper error handling
- Use parameterized queries to prevent SQL injection
- Implement rate limiting to prevent abuse
- Keep dependencies up to date
- Use dependency scanning tools

## Security Scanning

Our CI/CD pipeline includes:
- Static analysis with Bandit
- Dependency vulnerability scanning with Safety
- Linting with Flake8 and Black
- Type checking with MyPy
- Automated testing with PyTest

## Dependencies

We actively maintain our dependencies and regularly update them to include security fixes:
- Dependencies are scanned for known vulnerabilities
- Outdated dependencies are automatically updated via Dependabot
- New dependencies are reviewed before inclusion

## Updates

- Security updates are released as soon as possible after discovery
- Breaking security fixes may be released as minor versions
- All security-related changes are documented in the CHANGELOG

## Contact

For security-related questions or concerns, please contact kolja.nolte@gmail.com.