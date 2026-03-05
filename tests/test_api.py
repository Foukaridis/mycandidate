import pytest
from app import db

def test_get_ward_candidates(client):
    """
    Test the GET /api/v1/wards/<ward_id>/candidates endpoint.
    Since the candidates table is created dynamically, we create it manually for the test.
    """
    with client.application.app_context():
        # Create the dynamic table
        db.session.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_type TEXT,
                locator TEXT,
                ward_id TEXT,
                name TEXT
            )
        """)
        # Insert a mock candidate
        # locator format: {code_column, name_column}
        db.session.execute("""
            INSERT INTO candidates (candidate_type, locator, ward_id, name)
            VALUES ('ward', '{ward_id,name}', '12345', 'John Candidate')
        """)
        db.session.commit()

    # Call the API endpoint
    response = client.get('/api/v1/wards/12345/candidates')
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'John Candidate'
    assert data[0]['ward_id'] == '12345'

def test_get_ward_candidates_empty(client):
    """
    Test the endpoint with a ward_id that has no candidates.
    """
    response = client.get('/api/v1/wards/99999/candidates')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0
