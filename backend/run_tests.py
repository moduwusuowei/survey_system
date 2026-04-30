"""Run tests script."""
import pytest
import sys

if __name__ == "__main__":
    # Run all tests with coverage
    result = pytest.main([
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term"
    ])
    
    sys.exit(result)
