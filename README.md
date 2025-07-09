# ZKTeco Push SDK Demo Web Interface

This repository contains a small Flask web application that accepts push
requests from ZKTeco devices. It provides simple pages to manage users,
view connected devices and monitor events in real time.

## Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

3. Access the web interface:
   - `http://localhost:5000/` shows recent device events.
   - `http://localhost:5000/users` manages users.
   - `http://localhost:5000/devices` lists connected devices.
   - `http://localhost:5000/monitor` also displays events in real time.
   Devices should POST push data to `http://localhost:5000/device/push` and
   use `/iclock/cdata` and `/iclock/registry` to connect as described in the
   ZKTeco PUSH protocol.

User information is stored in `users.json` and device information in
`devices.json` in the application directory.
