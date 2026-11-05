const http = require('http');

http.get('http://127.0.0.1:8000/', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    console.log('HTTP Status:', res.statusCode);
    console.log('Contains btnLandingLangToggle:', data.includes('id="btnLandingLangToggle"'));
    console.log('Contains heroHeadline:', data.includes('data-i18n="heroHeadline"'));
    console.log('Contains btnLoginLangToggle:', data.includes('id="btnLoginLangToggle"'));
    console.log('Contains btnRegisterLangToggle:', data.includes('id="btnRegisterLangToggle"'));
  });
}).on('error', err => console.error('Fetch error:', err.message));
