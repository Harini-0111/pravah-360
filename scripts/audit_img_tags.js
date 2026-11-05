const fs = require('fs');
const html = fs.readFileSync('C:/major project/frontend/index.html', 'utf8');
const rx = /<img[^>]+src=['"]([^'"]+)['"]/g;
let m;
const list = [];
while ((m = rx.exec(html)) !== null) {
  list.push(m[1]);
}
console.log("Total <img> tags:", list.length);
list.forEach((s, i) => console.log(i + 1, s));

// Also check CSS background-images in entry_journey.css and styles.css
for (let file of ['frontend/entry_journey.css', 'frontend/styles.css']) {
  const css = fs.readFileSync('C:/major project/' + file, 'utf8');
  const rxCss = /url\(['"]?([^'")]+)['"]?\)/g;
  let cm;
  console.log("\nBackground images in " + file + ":");
  while ((cm = rxCss.exec(css)) !== null) {
    if (!cm[1].includes('data:') && !cm[1].includes('fonts.')) {
      console.log("  ", cm[1]);
    }
  }
}
