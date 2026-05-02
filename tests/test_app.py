import json
import pytest
from unittest.mock import patch
from app import app, db, User


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_home_route(client):
    """GET / should return 200 and contain MindCare."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'MindCare' in response.data


def test_signup_auth_flow(client):
    """Test the signup and verify flow."""
    # 1. Signup
    response = client.post('/signup', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Verify Your Email' in response.data

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.is_verified is False
        otp = user.otp

    # 2. Verify OTP
    response = client.post('/verify', data={
        'otp': otp
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to MindCare AI' in response.data or b'Account verified' in response.data

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user.is_verified is True


def test_login_flow(client):
    """Test the login flow for verified user."""
    # Prepare verified user
    from werkzeug.security import generate_password_hash
    with app.app_context():
        user = User(name='Login User', email='login@example.com',
                    password_hash=generate_password_hash('abc12345'),
                    is_verified=True)
        db.session.add(user)
        db.session.commit()

    # Login
    response = client.post('/login', data={
        'email': 'login@example.com',
        'password': 'abc12345'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data


def test_analyze_missing_text(client):
    """POST /analyze with empty text should return 400."""
    response = client.post(
        '/analyze',
        data=json.dumps({'text': ''}),
        content_type='application/json'
    )
    assert response.status_code == 400


@patch('app.classify_and_respond')
def test_analyze_success(mock_classify, client):
    """POST /analyze with valid text should return 200 with all metadata."""
    mock_classify.return_value = {
        "stress_level": "HIGH",
        "mood_emoji": "🚨",
        "empathy": "I hear you, and I'm here for you.",
        "daily_affirmation": "You are strong.",
        "next_step": "Take a deep breath",
        "tips": ["Breathe"],
        "helplines": [{"name": "iCall", "number": "9152987821"}]
    }

    response = client.post(
        '/analyze',
        data=json.dumps({'text': 'I feel overwhelmed and cannot cope'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['stress_level'] == 'HIGH'
    assert data['mood_emoji'] == '🚨'
    assert data['daily_affirmation'] == 'You are strong.'
