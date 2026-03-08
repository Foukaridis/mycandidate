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
    
    For Docker/CI: Set DB_HOST=db and DB_PORT=5432 (uses service name)
    For local with docker-compose: Defaults to localhost:5433 (docker-compose exposes on 5433)
    For local with system postgres: Set DB_PORT=5432
    """
    app.config['TESTING'] = True
    
    # Use environment variable for database URL if provided
    # Default to localhost for local development with docker-compose
    # docker-compose exposes PostgreSQL on port 5433 (container 5432)
    # In docker-compose network: set DB_HOST=db DB_PORT=5432
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_port = os.getenv('DB_PORT', '5433')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/mycandidate_test'
    )

    client = app.test_client()

    with app.app_context():
        db.create_all()
        # Clean up any raw SQL tables from previous tests
        try:
            db.session.execute('DROP TABLE IF EXISTS candidates CASCADE')
            db.session.commit()
        except Exception:
            pass

    yield client

    with app.app_context():
        # Clean up all tables
        try:
            db.session.execute('DROP TABLE IF EXISTS candidates CASCADE')
            db.session.commit()
        except Exception:
            pass
        db.drop_all()

