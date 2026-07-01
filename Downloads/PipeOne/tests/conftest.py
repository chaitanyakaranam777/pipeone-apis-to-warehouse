"""
Shared pytest configuration and fixtures for the PipeOne test suite.

All tests run without a live PostgreSQL — the loader and DB tests use
an in-memory SQLite database via monkeypatching or scoped fixtures.
"""
import sys
import os
import pytest

# Project root on sys.path for all test modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test environment variables — override any .env settings
os.environ.update({
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "pipeone_test",
    "POSTGRES_USER": "pipeone_user",
    "POSTGRES_PASSWORD": "pipeone_pass",
    "GITHUB_TOKEN": "test_token_ci",
    "LOG_LEVEL": "WARNING",       # Suppress info logs during tests
    "ENVIRONMENT": "test",
})
