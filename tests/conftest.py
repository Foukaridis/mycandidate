import pytest
import os
from main.database.session import SessionLocal
from typing import Generator
from app import app, db


@pytest.fixture
def client() -> Generator:
    """
    Test client fixture that sets up a clean test database for each test.
    Handles both Docker (with db service) and local testing environments.
    """
    app.config['TESTING'] = True
    
    # Use environment variable for database URL if provided, otherwise default
    db_host = os.getenv('DB_HOST', 'db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/mycandidate_test'
    )

    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

