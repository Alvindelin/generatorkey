// api/admin/generate.js

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const ADMIN_KEY = process.env.ADMIN_SECRET || "alvinadmin123";
  const { secret, days, maxDevices, prefix } = req.body;

  if (secret !== ADMIN_KEY) {
    return res.status(401).json({ error: 'Invalid admin secret' });
  }

  // Generate random key
  const randomPart = Math.random().toString(36).substring(2, 8).toUpperCase();
  const key = `${prefix || 'ALVIN-VIP'}-${randomPart}`;
  
  const expiry = new Date();
  expiry.setDate(expiry.getDate() + (parseInt(days) || 30));

  return res.status(200).json({
    key: key,
    expiry: expiry.toISOString().split('T')[0],
    maxDevices: parseInt(maxDevices) || 1,
    status: "active",
    generatedAt: new Date().toISOString()
  });
}
