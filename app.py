from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    url_for,
    render_template_string,
)
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)
USERS_FILE = 'users.json'
DEVICES_FILE = 'devices.json'
COMMANDS_FILE = 'commands.json'

events = []  # in-memory list of recent events

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def load_devices():
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)


def load_commands():
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_commands(cmds):
    with open(COMMANDS_FILE, 'w') as f:
        json.dump(cmds, f, indent=2)


def _format_date(value: str) -> str:
    """Convert a YYYY-MM-DD or YYYY-MM-DD HH:MM string to YYYYMMDD or return 0."""
    if not value:
        return "0"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return "0"
    return dt.strftime("%Y%m%d")

@app.route('/device/push', methods=['POST'])
def device_push():
    """Endpoint for devices to push data."""
    data = request.get_json(force=True, silent=True) or request.form.to_dict()

    # Determine device identifier
    device_id = (
        data.get("SN")
        or data.get("sn")
        or data.get("device")
        or "unknown"
    )

    # Update devices info with last seen timestamp
    devices = load_devices()
    devices[device_id] = {"last_seen": datetime.now(timezone.utc).isoformat()}
    save_devices(devices)

    # Record event
    events.append({"device": device_id, "data": data, "ts": datetime.now(timezone.utc).isoformat()})
    if len(events) > 100:
        del events[0]

    return jsonify({"received": data}), 200


@app.route('/iclock/cdata', methods=['GET'])
def iclock_cdata():
    """Handle initial connection requests from devices."""
    sn = request.args.get('SN', request.args.get('sn', 'unknown'))
    devices = load_devices()
    device = devices.get(sn, {})
    device.setdefault('registered', False)
    device['last_seen'] = datetime.now(timezone.utc).isoformat()
    devices[sn] = device
    save_devices(devices)

    events.append({
        'device': sn,
        'endpoint': '/iclock/cdata',
        'data': request.args.to_dict(),
        'ts': datetime.now(timezone.utc).isoformat(),
    })
    if len(events) > 100:
        events.pop(0)

    if device.get('registered'):
        return 'registry=ok\nRegistryCode=0000\n', 200, {'Content-Type': 'text/plain'}
    return 'OK\n', 200, {'Content-Type': 'text/plain'}


@app.route('/iclock/registry', methods=['POST'])
def iclock_registry():
    """Register a device."""
    sn = request.args.get('SN') or request.form.get('SN') or request.form.get('sn', 'unknown')
    devices = load_devices()
    device = devices.get(sn, {})
    device['registered'] = True
    device['last_seen'] = datetime.now(timezone.utc).isoformat()
    device['info'] = request.form.to_dict()
    devices[sn] = device
    save_devices(devices)

    events.append({
        'device': sn,
        'endpoint': '/iclock/registry',
        'data': request.form.to_dict(),
        'ts': datetime.now(timezone.utc).isoformat(),
    })
    if len(events) > 100:
        events.pop(0)

    return 'registry=ok\nRegistryCode=0000\n', 200, {'Content-Type': 'text/plain'}

USERS_TEMPLATE = """
<!doctype html>
<title>Users</title>
<a href='{{ url_for('index') }}'>Home</a> |
<a href='{{ url_for('devices_page') }}'>Devices</a> |
<a href='{{ url_for('monitor_page') }}'>Monitor</a>
<h1>User List</h1>
<ul>
{% for uid, info in users.items() %}
  <li>{{ uid }} - card: {{ info['card'] }} - valid: {{ info['start'] }} &rarr; {{ info['end'] }}
    <form style='display:inline' method='post' action='{{ url_for('delete_user', uid=uid) }}'>
      <button type='submit'>Delete</button>
    </form>
  </li>
{% endfor %}
</ul>
<h2>Add User</h2>
<form method="post" action="{{ url_for('create_user') }}">
  ID: <input type="text" name="uid"><br>
  Card number: <input type="text" name="card"><br>
  Start (YYYY-MM-DD HH:MM): <input type="text" name="start"><br>
  End (YYYY-MM-DD HH:MM): <input type="text" name="end"><br>
  <input type="submit" value="Create">
</form>
"""

DEVICES_TEMPLATE = """
<!doctype html>
<title>Devices</title>
<a href='{{ url_for('index') }}'>Home</a> |
<a href='{{ url_for('users_page') }}'>Users</a> |
<a href='{{ url_for('monitor_page') }}'>Monitor</a>
<h1>Connected Devices</h1>
<ul>
{% for did, info in devices.items() %}
  <li>{{ did }} - last seen: {{ info['last_seen'] }}</li>
{% endfor %}
</ul>
"""

MONITOR_TEMPLATE = """
<!doctype html>
<title>Monitor</title>
<a href='{{ url_for('index') }}'>Home</a> |
<a href='{{ url_for('users_page') }}'>Users</a> |
<a href='{{ url_for('devices_page') }}'>Devices</a>
<h1>Real-time Events</h1>
<pre id='log'></pre>
<script>
async function fetchEvents() {
  const r = await fetch('{{ url_for('events_feed') }}');
  const data = await r.json();
  document.getElementById('log').textContent = JSON.stringify(data, null, 2);
}
setInterval(fetchEvents, 2000);
fetchEvents();
</script>
"""

@app.route('/users', methods=['GET'])
def users_page():
    users = load_users()
    return render_template_string(USERS_TEMPLATE, users=users)

@app.route('/users/create', methods=['POST'])
def create_user():
    uid = request.form.get('uid')
    card = request.form.get('card')
    start = request.form.get('start', '')
    end = request.form.get('end', '')
    if not uid or not card:
        return "Missing uid or card", 400
    users = load_users()
    users[uid] = {'card': card, 'start': start, 'end': end}
    save_users(users)

    # queue command to sync with devices
    devices = load_devices()
    cmds = load_commands()
    for sn, info in devices.items():
        if info.get('registered'):
            cmd_id = int(datetime.now(timezone.utc).timestamp())
            start_val = _format_date(start)
            end_val = _format_date(end)
            cmd = (
                f"C:{cmd_id}:DATA UPDATE user CardNo={card}\tPin={uid}\tPassword=\t"
                f"Group=1\tStartTime={start_val}\tEndTime={end_val}\t"
                "Name=\tPrivilege=0\tDisable=0"
            )
            cmds.setdefault(sn, []).append(cmd)
    save_commands(cmds)

    return redirect(url_for('users_page'))


@app.route('/devices', methods=['GET'])
def devices_page():
    devices = load_devices()
    return render_template_string(DEVICES_TEMPLATE, devices=devices)


@app.route('/')
def index():
    """Home page showing recent events."""
    return render_template_string(MONITOR_TEMPLATE)


@app.route('/monitor', methods=['GET'])
def monitor_page():
    return render_template_string(MONITOR_TEMPLATE)


@app.route('/events', methods=['GET'])
def events_feed():
    return jsonify(events)


@app.route('/iclock/getrequest', methods=['GET'])
def iclock_getrequest():
    """Provide queued commands for a device."""
    sn = request.args.get('SN', 'unknown')
    cmds = load_commands()
    device_cmds = cmds.get(sn, [])
    cmds[sn] = []
    save_commands(cmds)
    events.append({
        'device': sn,
        'endpoint': '/iclock/getrequest',
        'data': {'count': len(device_cmds)},
        'ts': datetime.now(timezone.utc).isoformat(),
    })
    if len(events) > 100:
        events.pop(0)
    if device_cmds:
        return '\n'.join(device_cmds) + '\n', 200, {'Content-Type': 'text/plain'}
    return 'OK\n', 200, {'Content-Type': 'text/plain'}


@app.route('/iclock/devicecmd', methods=['POST'])
def iclock_devicecmd():
    sn = request.args.get('SN') or request.form.get('SN', 'unknown')
    events.append({
        'device': sn,
        'endpoint': '/iclock/devicecmd',
        'data': request.form.to_dict(),
        'ts': datetime.now(timezone.utc).isoformat(),
    })
    if len(events) > 100:
        events.pop(0)
    return 'OK\n', 200, {'Content-Type': 'text/plain'}


@app.route('/users/delete/<uid>', methods=['POST'])
def delete_user(uid):
    users = load_users()
    users.pop(uid, None)
    save_users(users)

    devices = load_devices()
    cmds = load_commands()
    for sn, info in devices.items():
        if info.get('registered'):
            cmd_id = int(datetime.now(timezone.utc).timestamp())
            cmd = f"C:{cmd_id}:DATA DELETE user Pin={uid}"
            cmds.setdefault(sn, []).append(cmd)
    save_commands(cmds)

    return redirect(url_for('users_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
