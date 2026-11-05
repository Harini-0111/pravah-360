const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');

const fields = ['regFullName', 'regEmail', 'regPassword', 'regConfirmPassword', 'regDistrict', 'regMandal', 'dedicatedRegisterFeedback', 'btnRegisterSubmit'];
fields.forEach(f => {
  console.log(`${f}: in html?`, html.includes(`id="${f}"`));
});
