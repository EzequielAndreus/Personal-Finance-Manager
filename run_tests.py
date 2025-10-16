#!/usr/bin/env python3
"""
Test runner script for the milestone-1 project
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function"""
    print("🧪 Milestone-1 Test Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: pyproject.toml not found. Please run from project root.")
        sys.exit(1)
    
    # Check if pytest is available
    try:
        subprocess.run(["pytest", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: pytest not found. Please install it with: uv add pytest")
        sys.exit(1)
    
    # Test commands to run
    test_commands = [
        ("pytest tests/ -v", "All tests"),
        ("pytest tests/ -m unit -v", "Unit tests only"),
        ("pytest tests/ -m integration -v", "Integration tests only"),
    ]
    
    # Check if pytest-cov is available for coverage testing
    try:
        subprocess.run(["pytest", "--help"], check=True, capture_output=True, text=True)
        if "--cov" in subprocess.run(["pytest", "--help"], capture_output=True, text=True).stdout:
            test_commands.append(("pytest tests/ --cov=src --cov=models --cov-report=term-missing", "Tests with coverage"))
    except:
        pass
    
    # Run tests
    success_count = 0
    total_count = len(test_commands)
    
    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Test Summary: {success_count}/{total_count} test suites passed")
    print(f"{'='*60}")
    
    if success_count == total_count:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
