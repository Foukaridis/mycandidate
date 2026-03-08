import pytest
from app import db

def test_get_ward_candidates(client):
    """
    Test the GET /api/v1/wards/<ward_id>/candidates endpoint.
    Since the candidates table is created dynamically, we create it manually for the test.
    """
    with client.application.app_context():
        # Create the dynamic table with all expected fields
        db.session.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_type TEXT,
                locator TEXT,
                ward_id TEXT,
                name TEXT,
                party TEXT,
                orderno TEXT
            )
        """)
        # Insert mock candidates
        # locator format: {code_column, name_column}
        db.session.execute("""
            INSERT INTO candidates (candidate_type, locator, ward_id, name, party, orderno)
            VALUES ('ward', 'ward_id,name', '12345', 'John Candidate', 'Party A', '1')
        """)
        db.session.execute("""
            INSERT INTO candidates (candidate_type, locator, ward_id, name, party, orderno)
            VALUES ('ward', 'ward_id,name', '12345', 'Jane Candidate', 'Party B', '2')
        """)
        db.session.commit()

    # Call the API endpoint
    response = client.get('/api/v1/wards/12345/candidates')
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'John Candidate'
    assert data[0]['ward_id'] == '12345'
    assert data[0]['party'] == 'Party A'
    assert data[1]['name'] == 'Jane Candidate'
    assert data[1]['party'] == 'Party B'


def test_get_ward_candidates_empty(client):
    """
    Test the endpoint with a ward_id that has no candidates.
    Should return empty array with 200 status.
    """
    with client.application.app_context():
        # Create empty table
        db.session.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_type TEXT,
                locator TEXT,
                ward_id TEXT,
                name TEXT,
                party TEXT,
                orderno TEXT
            )
        """)
        db.session.commit()
    
    response = client.get('/api/v1/wards/99999/candidates')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_ward_candidates_single(client):
    """
    Test the endpoint with a single candidate.
    """
    with client.application.app_context():
        db.session.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_type TEXT,
                locator TEXT,
                ward_id TEXT,
                name TEXT,
                party TEXT,
                orderno TEXT
            )
        """)
        db.session.execute("""
            INSERT INTO candidates (candidate_type, locator, ward_id, name, party, orderno)
            VALUES ('ward', 'ward_id,name', 'WARD-001', 'Alice Candidate', 'Independent', '1')
        """)
        db.session.commit()
    
    response = client.get('/api/v1/wards/WARD-001/candidates')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Alice Candidate'
    assert data[0]['party'] == 'Independent'

