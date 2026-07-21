from http.server import BaseHTTPRequestHandler
import json
import random
from datetime import datetime, timedelta

keys_db = [
    {"key": "ALVIN-VIP-001", "expiry": "2026-12-31", "maxDevices": 1, "devices": []},
    {"key": "ALVIN-VIP-002", "expiry": "2026-12-31", "maxDevices": 3, "devices": []},
]

ADMIN_SECRET = "alvinadmin123"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        self.send_json({"status": "ALVIN KEY API", "endpoints": ["/api/validate", "/api/admin/generate"]})

    def do_POST(self):
        path = self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        if path == '/api/validate':
            self.handle_validate(data)
        elif path == '/api/admin/generate':
            self.handle_generate(data)
        else:
            self.send_json({"error": "Not found"}, 404)

    def handle_validate(self, data):
        key = data.get('key')
        device_id = data.get('device_id')
        
        if not key or not device_id:
            self.send_json({"valid": False, "error": "Missing params"}, 400)
            return

        found = next((k for k in keys_db if k["key"] == key), None)
        
        if not found:
            self.send_json({"valid": False, "error": "Key not found"}, 404)
            return

        now = datetime.now()
        expiry = datetime.strptime(found["expiry"], "%Y-%m-%d")
        if now > expiry:
            self.send_json({"valid": False, "error": "Key expired"}, 403)
            return

        if device_id not in found["devices"]:
            if len(found["devices"]) >= found["maxDevices"]:
                self.send_json({"valid": False, "error": "Device limit reached"}, 403)
                return
            found["devices"].append(device_id)

        self.send_json({"valid": True, "key": found["key"], "expiry": found["expiry"]})

    def handle_generate(self, data):
        if data.get('secret') != ADMIN_SECRET:
            self.send_json({"error": "Unauthorized"}, 401)
            return

        random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        key = f"{data.get('prefix', 'ALVIN-VIP')}-{random_part}"
        expiry = datetime.now() + timedelta(days=int(data.get('days', 30)))
        
        keys_db.append({
            "key": key,
            "expiry": expiry.strftime("%Y-%m-%d"),
            "maxDevices": int(data.get('maxDevices', 1)),
            "devices": []
        })

        self.send_json({"key": key, "expiry": expiry.strftime("%Y-%m-%d")})

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
