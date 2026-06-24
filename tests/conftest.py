"""Pytest configuration and shared fixtures."""
import sys
import os
import pytest

# Ensure the project root is on sys.path for all tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "pipeone_test")
os.environ.setdefault("POSTGRES_USER", "pipeone_user")
os.environ.setdefault("POSTGRES_PASSWORD", "pipeone_pass")
os.environ.setdefault("GITHUB_TOKEN", "test_token")
os.environ.setdefault("LOG_LEVEL", "WARNING")
