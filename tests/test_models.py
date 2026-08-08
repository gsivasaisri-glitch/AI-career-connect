"""
tests/test_models.py — Model Unit Tests
=========================================
Verifies that ORM models behave correctly: creation,
relationships, and password hashing.
"""

# pyrefly: ignore [missing-import]
from app.models.user import User
# pyrefly: ignore [missing-import]
from app.models.career_profile import CareerProfile
# pyrefly: ignore [missing-import]
from app.models.chat_history import ChatHistory


def test_user_creation(db):
    """A new user can be created and persisted."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("securepass")
    db.session.add(user)
    db.session.commit()

    fetched = User.query.filter_by(email="test@example.com").first()
    assert fetched is not None
    assert fetched.username == "testuser"


def test_password_hashing(db):
    """Password hashing produces a non-plaintext hash and verifies correctly."""
    user = User(username="hashtest", email="hash@example.com")
    user.set_password("my_password")
    db.session.add(user)
    db.session.commit()

    assert user.password_hash != "my_password"
    assert user.check_password("my_password") is True
    assert user.check_password("wrong_password") is False


def test_career_profile_relationship(db):
    """A career profile is linked to its owning user."""
    user = User(username="proftest", email="prof@example.com")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()

    profile = CareerProfile(user_id=user.id, skills="Python, SQL")
    db.session.add(profile)
    db.session.commit()

    assert len(user.career_profiles) == 1
    assert user.career_profiles[0].skills == "Python, SQL"