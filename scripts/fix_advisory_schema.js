const fs = require('fs');
const SCHEMA_PATH = 'C:/major project/backend/app/schemas/operations.py';
let content = fs.readFileSync(SCHEMA_PATH, 'utf8');

// Fix C-4: Add max_length to advisory message field
const OLD_MSG = '    message: str = Field(..., description="Plain-language safety instructions")';
const NEW_MSG = '    message: str = Field(..., max_length=2000, description="Plain-language safety instructions (max 2000 chars)")';
if (content.includes(OLD_MSG)) {
  content = content.replace(OLD_MSG, NEW_MSG);
  console.log('✓ C-4: Advisory message max_length=2000 added');
} else {
  console.log('⚠ Advisory message field not found as expected');
  // Try without quotes
  const idx = content.indexOf("message: str = Field(..., description=");
  if (idx !== -1) {
    const lineEnd = content.indexOf('\n', idx);
    const oldLine = content.slice(idx, lineEnd);
    const newLine = oldLine.replace('description=', 'max_length=2000, description=');
    content = content.slice(0, idx) + newLine + content.slice(lineEnd);
    console.log('✓ C-4 applied via search');
  }
}

// Also add max_length to headline
const OLD_HEADLINE = '    headline: str = Field(..., description="Advisory headline")';
const NEW_HEADLINE = '    headline: str = Field(..., max_length=200, description="Advisory headline (max 200 chars)")';
if (content.includes(OLD_HEADLINE)) {
  content = content.replace(OLD_HEADLINE, NEW_HEADLINE);
  console.log('✓ Headline max_length=200 added');
}

fs.writeFileSync(SCHEMA_PATH, content, 'utf8');
console.log('Schema updated.');
