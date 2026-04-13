import sys
import os
import pytest

# Add backend to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set a dummy DATA_PATH before first import so the JSON file isn't created in cwd
os.environ.setdefault('DATA_PATH', '/dev/null')

import utils.data_manager as data_manager
import config as cfg_module
from app import app as flask_app


@pytest.fixture(autouse=True)
def isolate_data(tmp_path, monkeypatch):
    """Redirect all data I/O to a fresh per-test temp file."""
    data_file = str(tmp_path / 'gym_data.json')
    monkeypatch.setattr(cfg_module.Config, 'DATA_PATH', data_file)
    monkeypatch.setattr(data_manager.Config, 'DATA_PATH', data_file)


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SESSION_COOKIE_SECURE'] = False
    flask_app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    flask_app.secret_key = 'test-secret'
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post(
        '/api/auth/login',
        json={'username': 'admin', 'password': 'gym123'},
        content_type='application/json'
    )
    return client

