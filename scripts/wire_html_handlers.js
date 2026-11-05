const fs = require('fs');

let html = fs.readFileSync('frontend/index.html', 'utf8');

// 1. Language Toggle
html = html.replace(
  '<button type="button" class="btn-lang-toggle" id="btnLandingLangToggle">',
  '<button type="button" class="btn-lang-toggle" id="btnLandingLangToggle" onclick="window.toggleGlobalLanguage()">'
);

// 2. Login Form
html = html.replace(
  '<form id="dedicatedLoginForm" novalidate>',
  '<form id="dedicatedLoginForm" novalidate onsubmit="window.handleDedicatedLoginSubmit(event)">'
);

// 3. Register Form
html = html.replace(
  '<form id="dedicatedRegisterForm" novalidate>',
  '<form id="dedicatedRegisterForm" novalidate onsubmit="window.handleDedicatedRegisterSubmit(event)">'
);

// 4. Sign Out button
html = html.replace(
  '<button type="button" class="btn-home-signout" id="btnSituationHomeSignOut" data-i18n="signOut">',
  '<button type="button" class="btn-home-signout" id="btnSituationHomeSignOut" data-i18n="signOut" onclick="window.signOutUser()">'
);

fs.writeFileSync('frontend/index.html', html, 'utf8');
console.log('SUCCESS: HTML handlers attached directly in index.html');
