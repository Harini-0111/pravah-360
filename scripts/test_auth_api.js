const http = require('http');

function postJson(path, body) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(body);
    const req = http.request({
      hostname: '127.0.0.1',
      port: 8000,
      path: path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    }, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, data: JSON.parse(data) }));
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function run() {
  const accounts = [
    { email: 'citizen@pravah360.in', pass: 'Citizen@123' },
    { email: 'mandal.admin@pravah360.in', pass: 'Mandal@123' },
    { email: 'district.collector@pravah360.in', pass: 'District@123' },
    { email: 'ert.commander@pravah360.in', pass: 'Responder@123' }
  ];

  for (const acc of accounts) {
    try {
      const res = await postJson('/api/v1/auth/login', {
        email: acc.email,
        password: acc.pass
      });
      console.log(`Login result (${acc.email}): status=${res.status}, role=${res.data.user?.role}`);
    } catch (e) {
      console.error(`Login error (${acc.email}):`, e.message);
    }
  }
}

run();
