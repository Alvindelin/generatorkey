# api/index.py
# Vercel Python Serverless Function

from http.server import BaseHTTPRequestHandler
import json
import random
from datetime import datetime, timedelta

# ===== DATABASE KEY (sementara in-memory) =====
# Di production pake database (MongoDB, Supabase, dll)
keys_db = [
    {"key": "ALVIN-VIP-001", "expiry": "2026-12-31", "maxDevices": 1, "devices": []},
    {"key": "ALVIN-VIP-002", "expiry": "2026-12-31", "maxDevices": 3, "devices": []},
    {"key": "ALVIN-VIP-003", "expiry": "2026-08-01", "maxDevices": 1, "devices": []},
]

ADMIN_SECRET = "alvinadmin123"

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        path = self.path
        
        if path == '/api/':
            self.send_json({"status": "ALVIN KEY API RUN path == '/api/':
            self.send_json({"status": "ALVIN KEY API RUNNING", "version": "1.0.0"})
        
        elif path.startswith('/api/admin/keys'):
            # List semua key (butuh admin secret di query)
            import urllib.parse
            parsed = urllib.parse.urlparse(path)
            params = urllib.parse.parse_qs(parsed.query)
            secret = params.get('secret', [''])[0]
            
            if secret != ADMIN_SECRET:
                self.send_json({"error": "Unauthorized"}, 401)
                return
            
            self.send_json({
                "keys": [{"key": k["key"], "expiry": k["expiry"], "devices": len(k["devices"])} for k in keys_db]
            })
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        # ===== VALIDATE KEY =====
        if path == '/api/validate':
            key = data.get('key')
            device_id = data.get('device_id')
            
            if not key or not device_id:
                self.send_json({"valid": False, "error": "Missing key or device_id"}, 400)
                return
            
            found = None
            for k in keys_db:
                if k["key"] == key:
                    found = k
                    break
            
            if not found:
                self.send_json({"valid": False, "error": "Key not found", "code": 404}, 404)
                return
            
            # Cek expiry
            now = datetime.now()
            expiry = datetime.strptime(found["expiry"], "%Y-%m-%d")
            if now > expiry:
                self.send_json({"valid": False, "error": "Key expired", "code": 403}, 403)
                return
            
            # Device check
            if device_id not in found["devices"]:
                if len(found["devices"]) >= found["maxDevices"]:
                    self.send_json({
                        "valid": False, 
                        "error": "Device limit reached", 
                        "maxDevices": found["maxDevices"],
                        "code": 403
                    }, 403)
                    return
                found["devices"].append(device_id)
            
            self.send_json({
                "valid": True,
                "key": found["key"],
                "expiry": found["expiry"],
                "message": "Access granted"
            })
        
        # ===== GENERATE KEY =====
        elif path == '/api/admin/generate':
            secret = data.get('secret')
            days = int(data.get('days', 30))
            max_devices = int(data.get('maxDevices', 1))
            prefix = data.get('prefix', 'ALVIN-VIP')
            
            if secret != ADMIN_SECRET:
                self.send_json({"error": "Invalid admin secret"}, 401)
                return
            
            random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
            new_key = f"{prefix}-{random_part}"
            
            expiry = datetime.now() + timedelta(days=days)
            
            key_data = {
                "key": new_key,
                "expiry": expiry.strftime("%Y-%m-%d"),
                "maxDevices": max_devices,
                "devices": []
            }
            keys_db.append(key_data)
            
            self.send_json({
                "key": new_key,
                "expiry": key_data["expiry"],
                "maxDevices": max_devices,
                "status": "active"
            })
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
                            
