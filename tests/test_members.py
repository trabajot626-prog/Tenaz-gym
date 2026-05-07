"""Member CRUD operation tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest


VALID_MEMBER = {
    'name': 'Juan',
    'last_name': 'García',
    'id_number': '123456',
    'phone': '+573001234567',
    'email': 'juan@example.com',
    'plan_id': 1,
    'registration_date': '2026-01-01'
}


class TestCreateMember:
    def test_create_member_success(self, auth_client):
        res = auth_client.post('/api/members', json=VALID_MEMBER)
        assert res.status_code == 201
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Juan'
        assert data['data']['last_name'] == 'García'
        assert data['data']['id'] == 1

    def test_create_member_requires_auth(self, client):
        res = client.post('/api/members', json=VALID_MEMBER)
        assert res.status_code == 401

    def test_create_member_missing_name(self, auth_client):
        res = auth_client.post('/api/members', json={**VALID_MEMBER, 'name': ''})
        assert res.status_code == 400
        assert res.get_json()['success'] is False

    def test_create_member_missing_phone(self, auth_client):
        member = {**VALID_MEMBER, 'phone': ''}
        res = auth_client.post('/api/members', json=member)
        assert res.status_code == 400

    def test_create_member_duplicate_id_number(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        res = auth_client.post('/api/members', json={**VALID_MEMBER, 'name': 'Pedro'})
        assert res.status_code == 400
        assert res.get_json()['success'] is False

    def test_create_multiple_members(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        auth_client.post('/api/members', json={**VALID_MEMBER, 'id_number': '999', 'name': 'Pedro'})
        res = auth_client.get('/api/members')
        assert len(res.get_json()['data']) == 2


class TestReadMember:
    def test_list_members_empty(self, auth_client):
        res = auth_client.get('/api/members')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data'] == []

    def test_list_members_with_data(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        res = auth_client.get('/api/members')
        assert len(res.get_json()['data']) == 1

    def test_get_member_by_id(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        res = auth_client.get('/api/members/1')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['id'] == 1

    def test_get_member_not_found(self, auth_client):
        res = auth_client.get('/api/members/999')
        assert res.status_code == 404

    def test_search_by_name(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        auth_client.post('/api/members', json={**VALID_MEMBER, 'name': 'Pedro', 'id_number': '999'})
        res = auth_client.get('/api/members?search=Pedro')
        data = res.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Pedro'


class TestUpdateMember:
    def test_update_member_name(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        res = auth_client.put('/api/members/1', json={**VALID_MEMBER, 'name': 'Carlos'})
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Carlos'

    def test_update_member_not_found(self, auth_client):
        res = auth_client.put('/api/members/999', json=VALID_MEMBER)
        assert res.status_code == 404

    def test_update_member_requires_auth(self, client):
        res = client.put('/api/members/1', json=VALID_MEMBER)
        assert res.status_code == 401


class TestDeleteMember:
    def test_delete_member(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        res = auth_client.delete('/api/members/1')
        assert res.status_code == 200
        assert res.get_json()['success'] is True

    def test_deleted_member_not_found(self, auth_client):
        auth_client.post('/api/members', json=VALID_MEMBER)
        auth_client.delete('/api/members/1')
        res = auth_client.get('/api/members/1')
        assert res.status_code == 404

    def test_delete_member_not_found(self, auth_client):
        res = auth_client.delete('/api/members/999')
        assert res.status_code == 404

    def test_delete_member_requires_auth(self, client):
        res = client.delete('/api/members/1')
        assert res.status_code == 401
