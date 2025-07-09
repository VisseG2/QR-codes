import json
from app import app, load_users, save_users


def test_create_user(client):
    response = client.post('/admin/create', data={'uid': '1', 'card': '1234'})
    assert response.status_code == 302  # redirect
    users = load_users()
    assert users.get('1') == {'card': '1234'}


def test_device_push(client):
    response = client.post('/device/push', json={'event': 'test'})
    assert response.status_code == 200
    assert response.get_json()['received'] == {'event': 'test'}


def setup_module(module):
    save_users({})


def teardown_module(module):
    save_users({})
