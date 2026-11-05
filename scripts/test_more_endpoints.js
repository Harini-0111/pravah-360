const http = require('http');

function getJson(path) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:8000${path}`, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
        catch (e) { resolve({ status: res.statusCode, raw: data }); }
      });
    }).on('error', reject);
  });
}

async function run() {
  console.log('Testing /api/v1/weather/forecast...');
  try {
    const res = await getJson('/api/v1/weather/forecast?lat=16.9850&lon=81.7800');
    console.log('Forecast status:', res.status, JSON.stringify(res.data).slice(0, 200));
  } catch (e) {
    console.error('Forecast error:', e.message);
  }

  console.log('Testing /api/v1/risk/mandal/Rajahmundry...');
  try {
    const res = await getJson('/api/v1/risk/mandal/Rajahmundry');
    console.log('Risk mandal status:', res.status, JSON.stringify(res.data).slice(0, 200));
  } catch (e) {
    console.error('Risk mandal error:', e.message);
  }
}

run();
