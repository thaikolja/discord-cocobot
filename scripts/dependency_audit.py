#!/usr/bin/env python3
#  Copyright (C) 2026 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the
#  condition that the above copyright notice and this permission notice shall be
#  included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2024-2026
#  Package:   cocobot Discord Bot

"""
Dependency security audit script for the cocobot application.

This script performs security scanning of dependencies and generates
a report of potential vulnerabilities.
"""

# Parse safety/bandit JSON; they speak JSON when they're in a good mood
import json

# chdir so we run from the script directory, not wherever you were standing
import os

# Subprocess: we shell out to pip, safety, and bandit
import subprocess

# Exit codes so CI can fail the coconut
import sys

# Path to this script
from pathlib import Path

# Typing for reports that are just dicts with opinions
from typing import Dict, List, Optional


# Run a command; never raise, return codes like an adult
def run_command(cmd: List[str]) -> tuple[int, str, str]:
    """
    Run a command and return (return_code, stdout, stderr).

    Args:
        cmd: Command to run as a list of strings

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Capture stdout/stderr as text; check=False so we handle rc
    try:
        # Don't inherit a TTY; this is a scanner, not a chat
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Triple for the caller
        return result.returncode, result.stdout, result.stderr

    # Binary missing from PATH
    except FileNotFoundError:
        # Fake rc 1 and a useful stderr
        return 1, "", f"Command not found: {' '.join(cmd)}"


# safety check against requirements.txt
def check_dependency_vulnerabilities() -> Dict:
    """
    Check for vulnerabilities in dependencies using safety.

    Returns:
        Dictionary containing vulnerability report
    """
    # Announce so the log isn't silent for 40 seconds
    print("Checking for dependency vulnerabilities...")

    # Probe safety via python -m
    returncode, _, _ = run_command(["python", "-m", "safety", "--version"])

    # Not installed: pip install it into this interpreter
    if returncode != 0:
        # Tell the human we're about to mutate their env
        print("Installing safety...")

        # Same interpreter as this script
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "pip", "install", "safety"]
        )

        # Install failed: stop, don't pretend we scanned
        if returncode != 0:
            # Show pip's complaint
            print(f"Failed to install safety: {stderr}")

            # Structured error for the report
            return {"error": "Could not install safety"}

    # JSON check against requirements.txt
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "safety", "check", "-r", "requirements.txt", "--json"]
    )

    # Nonzero + stderr: print a warning, still try to parse stdout
    if returncode != 0 and stderr:
        # Safety loves to warn
        print(f"Safety check warning: {stderr}")

    # Parse JSON or admit defeat
    try:
        # Empty stdout is "no vulns", not "broken"
        vulnerabilities = json.loads(stdout) if stdout.strip() else []

        # Count and list
        return {
            "vulnerabilities_found": len(vulnerabilities) > 0,
            "count":                 len(vulnerabilities),
            "vulnerabilities":       vulnerabilities,
        }

    # safety printed a novel instead of JSON
    except json.JSONDecodeError:
        # Keep raw output for debugging
        return {
            "error":      f"Could not parse safety output: {stdout}",
            "raw_output": stdout,
        }


# pip list --outdated
def check_outdated_packages() -> Dict:
    """
    Check for outdated packages using pip list.

    Returns:
        Dictionary containing outdated packages report
    """
    # Status line
    print("Checking for outdated packages...")

    # JSON list of packages behind PyPI
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"]
    )

    # pip failed
    if returncode != 0:
        # Don't invent a package list
        return {"error": f"Could not check outdated packages: {stderr}"}

    # Parse
    try:
        # Empty means everything is current (or pip was quiet)
        outdated = json.loads(stdout) if stdout.strip() else []

        # Count and packages
        return {
            "outdated_found": len(outdated) > 0,
            "count":          len(outdated),
            "packages":       outdated,
        }

    # pip didn't give JSON
    except json.JSONDecodeError:
        # Include stdout
        return {"error": f"Could not parse pip list output: {stdout}"}


# bandit -r . as JSON
def run_bandit_scan() -> Dict:
    """
    Run Bandit security scan on the codebase.

    Returns:
        Dictionary containing scan results
    """
    # Status
    print("Running Bandit security scan...")

    # Is bandit on PATH?
    returncode, _, _ = run_command(["bandit", "--version"])

    # Install if missing
    if returncode != 0:
        # Announce pip install
        print("Installing bandit...")

        # Into this interpreter
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "pip", "install", "bandit"]
        )

        # Install failed
        if returncode != 0:
            # Print stderr
            print(f"Failed to install bandit: {stderr}")

            # Structured error
            return {"error": "Could not install bandit"}

    # Recurse, JSON, low confidence/severity filters as originally written
    returncode, stdout, stderr = run_command(
        ["bandit", "-r", ".", "-f", "json", "-ll", "-ii"]
    )

    # Nonzero with stderr: warn
    if returncode != 0 and stderr:
        # Bandit uses rc for findings too; still log stderr
        print(f"Bandit scan issue: {stderr}")

    # Parse
    try:
        # Empty stdout -> empty dict
        results = json.loads(stdout) if stdout.strip() else {}

        # Count results list
        return {
            "issues_found": results.get("results") and len(results["results"]) > 0,
            "count":        len(results.get("results", [])),
            "results":      results,
        }

    # Not JSON
    except json.JSONDecodeError:
        # Keep raw
        return {
            "error":      f"Could not parse bandit output: {stdout}",
            "raw_output": stdout,
        }


# Run all three checks into one report dict
def generate_report() -> Dict:
    """
    Generate a comprehensive security report.

    Returns:
        Dictionary containing the complete security report
    """
    # Header
    print("Generating security report for cocobot...")

    # Visual ruler
    print("=" * 50)

    # Timestamp via datetime import inline (original style)
    report = {
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "project":   "cocobot",
        "checks":    {
            "dependency_vulnerabilities": check_dependency_vulnerabilities(),
            "outdated_packages":          check_outdated_packages(),
            "code_security_scan":         run_bandit_scan(),
        },
    }

    # Hand back the blob
    return report


# Pretty-print the report to stdout
def print_report(report: Dict):
    """
    Print a formatted security report.

    Args:
        report: Security report dictionary
    """
    # Banner
    print("\n" + "=" * 50)

    # Title
    print("COCOBOT SECURITY REPORT")

    # Banner again
    print("=" * 50)

    # When we ran
    print(f"Generated: {report['timestamp']}")

    # Blank line
    print()

    # Pull dependency check
    dep_check = report['checks']['dependency_vulnerabilities']

    # Section title
    print("DEPENDENCY VULNERABILITIES")

    # Underline
    print("-" * 30)

    # Tool error
    if dep_check.get('error'):
        # Show error
        print(f"❌ Error: {dep_check['error']}")

    # Findings
    elif dep_check.get('vulnerabilities_found'):
        # Count
        print(f"❌ {dep_check['count']} vulnerabilities found!")

        # First five only
        for vuln in dep_check.get('vulnerabilities', [])[:5]:  # Show first 5
            # Name + description
            print(
                f"  - {vuln.get('name', 'Unknown')} - {vuln.get('description', 'No description')}"
            )

        # Overflow line
        if dep_check['count'] > 5:
            # How many we hid
            print(f"  ... and {dep_check['count'] - 5} more")

    # Clean
    else:
        # Count lines in requirements.txt as "dependencies"
        print(
            f"✅ No vulnerabilities found in {len(open('requirements.txt').readlines())} dependencies"
        )

    # Spacer
    print()

    # Outdated section
    outdated_check = report['checks']['outdated_packages']

    # Title
    print("OUTDATED PACKAGES")

    # Underline
    print("-" * 30)

    # Error
    if outdated_check.get('error'):
        # Print it
        print(f"❌ Error: {outdated_check['error']}")

    # Outdated list
    elif outdated_check.get('outdated_found'):
        # Count
        print(f"⚠️  {outdated_check['count']} outdated packages found!")

        # First ten
        for pkg in outdated_check.get('packages', [])[:10]:  # Show first 10
            # name: old -> new
            print(f"  - {pkg['name']}: {pkg['version']} -> {pkg['latest_version']}")

        # Overflow
        if outdated_check['count'] > 10:
            # Remaining
            print(f"  ... and {outdated_check['count'] - 10} more")

    # All current
    else:
        # Same requirements.txt line count trick
        print(
            f"✅ All {len(open('requirements.txt').readlines())} packages are up to date"
        )

    # Spacer
    print()

    # Bandit section
    code_check = report['checks']['code_security_scan']

    # Title
    print("CODE SECURITY SCAN")

    # Underline
    print("-" * 30)

    # Error
    if code_check.get('error'):
        # Print
        print(f"❌ Error: {code_check['error']}")

    # Issues
    elif code_check.get('issues_found'):
        # Count
        print(f"⚠️  {code_check['count']} security issues found in code!")

        # HIGH severity
        high_issues = [
            r
            for r in code_check.get('results', {}).get('results', [])
            if r.get('issue_severity') == 'HIGH'
        ]

        # MEDIUM
        medium_issues = [
            r
            for r in code_check.get('results', {}).get('results', [])
            if r.get('issue_severity') == 'MEDIUM'
        ]

        # LOW
        low_issues = [
            r
            for r in code_check.get('results', {}).get('results', [])
            if r.get('issue_severity') == 'LOW'
        ]

        # Print counts
        print(f"  - High severity: {len(high_issues)}")

        # Medium
        print(f"  - Medium severity: {len(medium_issues)}")

        # Low
        print(f"  - Low severity: {len(low_issues)}")

    # Clean code, or bandit found nothing
    else:
        # Green check
        print("✅ No security issues found in code")

    # Spacer
    print()

    # Summary
    print("SUMMARY")

    # Underline
    print("-" * 30)

    # Any of the three checks unhappy?
    issues_found = (
        dep_check.get('vulnerabilities_found', False)
        or outdated_check.get('outdated_found', False)
        or code_check.get('issues_found', False)
    )

    # Unhappy
    if issues_found:
        # Review the report
        print("⚠️  Issues detected - please review the detailed report above")

        # Unsolicited advice
        print("   Consider updating dependencies and fixing security issues")

    # Happy
    else:
        # Pat on the shell
        print("✅ No issues detected - good security posture!")

    # Close banner
    print("=" * 50)


# Dump JSON to disk
def save_report(report: Dict, filename: Optional[str] = None):
    """
    Save the security report to a file.

    Args:
        report: Security report dictionary
        filename: Output filename (default: security_report_YYYYMMDD.json)
    """
    # Default name with UTC timestamp
    if filename is None:
        # Local import, matching original
        from datetime import datetime

        # Compact stamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Filename
        filename = f"security_report_{timestamp}.json"

    # Write JSON
    with open(filename, 'w') as f:
        # Pretty-printed
        json.dump(report, f, indent=2)

    # Tell the operator where it went
    print(f"\nFull security report saved to: {filename}")


# CLI: chdir, generate, print, save, exit
def main():
    """Main function to run the dependency audit."""
    # Directory of this file
    script_dir = Path(__file__).parent

    # Run from here so requirements.txt resolves
    os.chdir(script_dir)

    # Build the report
    report = generate_report()

    # Human-readable stdout
    print_report(report)

    # JSON on disk
    save_report(report)

    # Same issue flags as the summary
    issues_found = (
        report['checks']['dependency_vulnerabilities'].get(
            'vulnerabilities_found', False
        )
        or report['checks']['outdated_packages'].get('outdated_found', False)
        or report['checks']['code_security_scan'].get('issues_found', False)
    )

    # Fail CI
    if issues_found:
        # Stern line
        print("\nSecurity issues were found. Please address them as soon as possible.")

        # Exit 1
        sys.exit(1)

    # Pass
    else:
        # Encouragement
        print("\nNo security issues found. Good job!")

        # Exit 0
        sys.exit(0)


# Script entry
if __name__ == "__main__":
    # Run the audit
    main()
