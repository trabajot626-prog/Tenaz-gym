"""Basic authentication tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest


class TestLogin:
    def test_login_success(self, client):
        res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'gym123'})
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'admin'

    def test_login_wrong_password(self, client):
        res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'wrong'})
        assert res.status_code == 401
        data = res.get_json()
        assert data['success'] is False

    def test_login_wrong_username(self, client):
        res = client.post('/api/auth/login', json={'username': 'unknown', 'password': 'gym123'})
        assert res.status_code == 401
        assert res.get_json()['success'] is False

    def test_login_empty_credentials(self, client):
        res = client.post('/api/auth/login', json={'username': '', 'password': ''})
        assert res.status_code == 401

    def test_login_missing_body(self, client):
        res = client.post('/api/auth/login', data='not-json', content_type='text/plain')
        assert res.status_code == 401


class TestLogout:
    def test_logout_when_authenticated(self, auth_client):
        res = auth_client.post('/api/auth/logout')
        assert res.status_code == 200
        assert res.get_json()['success'] is True

    def test_session_cleared_after_logout(self, auth_client):
        auth_client.post('/api/auth/logout')
        res = auth_client.get('/api/auth/status')
        assert res.get_json()['data']['logged_in'] is False

    def test_protected_endpoint_after_logout(self, auth_client):
        auth_client.post('/api/auth/logout')
        res = auth_client.get('/api/members')
        assert res.status_code == 401


class TestAuthStatus:
    def test_status_unauthenticated(self, client):
        res = client.get('/api/auth/status')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['logged_in'] is False

    def test_status_authenticated(self, auth_client):
        res = auth_client.get('/api/auth/status')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['logged_in'] is True

    def test_protected_route_requires_auth(self, client):
        res = client.get('/api/members')
        assert res.status_code == 401

    def test_health_is_public(self, client):
        res = client.get('/api/health')
        assert res.status_code == 200
        assert res.get_json()['success'] is True
