"""
Pytest configuration and fixtures

Sets up test environment variables
"""
import os
import pytest

# Set test environment variables before any app modules are imported
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'
os.environ['PLAID_CLIENT_ID'] = 'test-plaid-client'
os.environ['PLAID_SECRET'] = 'test-plaid-secret'
os.environ['GOOGLE_MAPS_API_KEY'] = 'test-maps-key'
os.environ['GOOGLE_PLACES_API_KEY'] = 'test-places-key'
os.environ['ENCRYPTION_KEY'] = 'test-encryption-key-32bytes!!'
os.environ['PLAID_ENV'] = 'sandbox'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
