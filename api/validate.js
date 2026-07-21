// api/validate.js
module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ valid: false });

  const { key, device_id } = req.body;
  if (!key || !device_id) {
    return res.status(400).json({ valid: false, error: 'Missing params' });
  }

  // ===== DATABASE KEY (hardcoded) =====
  const keysDB = [
    { key: "ALVIN-VIP-001", expiry: "2026-12-31", maxDevices: 1, devices: [] },
    { key: "ALVIN-VIP-002", expiry: "2026-12-31", maxDevices: 3, devices: [] },
    { key: "ALVIN-VIP-003", expiry: "2026-08-01", maxDevices: 1, devices: [] },
  ];

  const found = keysDB.find(k => k.key === key);

  if (!found) {
    return res.status(404).json({ valid: false, error: "Key not found", code: 404 });
  }

  const now = new Date();
  const expiry = new Date(found.expiry);
  if (now > expiry) {
    return res.status(403).json({ valid: false, error: "Key expired", code: 403 });
  }

  // Device check
  if (!found.devices.includes(device_id)) {
    if (found.devices.length >= found.maxDevices) {
      return res.status(403).json({ 
        valid: false, 
        error: "Device limit reached", 
        code: 403 
      });
    }
    found.devices.push(device_id);
  }

  return res.status(200).json({
    valid: true,
    key: found.key,
    expiry: found.expiry,
    message: "Access granted"
  });
};
