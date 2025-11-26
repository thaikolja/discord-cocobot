#!/usr/bin/env python3
"""
Dependency security audit script for the cocobot application.

This script performs security scanning of dependencies and generates
a report of potential vulnerabilities.
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional


def run_command(cmd: List[str]) -> tuple[int, str, str]:
    """
    Run a command and return (return_code, stdout, stderr).
    
    Args:
        cmd: Command to run as a list of strings
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", f"Command not found: {' '.join(cmd)}"


def check_dependency_vulnerabilities() -> Dict:
    """
    Check for vulnerabilities in dependencies using safety.
    
    Returns:
        Dictionary containing vulnerability report
    """
    print("Checking for dependency vulnerabilities...")
    
    # Check if safety is installed
    returncode, _, _ = run_command(["python", "-m", "safety", "--version"])
    if returncode != 0:
        # Install safety
        print("Installing safety...")
        returncode, stdout, stderr = run_command([
            sys.executable, "-m", "pip", "install", "safety"
        ])
        if returncode != 0:
            print(f"Failed to install safety: {stderr}")
            return {"error": "Could not install safety"}
    
    # Run safety check
    returncode, stdout, stderr = run_command([
        sys.executable, "-m", "safety", "check", "-r", "requirements.txt", "--json"
    ])
    
    if returncode != 0 and stderr:
        print(f"Safety check warning: {stderr}")
    
    try:
        vulnerabilities = json.loads(stdout) if stdout.strip() else []
        return {
            "vulnerabilities_found": len(vulnerabilities) > 0,
            "count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities
        }
    except json.JSONDecodeError:
        return {
            "error": f"Could not parse safety output: {stdout}",
            "raw_output": stdout
        }


def check_outdated_packages() -> Dict:
    """
    Check for outdated packages using pip list.
    
    Returns:
        Dictionary containing outdated packages report
    """
    print("Checking for outdated packages...")
    
    returncode, stdout, stderr = run_command([
        sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"
    ])
    
    if returncode != 0:
        return {"error": f"Could not check outdated packages: {stderr}"}
    
    try:
        outdated = json.loads(stdout) if stdout.strip() else []
        return {
            "outdated_found": len(outdated) > 0,
            "count": len(outdated),
            "packages": outdated
        }
    except json.JSONDecodeError:
        return {"error": f"Could not parse pip list output: {stdout}"}


def run_bandit_scan() -> Dict:
    """
    Run Bandit security scan on the codebase.
    
    Returns:
        Dictionary containing scan results
    """
    print("Running Bandit security scan...")
    
    # Check if bandit is installed
    returncode, _, _ = run_command(["bandit", "--version"])
    if returncode != 0:
        # Install bandit
        print("Installing bandit...")
        returncode, stdout, stderr = run_command([
            sys.executable, "-m", "pip", "install", "bandit"
        ])
        if returncode != 0:
            print(f"Failed to install bandit: {stderr}")
            return {"error": "Could not install bandit"}
    
    # Run bandit scan
    returncode, stdout, stderr = run_command([
        "bandit", "-r", ".", "-f", "json", "-ll", "-ii"
    ])
    
    if returncode != 0 and stderr:
        print(f"Bandit scan issue: {stderr}")
    
    try:
        results = json.loads(stdout) if stdout.strip() else {}
        return {
            "issues_found": results.get("results") and len(results["results"]) > 0,
            "count": len(results.get("results", [])),
            "results": results
        }
    except json.JSONDecodeError:
        return {
            "error": f"Could not parse bandit output: {stdout}",
            "raw_output": stdout
        }


def generate_report() -> Dict:
    """
    Generate a comprehensive security report.
    
    Returns:
        Dictionary containing the complete security report
    """
    print("Generating security report for cocobot...")
    print("=" * 50)
    
    report = {
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "project": "cocobot",
        "checks": {
            "dependency_vulnerabilities": check_dependency_vulnerabilities(),
            "outdated_packages": check_outdated_packages(),
            "code_security_scan": run_bandit_scan()
        }
    }
    
    return report


def print_report(report: Dict):
    """
    Print a formatted security report.
    
    Args:
        report: Security report dictionary
    """
    print("\n" + "=" * 50)
    print("COCOBOT SECURITY REPORT")
    print("=" * 50)
    print(f"Generated: {report['timestamp']}")
    print()
    
    # Dependency vulnerabilities
    dep_check = report['checks']['dependency_vulnerabilities']
    print("DEPENDENCY VULNERABILITIES")
    print("-" * 30)
    if dep_check.get('error'):
        print(f"❌ Error: {dep_check['error']}")
    elif dep_check.get('vulnerabilities_found'):
        print(f"❌ {dep_check['count']} vulnerabilities found!")
        for vuln in dep_check.get('vulnerabilities', [])[:5]:  # Show first 5
            print(f"  - {vuln.get('name', 'Unknown')} - {vuln.get('description', 'No description')}")
        if dep_check['count'] > 5:
            print(f"  ... and {dep_check['count'] - 5} more")
    else:
        print(f"✅ No vulnerabilities found in {len(open('requirements.txt').readlines())} dependencies")
    print()
    
    # Outdated packages
    outdated_check = report['checks']['outdated_packages']
    print("OUTDATED PACKAGES")
    print("-" * 30)
    if outdated_check.get('error'):
        print(f"❌ Error: {outdated_check['error']}")
    elif outdated_check.get('outdated_found'):
        print(f"⚠️  {outdated_check['count']} outdated packages found!")
        for pkg in outdated_check.get('packages', [])[:10]:  # Show first 10
            print(f"  - {pkg['name']}: {pkg['version']} -> {pkg['latest_version']}")
        if outdated_check['count'] > 10:
            print(f"  ... and {outdated_check['count'] - 10} more")
    else:
        print(f"✅ All {len(open('requirements.txt').readlines())} packages are up to date")
    print()
    
    # Code security scan
    code_check = report['checks']['code_security_scan']
    print("CODE SECURITY SCAN")
    print("-" * 30)
    if code_check.get('error'):
        print(f"❌ Error: {code_check['error']}")
    elif code_check.get('issues_found'):
        print(f"⚠️  {code_check['count']} security issues found in code!")
        # Count by severity
        high_issues = [r for r in code_check.get('results', {}).get('results', []) if r.get('issue_severity') == 'HIGH']
        medium_issues = [r for r in code_check.get('results', {}).get('results', []) if r.get('issue_severity') == 'MEDIUM']
        low_issues = [r for r in code_check.get('results', {}).get('results', []) if r.get('issue_severity') == 'LOW']
        
        print(f"  - High severity: {len(high_issues)}")
        print(f"  - Medium severity: {len(medium_issues)}")
        print(f"  - Low severity: {len(low_issues)}")
    else:
        print("✅ No security issues found in code")
    print()
    
    # Summary
    print("SUMMARY")
    print("-" * 30)
    issues_found = (
        dep_check.get('vulnerabilities_found', False) or
        outdated_check.get('outdated_found', False) or
        code_check.get('issues_found', False)
    )
    
    if issues_found:
        print("⚠️  Issues detected - please review the detailed report above")
        print("   Consider updating dependencies and fixing security issues")
    else:
        print("✅ No issues detected - good security posture!")
    
    print("=" * 50)


def save_report(report: Dict, filename: Optional[str] = None):
    """
    Save the security report to a file.
    
    Args:
        report: Security report dictionary
        filename: Output filename (default: security_report_YYYYMMDD.json)
    """
    if filename is None:
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"security_report_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nFull security report saved to: {filename}")


def main():
    """Main function to run the dependency audit."""
    # Change to the script's directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Generate report
    report = generate_report()
    
    # Print formatted report
    print_report(report)
    
    # Save detailed report to file
    save_report(report)
    
    # Exit with error code if issues found
    issues_found = (
        report['checks']['dependency_vulnerabilities'].get('vulnerabilities_found', False) or
        report['checks']['outdated_packages'].get('outdated_found', False) or
        report['checks']['code_security_scan'].get('issues_found', False)
    )
    
    if issues_found:
        print("\nSecurity issues were found. Please address them as soon as possible.")
        sys.exit(1)
    else:
        print("\nNo security issues found. Good job!")
        sys.exit(0)


if __name__ == "__main__":
    main()