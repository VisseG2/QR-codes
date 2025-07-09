import json
from app import (
    app,
    load_users,
    save_users,
    load_devices,
    save_devices,
    load_commands,
    save_commands,
    events,
)


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


def test_root_and_iclock(client):
    events.clear()

    resp = client.get('/')
    assert resp.status_code == 200

    # initial connection
    resp = client.get('/iclock/cdata?SN=testdev&options=all')
    assert resp.status_code == 200
    assert b'OK' in resp.data

    # register device
    resp = client.post('/iclock/registry?SN=testdev', data={'DeviceType': 'acc'})
    assert resp.status_code == 200
    assert b'registry=ok' in resp.data

    resp = client.get('/iclock/cdata?SN=testdev&options=all')
    assert b'registry=ok' in resp.data

    devices = load_devices()
    assert devices['testdev']['registered'] is True


def test_user_sync(client):
    events.clear()
    client.get('/iclock/cdata?SN=mydev&options=all')
    client.post('/iclock/registry?SN=mydev')

    client.post('/users/create', data={'uid': '55', 'card': '9999'})

    resp = client.get('/iclock/getrequest?SN=mydev')
    body = resp.get_data(as_text=True)
    assert 'DATA UPDATE user' in body
    # commands should be cleared after retrieval
    resp = client.get('/iclock/getrequest?SN=mydev')
    assert resp.data == b''


def setup_module(module):
    save_users({})
    save_devices({})
    save_commands({})


def teardown_module(module):
    save_users({})
    save_devices({})
    save_commands({})
