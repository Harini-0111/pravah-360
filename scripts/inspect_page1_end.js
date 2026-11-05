const fs = require('fs');
const html = fs.readFileSync('C:/major project/frontend/index.html', 'utf8');
const p1End = html.indexOf('</main>');
console.log("End of page-welcome at char:", p1End);
console.log("Snippet before end of page-welcome:\n", html.slice(p1End - 800, p1End + 100));

// Let's also see what comes after </main>
console.log("Snippet after page-welcome:\n", html.slice(p1End + 7, p1End + 1000));
