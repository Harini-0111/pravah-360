const fs = require('fs');
const path = require('path');

const timestamp = new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14);
const backupDir = path.join('backups', `recovery_checkpoint_${timestamp}`);
fs.mkdirSync(backupDir, { recursive: true });

function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach((childItemName) => {
      copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

['frontend', 'backend'].forEach(folder => {
  if (fs.existsSync(folder)) {
    copyRecursiveSync(folder, path.join(backupDir, folder));
  }
});

if (fs.existsSync('data/users.db')) {
  fs.copyFileSync('data/users.db', path.join(backupDir, 'users.db'));
}

console.log(`CURRENT_CHECKPOINT_CREATED: ${backupDir}`);
