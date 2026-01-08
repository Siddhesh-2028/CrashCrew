import os
import json
import tempfile
import pytest

from app import create_app
from extensions import db


@pytest.fixture
def app():
    # Use a temporary file for sqlite to avoid interfering with real db
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-jwt-secret',
    }

    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()

    yield app

    # teardown
    try:
        os.remove(db_path)
    except OSError:
        pass


def test_register_and_create_profile(client):
    # Register
    resp = client.post('/api/auth/register', json={
        'username': 'pytestuser',
        'email': 'pytest@example.com',
        'password': 'testpass'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['message'] == 'User registered successfully'
    user_id = data['user_id']

    # Create profile
    profile_payload = {
        'user_id': user_id,
        'living_arrangement': 'Apartment',
        'pays_electricity': True,
        'household_size': '1',
        'uses_ac': False,
        'appliances_used': ['Refrigerator'],
        'primary_transport': 'walk',
        'owns_vehicle': 'none',
        'diet_type': 'veg',
        'eating_out_frequency': 'rarely',
        'life_stage': 'student',
        'sustainability_interest': 'somewhat'
    }

    resp2 = client.post('/api/profile/create', json=profile_payload)
    assert resp2.status_code == 201
    data2 = resp2.get_json()
    assert data2['message'] == 'Profile created successfully'
