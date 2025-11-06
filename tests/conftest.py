import pytest
import tempfile
import os
from datetime import datetime, date
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from utils.db_init import init_db
from models import db, User, Expense


@pytest.fixture(scope="session")
def app_config():
    """Configuration for testing"""
    test_db_url = os.getenv(
        "TEST_DATABASE_URL", 
        "postgresql+psycopg2://postgres:password@localhost/test_milestone_1"
    )
    return {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": test_db_url,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
    }


@pytest.fixture(scope="function")
def test_app(app_config):
    """Create a test Flask application"""
    app = create_app()
    app.config.update(app_config)
    
    with app.app_context():
        # Drop all tables and recreate them for clean state
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client"""
    return test_app.test_client()


@pytest.fixture(scope="function")
def db_session(test_app):
    """Create a database session for testing"""
    with test_app.app_context():
        yield db.session


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(username="testuser", is_admin=False)
    user.set_password("testpassword")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(username="admin", is_admin=True)
    user.set_password("admin")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_expense(db_session, sample_user):
    """Create a sample expense for testing"""
    expense = Expense(
        name="Test Expense",
        amount=100.50,
        category="Food",
        date=date.today(),
        user_id=sample_user.id,
        comment="Test comment"
    )
    db_session.add(expense)
    db_session.commit()
    return expense


@pytest.fixture
def sample_debt(db_session, sample_user):
    """Create a sample debt for testing"""
    debt = Expense(
        name="Test Debt",
        amount=250.00,
        category="Utilities",
        date=date.today(),
        due_date=date.today(),
        user_id=sample_user.id,
        comment="Test debt"
    )
    db_session.add(debt)
    db_session.commit()
    return debt


@pytest.fixture
def authenticated_client(client, sample_user):
    """Create an authenticated test client"""
    with client.session_transaction() as sess:
        sess["user_id"] = sample_user.id
        sess["username"] = sample_user.username
        sess["is_admin"] = sample_user.is_admin
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Create an authenticated admin test client"""
    with client.session_transaction() as sess:
        sess["user_id"] = admin_user.id
        sess["username"] = admin_user.username
        sess["is_admin"] = admin_user.is_admin
    return client
