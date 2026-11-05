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
  console.log('Testing /api/v1/weather/current...');
  try {
    const res = await getJson('/api/v1/weather/current?lat=16.9850&lon=81.7800');
    console.log('Weather status:', res.status);
    console.log('Weather data sample:', JSON.stringify(res.data).slice(0, 300));
  } catch (e) {
    console.error('Weather error:', e.message);
  }

  console.log('\nTesting /api/v1/infrastructure/facilities...');
  try {
    const res = await getJson('/api/v1/infrastructure/facilities?limit=10&study_area_only=true');
    console.log('Facilities status:', res.status);
    if (res.data && res.data.features) {
      console.log('Facilities count:', res.data.features.length);
      console.log('Sample facility:', res.data.features[0]?.properties);
    }
  } catch (e) {
    console.error('Facilities error:', e.message);
  }

  console.log('\nTesting /api/v1/monitoring/river-stages...');
  try {
    const res = await getJson('/api/v1/monitoring/river-stages');
    console.log('River stages status:', res.status);
    console.log('Sample stage:', res.data ? res.data[0] : null);
  } catch (e) {
    console.error('River stages error:', e.message);
  }
}

run();
