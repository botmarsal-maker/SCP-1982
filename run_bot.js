const { spawn } = require('child_process');

const botProcess = spawn('python3', ['bot.py'], {
  cwd: './telegram_bot',
  env: { ...process.env, BOT_TOKEN: '1234:dummy', OWNER_ID: '123' },
});

botProcess.stdout.on('data', (data) => {
  console.log(`STDOUT: ${data}`);
});

botProcess.stderr.on('data', (data) => {
  console.log(`STDERR: ${data}`);
});

setTimeout(() => {
  botProcess.kill();
}, 5000);
