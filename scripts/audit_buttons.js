const fs = require('fs');
const c = fs.readFileSync('C:/major project/frontend/index.html', 'utf8');
const buttons = [];
// Match all button elements (simplified)
const rx = /<button([^>]*)>([\s\S]*?)<\/button>/g;
let m;
while ((m = rx.exec(c)) !== null) {
  const attrs = m[1];
  const inner = m[2].replace(/<[^>]+>/g, '').trim().slice(0, 50);
  const idMatch = attrs.match(/id="([^"]+)"/);
  const onclickMatch = attrs.match(/onclick="([^"]+)"/);
  const typeMatch = attrs.match(/type="([^"]+)"/);
  const classMatch = attrs.match(/class="([^"]+)"/);
  buttons.push({
    text: inner,
    id: idMatch ? idMatch[1] : '',
    type: typeMatch ? typeMatch[1] : 'button',
    hasOnclick: !!onclickMatch,
    onclick: onclickMatch ? onclickMatch[1].slice(0, 60) : '',
    class: classMatch ? classMatch[1].slice(0, 40) : ''
  });
}
console.log('Total buttons:', buttons.length);
buttons.forEach((b, i) => {
  console.log(i + 1, '|', b.type, '|', b.id || '-', '|', b.text, '|', b.hasOnclick ? b.onclick : 'no-onclick');
});
