const fs = require('fs');
const APP_PATH = 'C:/major project/frontend/app.js';
let content = fs.readFileSync(APP_PATH, 'utf8');

// Fix: btnSubmitSosForm is the HTML button, but app.js looks for btnSubmitHelpRequest
// Find the form submission handler that uses btnSubmitHelpRequest
const OLD_SUBMIT_ID = "const btn = document.getElementById('btnSubmitHelpRequest');";
const NEW_SUBMIT_ID = "const btn = document.getElementById('btnSubmitSosForm') || document.getElementById('btnSubmitHelpRequest');";

if (content.includes(OLD_SUBMIT_ID)) {
  content = content.replace(OLD_SUBMIT_ID, NEW_SUBMIT_ID);
  console.log('✓ SOS form button ID aligned');
} else {
  console.log('⚠ btnSubmitHelpRequest not found as standalone - checking for sosBeacon inline handler');
}

// Also check feedback element
const OLD_FEEDBACK_ID = "document.getElementById('helpSubmissionFeedback')";
const NEW_FEEDBACK_ID = "document.getElementById('sosFormFeedback') || document.getElementById('helpSubmissionFeedback')";
if (content.includes(OLD_FEEDBACK_ID)) {
  content = content.replace(OLD_FEEDBACK_ID, NEW_FEEDBACK_ID);
  console.log('✓ SOS feedback element aligned');
}

fs.writeFileSync(APP_PATH, content, 'utf8');
console.log('Done.');
