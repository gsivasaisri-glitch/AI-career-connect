"""
tests/conftest.py — Pytest Fixtures
=====================================
Shared fixtures that spin up a test-configured Flask app
and provide a test client + clean database per test.
"""

# pyrefly: ignore [missing-import]
import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing."""
    app = create_app("test")
    yield app


@pytest.fixture(scope="function")
def client(app):
    """Provide a Flask test client with a fresh database."""
    with app.test_client() as client:
        with app.app_context():
            _db.create_all()
            yield client
            _db.session.remove()
            _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide the SQLAlchemy db instance inside an app context."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()