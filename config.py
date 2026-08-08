"""
config.py — Application Configuration
======================================
WHY THIS FILE EXISTS:
    Centralizes ALL configuration (database URI, API keys, secret keys)
    in one place. This follows the 'Separation of Concerns' principle.
    Never hardcode secrets in your route files.

    Flask reads from this class via app.config.from_object(Config).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    # Flask secret key for session management & CSRF protection
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLite database path — stored inside /instance folder (Flask convention)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///app.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable overhead of tracking changes

    # Mistral AI API configuration
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
    MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
