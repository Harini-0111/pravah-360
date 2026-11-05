const {spawnSync} = require('child_process');
const result = spawnSync(
  'C:\\major project\\.venv\\Scripts\\python.exe',
  ['-m', 'pytest', 'tests/', '-v', '--tb=short', '-q'],
  { cwd: 'C:\\major project', encoding: 'utf8', timeout: 120000 }
);
console.log('STDOUT:', result.stdout.slice(-3000));
console.log('STDERR:', result.stderr.slice(-1000));
console.log('Exit code:', result.status);
