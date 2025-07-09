import json
from app import app, load_users, save_users, events


def test_create_user(client):
    response = client.post('/users/create', data={
        'uid': '1',
        'card': '1234',
        'start': '2025-01-01 00:00',
        'end': '2025-12-31 23:59'
    })
    assert response.status_code == 302  # redirect
    users = load_users()
    assert users.get('1') == {
        'card': '1234',
        'start': '2025-01-01 00:00',
        'end': '2025-12-31 23:59'
    }


def test_device_push(client):
    events.clear()
    response = client.post('/device/push', json={'event': 'test', 'SN': 'dev1'})
    assert response.status_code == 200
    assert response.get_json()['received'] == {'event': 'test', 'SN': 'dev1'}
    feed = client.get('/events')
    assert any(e['data'].get('event') == 'test' for e in feed.get_json())



def setup_module(module):
    save_users({})


def teardown_module(module):
    save_users({})
