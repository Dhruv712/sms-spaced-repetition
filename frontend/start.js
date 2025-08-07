const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 8080;
const buildPath = path.join(__dirname, 'build');

console.log('PORT is:', port);
console.log('Build directory exists:', fs.existsSync(buildPath));

if (fs.existsSync(buildPath)) {
  console.log('Starting production server...');
  const serve = spawn('npx', ['serve', '-s', 'build', '-l', port.toString()], {
    stdio: 'inherit',
    cwd: __dirname
  });
  
  serve.on('error', (err) => {
    console.error('Failed to start serve:', err);
    process.exit(1);
  });
} else {
  console.log('Build directory not found, starting development server...');
  const dev = spawn('npm', ['run', 'start'], {
    stdio: 'inherit',
    cwd: __dirname
  });
  
  dev.on('error', (err) => {
    console.error('Failed to start dev server:', err);
    process.exit(1);
  });
} 