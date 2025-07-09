from flask import Flask, request, jsonify, redirect, url_for, render_template_string
import json
import os

app = Flask(__name__)
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/device/push', methods=['POST'])
def device_push():
    """Endpoint for devices to push data."""
    data = request.get_json(force=True, silent=True) or request.form.to_dict()
    # For demo purposes we just return the data back
    return jsonify({'received': data}), 200

ADMIN_TEMPLATE = """
<!doctype html>
<title>User Admin</title>
<h1>User List</h1>
<ul>
{% for uid, info in users.items() %}
  <li>{{ uid }} - card: {{ info['card'] }}</li>
{% endfor %}
</ul>
<h2>Add User</h2>
<form method="post" action="{{ url_for('create_user') }}">
  ID: <input type="text" name="uid"><br>
  Card number: <input type="text" name="card"><br>
  <input type="submit" value="Create">
</form>
"""

@app.route('/admin', methods=['GET'])
def admin_index():
    users = load_users()
    return render_template_string(ADMIN_TEMPLATE, users=users)

@app.route('/admin/create', methods=['POST'])
def create_user():
    uid = request.form.get('uid')
    card = request.form.get('card')
    if not uid or not card:
        return "Missing uid or card", 400
    users = load_users()
    users[uid] = {'card': card}
    save_users(users)
    return redirect(url_for('admin_index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
