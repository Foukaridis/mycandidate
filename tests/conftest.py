import pytest
import os, tempfile
from main.database.session import SessionLocal
from typing import Generator
from app import app, db


@pytest.fixture
def client() -> Generator:
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/mycandidate_test'

    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()
