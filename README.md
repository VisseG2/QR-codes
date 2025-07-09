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

3. Access the web interface at `http://localhost:5000/users` to manage users.
   A list of connected devices is available at `http://localhost:5000/devices`
   and the real-time monitor at `http://localhost:5000/monitor`.
   Devices should POST push data to `http://localhost:5000/device/push`.

User information is stored in `users.json` and device information in
`devices.json` in the application directory.

