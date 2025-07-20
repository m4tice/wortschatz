#!/usr/bin/env python3
"""
Test runner script for the Wortschatz application.
Provides convenient commands to run different test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Wortschatz application tests")
    parser.add_argument("--suite", choices=["all", "unit", "integration", "auth", "db", "utils", "wortschatz"], 
                       default="all", help="Test suite to run")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Run only fast tests")
    
    args = parser.parse_args()
    
    # Base python command
    python_cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        python_cmd.append("-v")
    
    # Add coverage if requested
    if args.coverage:
        python_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add fast filter if requested
    if args.fast:
        python_cmd.extend(["-m", "not slow"])
    
    # Determine test suite
    success = True
    
    if args.suite == "all":
        # Run all tests
        cmd = python_cmd + ["tests/"]
        success = run_command(cmd, "All Tests")
        
    elif args.suite == "unit":
        # Run unit tests only
        cmd = python_cmd + ["-m", "unit", "tests/"]
        success = run_command(cmd, "Unit Tests")
        
    elif args.suite == "integration":
        # Run integration tests
        cmd = python_cmd + ["tests/test_integration.py"]
        success = run_command(cmd, "Integration Tests")
        
    elif args.suite == "auth":
        # Run authentication tests
        cmd = python_cmd + ["tests/test_authentication.py", "tests/test_authenticator.py"]
        success = run_command(cmd, "Authentication Tests")
        
    elif args.suite == "db":
        # Run database tests
        cmd = python_cmd + ["tests/test_database.py"]
        success = run_command(cmd, "Database Tests")
        
    elif args.suite == "utils":
        # Run utility tests
        cmd = python_cmd + ["tests/test_utils.py"]
        success = run_command(cmd, "Utility Tests")
        
    elif args.suite == "wortschatz":
        # Run wortschatz module tests
        cmd = python_cmd + ["tests/test_wortschatz.py"]
        success = run_command(cmd, "Wortschatz Module Tests")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
