# ZKTeco Push SDK Demo Web Interface

This repository contains a small Flask web application that accepts push
requests from ZKTeco devices and lets an administrator create users with
assigned card numbers.

## Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

3. Access the admin interface at `http://localhost:5000/admin` to create users.
Devices can POST data to `http://localhost:5000/device/push`.

User information is stored in `users.json` in the application directory.
